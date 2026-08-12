"""
====================================================================
WRO FUTURE ENGINEERS 2026
THE DOON SCHOOL

RASPBERRY PI VISION + ESP32 CONTROL
Version: 1.0

SYSTEM
------
Raspberry Pi 4B
    |
    +-- Pi Camera 3 Wide
    |
    +-- OpenCV vision
    |
    +-- PD steering
    |
    +-- USB serial
            |
            v
        ESP32
            |
            +-- MG996R steering servo
            |
            +-- TB6612FNG
                    |
                    +-- N20 6V 600RPM drive motor

CURRENT PHASE
-------------
This version integrates the existing computer-vision system with
the ESP32 low-level controller.

Implemented:
    - Camera handling
    - 3x3 colour grid
    - Red / Green / Blue / Purple / Orange detection
    - Black detection
    - Object contour detection
    - Target selection
    - Centering error
    - PD steering
    - Dynamic drive speed
    - USB serial ESP32 communication
    - Serial communication fail-safe

NOT YET IMPLEMENTED
-------------------
    - WRO orange/blue line following
    - IMU sensor fusion
    - VL ToF integration
    - Lap counting
    - Full red/green pillar strategy
    - Parallel parking

These will be added after the basic Pi -> ESP32 control loop is
physically verified.
====================================================================
"""

# ============================================================
# IMPORTS
# ============================================================

import sys
import time

import cv2
import numpy as np
import serial
import serial.tools.list_ports


# ============================================================
# CAMERA
# ============================================================

CAMERA_INDEX = 0

CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

CAMERA_FPS_REQUEST = 60

# None = automatically select an appropriate backend.
#
# Linux:
#     V4L2
#
# Windows:
#     DirectShow
#
# macOS:
#     AVFoundation
#
CAMERA_BACKEND_OVERRIDE = None

CAMERA_OPEN_RETRIES = 3
CAMERA_OPEN_RETRY_DELAY_S = 0.5


# ============================================================
# ESP32 USB SERIAL
# ============================================================

SERIAL_BAUD = 115200

# Set this manually if automatic detection selects the wrong
# serial device.
#
# Example on Raspberry Pi:
#
#     SERIAL_PORT_OVERRIDE = "/dev/ttyUSB0"
#
# or:
#
#     SERIAL_PORT_OVERRIDE = "/dev/ttyACM0"
#
SERIAL_PORT_OVERRIDE = None

SERIAL_CONNECT_RETRIES = 5
SERIAL_CONNECT_DELAY_S = 1.0

# The camera may run at ~60 FPS, but we do not need to send
# motor commands at that rate.
ESP32_COMMAND_HZ = 25.0
ESP32_COMMAND_PERIOD = 1.0 / ESP32_COMMAND_HZ


# ============================================================
# GRID
# ============================================================

# Vertical:
#
# TOP       = 40%
# MIDDLE    = 20%
# BOTTOM    = 40%
#
# Horizontal:
#
# LEFT      = 30%
# CENTER    = 40%
# RIGHT     = 30%

TOP_RATIO = 0.40
MIDDLE_RATIO = 0.20
BOTTOM_RATIO = 0.40

LEFT_RATIO = 0.30
CENTER_RATIO = 0.40
RIGHT_RATIO = 0.30

GRID_LINE_THICKNESS = 4


# ============================================================
# IMAGE PROCESSING
# ============================================================

GAUSSIAN_KERNEL = 5
GAUSSIAN_SIGMA = 0

MORPH_KERNEL_SIZE = 5

# Minimum contour area to accept.
MIN_AREA = 100


# ============================================================
# CENTERING
# ============================================================

CENTER_DEADZONE = 0.05


# ============================================================
# DEVELOPMENT DISTANCE ESTIMATION
# ============================================================

# Temporary monocular distance estimate.
#
# This remains part of the development vision system.
#
# The VL ToF sensor will later become part of the actual distance
# estimation / sensor-fusion system.

KNOWN_OBJECT_HEIGHT_CM = 20.0
FOCAL_LENGTH_PX = 700.0


# ============================================================
# PD STEERING
# ============================================================

# Starting values only.
#
# These are NOT final calibrated values.
# Tune on the physical robot.

KP = 32.0
KD = 10.0

STEERING_MIN_DEG = -45.0
STEERING_MAX_DEG = 45.0

# Maximum derivative contribution before limiting.
MAX_DERIVATIVE = 3.0

_previous_error = 0.0
_previous_error_time = None


# ============================================================
# DRIVE SPEED
# ============================================================

# Initial development values.
#
# PWM:
#     0   = stopped
#     255 = maximum commanded PWM

BASE_SPEED = 165

MIN_SPEED = 80
MAX_SPEED = 220

# Reduce speed when steering demand becomes large.
CORNER_SPEED_REDUCTION = 70


# ============================================================
# COLOR CENTERS
#
# OpenCV HSV:
#
# H = 0..179
# S = 0..255
# V = 0..255
# ============================================================

COLOR_CENTERS = {
    "red": {
        "h": 0,
        "s": 210,
        "v": 180,
    },

    "green": {
        "h": 60,
        "s": 190,
        "v": 150,
    },

    "blue": {
        "h": 110,
        "s": 200,
        "v": 160,
    },

    "purple": {
        "h": 145,
        "s": 180,
        "v": 150,
    },

    "orange": {
        "h": 15,
        "s": 220,
        "v": 180,
    },
}


# ============================================================
# COLOR GRID
# ============================================================

GRID_COLORS = {
    "top_left": [
        "red",
        "green",
    ],

    "top_center": [
        "red",
        "green",
    ],

    "top_right": [
        "red",
        "green",
    ],

    "middle_left": [
        "red",
        "green",
        "purple",
    ],

    "middle_center": [
        "red",
        "green",
        "purple",
    ],

    "middle_right": [
        "red",
        "green",
        "purple",
    ],

    "bottom_left": [
        "orange",
        "blue",
    ],

    "bottom_center": [
        "orange",
        "blue",
    ],

    "bottom_right": [
        "orange",
        "blue",
    ],
}


# ============================================================
# BLACK GRID
# ============================================================

BLACK_GRID = {
    "top_left": True,
    "top_center": True,
    "top_right": True,

    "middle_left": True,
    "middle_center": False,
    "middle_right": True,

    "bottom_left": True,
    "bottom_center": False,
    "bottom_right": True,
}


# ============================================================
# SERIAL COMMUNICATION CLASS
# ============================================================

class ESP32Controller:
    """
    USB serial interface between Raspberry Pi and ESP32.

    Protocol:

        CMD,<steering_deg>,<motor_pwm>,<mode>

    Example:

        CMD,-12.50,180,DRIVE

    Additional commands:

        STOP
        PING

    ESP32 responses include:

        ACK,CMD
        ACK,STOP
        PONG
        STATUS,...
        ERR,...
    """

    def __init__(
        self,
        port=None,
        baudrate=115200,
    ):
        self.port_override = port
        self.baudrate = baudrate

        self.serial = None
        self.connected = False

        self.last_send_time = 0.0

        self.last_response = ""

    # --------------------------------------------------------
    # FIND USB SERIAL DEVICE
    # --------------------------------------------------------

    def find_port(self):
        """
        Automatically find a likely ESP32 USB serial port.
        """

        if self.port_override:
            return self.port_override

        ports = list(
            serial.tools.list_ports.comports()
        )

        if not ports:
            return None

        candidates = []

        for port in ports:

            score = 0

            device = (
                port.device or ""
            ).lower()

            description = (
                port.description or ""
            ).lower()

            manufacturer = (
                port.manufacturer or ""
            ).lower()

            # Generic USB serial device
            if "usb" in device:
                score += 2

            if "usb" in description:
                score += 2

            # Common ESP32 USB-to-UART bridges
            if "cp210" in description:
                score += 3

            if "cp210" in manufacturer:
                score += 3

            if "ch340" in description:
                score += 3

            if "ch340" in manufacturer:
                score += 3

            # Some boards expose ESP32 explicitly.
            if "esp32" in description:
                score += 5

            if "esp32" in manufacturer:
                score += 5

            candidates.append(
                (
                    score,
                    port.device,
                )
            )

        candidates.sort(
            reverse=True
        )

        return candidates[0][1]

    # --------------------------------------------------------
    # CONNECT
    # --------------------------------------------------------

    def connect(self):

        for attempt in range(
            1,
            SERIAL_CONNECT_RETRIES + 1,
        ):

            port = self.find_port()

            if port is None:

                print(
                    "WARNING: ESP32 USB serial device "
                    f"not found "
                    f"(attempt {attempt}/"
                    f"{SERIAL_CONNECT_RETRIES})"
                )

                time.sleep(
                    SERIAL_CONNECT_DELAY_S
                )

                continue

            try:

                print(
                    f"Attempting ESP32 connection "
                    f"on {port}..."
                )

                self.serial = serial.Serial(
                    port=port,
                    baudrate=self.baudrate,
                    timeout=0.02,
                    write_timeout=0.05,
                )

                # Some ESP32 boards reset when the
                # USB serial connection is opened.
                time.sleep(2.0)

                self.serial.reset_input_buffer()
                self.serial.reset_output_buffer()

                self.connected = True

                print(
                    f"ESP32 connected on {port}"
                )

                return True

            except (
                serial.SerialException,
                OSError,
            ) as exc:

                print(
                    f"WARNING: failed to connect "
                    f"to {port}: {exc}"
                )

                self.serial = None
                self.connected = False

                time.sleep(
                    SERIAL_CONNECT_DELAY_S
                )

        return False

    # --------------------------------------------------------
    # SEND DRIVE COMMAND
    # --------------------------------------------------------

    def send(
        self,
        steering_deg,
        motor_pwm,
        mode="DRIVE",
        force=False,
    ):
        """
        Send a motor/steering command.

        steering_deg:
            -45 .. +45

        motor_pwm:
            -255 .. +255

        mode:
            DRIVE / PARK / STOP / FINISH
        """

        if (
            not self.connected
            or self.serial is None
        ):
            return False

        now = time.perf_counter()

        # Rate limit command transmission.
        if (
            not force
            and (
                now - self.last_send_time
                < ESP32_COMMAND_PERIOD
            )
        ):
            self.poll()

            return True

        steering_deg = max(
            STEERING_MIN_DEG,
            min(
                STEERING_MAX_DEG,
                float(steering_deg),
            ),
        )

        motor_pwm = int(
            max(
                -255,
                min(
                    255,
                    int(motor_pwm),
                ),
            )
        )

        mode = str(mode).upper()

        packet = (
            f"CMD,"
            f"{steering_deg:.2f},"
            f"{motor_pwm},"
            f"{mode}\n"
        )

        try:

            self.serial.write(
                packet.encode("ascii")
            )

            self.serial.flush()

            self.last_send_time = now

            self.poll()

            return True

        except (
            serial.SerialException,
            OSError,
        ) as exc:

            print(
                f"ERROR: ESP32 write failed: {exc}"
            )

            self.connected = False

            return False

    # --------------------------------------------------------
    # STOP
    # --------------------------------------------------------

    def stop(self):

        if (
            not self.connected
            or self.serial is None
        ):
            return

        try:

            self.serial.write(
                b"STOP\n"
            )

            self.serial.flush()

            time.sleep(0.05)

            self.poll()

        except (
            serial.SerialException,
            OSError,
        ):
            pass

    # --------------------------------------------------------
    # PING
    # --------------------------------------------------------

    def ping(self):

        if (
            not self.connected
            or self.serial is None
        ):
            return False

        try:

            self.serial.write(
                b"PING\n"
            )

            self.serial.flush()

            deadline = (
                time.perf_counter()
                + 0.25
            )

            while (
                time.perf_counter()
                < deadline
            ):

                if self.serial.in_waiting:

                    data = (
                        self.serial.readline()
                    )

                    if data:

                        response = (
                            data
                            .decode(
                                "ascii",
                                errors="ignore",
                            )
                            .strip()
                        )

                        self.last_response = (
                            response
                        )

                        if response == "PONG":
                            return True

            return False

        except (
            serial.SerialException,
            OSError,
        ):

            self.connected = False

            return False

    # --------------------------------------------------------
    # READ AVAILABLE ESP32 RESPONSES
    # --------------------------------------------------------

    def poll(self):

        if (
            not self.connected
            or self.serial is None
        ):
            return

        try:

            while self.serial.in_waiting:

                data = (
                    self.serial.readline()
                )

                if not data:
                    break

                response = (
                    data
                    .decode(
                        "ascii",
                        errors="ignore",
                    )
                    .strip()
                )

                if not response:
                    continue

                self.last_response = response

                # Only print errors.
                # ACK/STATUS traffic is intentionally
                # kept quiet during normal operation.

                if response.startswith("ERR"):
                    print(
                        f"ESP32: {response}"
                    )

        except (
            serial.SerialException,
            OSError,
        ):

            self.connected = False

    # --------------------------------------------------------
    # CLOSE
    # --------------------------------------------------------

    def close(self):

        if self.serial is not None:

            try:

                self.serial.close()

            except Exception:
                pass

        self.serial = None
        self.connected = False


# ============================================================
# STARTUP VALIDATION
# ============================================================

def validate_config():

    # --------------------------------------------------------
    # Grid ratio validation
    # --------------------------------------------------------

    ratio_sum_v = (
        TOP_RATIO
        + MIDDLE_RATIO
        + BOTTOM_RATIO
    )

    ratio_sum_h = (
        LEFT_RATIO
        + CENTER_RATIO
        + RIGHT_RATIO
    )

    if not np.isclose(
        ratio_sum_v,
        1.0,
    ):

        raise ValueError(
            "Vertical grid ratios "
            f"must sum to 1.0, "
            f"got {ratio_sum_v}"
        )

    if not np.isclose(
        ratio_sum_h,
        1.0,
    ):

        raise ValueError(
            "Horizontal grid ratios "
            f"must sum to 1.0, "
            f"got {ratio_sum_h}"
        )

    # --------------------------------------------------------
    # Expected grid cells
    # --------------------------------------------------------

    expected_cells = {
        f"{row}_{column}"
        for row in (
            "top",
            "middle",
            "bottom",
        )
        for column in (
            "left",
            "center",
            "right",
        )
    }

    if (
        set(GRID_COLORS.keys())
        != expected_cells
    ):

        raise ValueError(
            "GRID_COLORS is missing "
            "or has extra grid cells"
        )

    if (
        set(BLACK_GRID.keys())
        != expected_cells
    ):

        raise ValueError(
            "BLACK_GRID is missing "
            "or has extra grid cells"
        )

    # --------------------------------------------------------
    # Colour reference validation
    # --------------------------------------------------------

    for cell, colors in (
        GRID_COLORS.items()
    ):

        for color in colors:

            if color not in COLOR_CENTERS:

                raise ValueError(
                    f"GRID_COLORS['{cell}'] "
                    f"references unknown color "
                    f"'{color}'"
                )


# ============================================================
# CAMERA
# ============================================================

def pick_default_backend():

    if (
        CAMERA_BACKEND_OVERRIDE
        is not None
    ):

        return CAMERA_BACKEND_OVERRIDE

    if sys.platform.startswith("win"):

        return cv2.CAP_DSHOW

    if sys.platform.startswith("linux"):

        return cv2.CAP_V4L2

    if sys.platform == "darwin":

        return cv2.CAP_AVFOUNDATION

    return cv2.CAP_ANY


def open_camera():

    backend = (
        pick_default_backend()
    )

    for attempt in range(
        1,
        CAMERA_OPEN_RETRIES + 1,
    ):

        cap = cv2.VideoCapture(
            CAMERA_INDEX,
            backend,
        )

        if cap.isOpened():

            cap.set(
                cv2.CAP_PROP_FRAME_WIDTH,
                CAMERA_WIDTH,
            )

            cap.set(
                cv2.CAP_PROP_FRAME_HEIGHT,
                CAMERA_HEIGHT,
            )

            cap.set(
                cv2.CAP_PROP_FPS,
                CAMERA_FPS_REQUEST,
            )

            return cap

        cap.release()

        print(
            "WARNING: camera index "
            f"{CAMERA_INDEX} failed "
            f"to open "
            f"(backend={backend}, "
            f"attempt {attempt}/"
            f"{CAMERA_OPEN_RETRIES})"
        )

        time.sleep(
            CAMERA_OPEN_RETRY_DELAY_S
        )

    # Last resort.
    cap = cv2.VideoCapture(
        CAMERA_INDEX,
        cv2.CAP_ANY,
    )

    if cap.isOpened():

        cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            CAMERA_WIDTH,
        )

        cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            CAMERA_HEIGHT,
        )

        cap.set(
            cv2.CAP_PROP_FPS,
            CAMERA_FPS_REQUEST,
        )

        return cap

    cap.release()

    return None


# ============================================================
# GRID COORDINATES
# ============================================================

def get_grid(
    width,
    height,
):

    y_top = round(
        height * TOP_RATIO
    )

    y_middle = round(
        height
        * (
            TOP_RATIO
            + MIDDLE_RATIO
        )
    )

    x_left = round(
        width * LEFT_RATIO
    )

    x_right = round(
        width
        * (
            LEFT_RATIO
            + CENTER_RATIO
        )
    )

    return (
        y_top,
        y_middle,
        x_left,
        x_right,
    )


# ============================================================
# IMAGE PROCESSING
# ============================================================

_MORPH_KERNEL = np.ones(
    (
        MORPH_KERNEL_SIZE,
        MORPH_KERNEL_SIZE,
    ),
    np.uint8,
)


def smooth(frame):

    return cv2.GaussianBlur(
        frame,
        (
            GAUSSIAN_KERNEL,
            GAUSSIAN_KERNEL,
        ),
        GAUSSIAN_SIGMA,
    )


def clean_mask(mask):

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        _MORPH_KERNEL,
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        _MORPH_KERNEL,
    )

    return mask


def create_color_mask(
    hsv,
    color,
    tolerance,
):

    center = COLOR_CENTERS[color]

    h = center["h"]
    s = center["s"]
    v = center["v"]

    hue_tol = max(
        2,
        round(
            tolerance * 0.35
        ),
    )

    sat_min = max(
        30,
        s - tolerance * 2,
    )

    val_min = max(
        25,
        v - tolerance * 2,
    )

    # Red wraps around the HSV hue boundary.
    if color == "red":

        mask1 = cv2.inRange(
            hsv,
            np.array(
                [
                    0,
                    sat_min,
                    val_min,
                ]
            ),
            np.array(
                [
                    hue_tol,
                    255,
                    255,
                ]
            ),
        )

        mask2 = cv2.inRange(
            hsv,
            np.array(
                [
                    179 - hue_tol,
                    sat_min,
                    val_min,
                ]
            ),
            np.array(
                [
                    179,
                    255,
                    255,
                ]
            ),
        )

        mask = cv2.bitwise_or(
            mask1,
            mask2,
        )

        return clean_mask(
            mask
        )

    lower = np.array(
        [
            max(
                0,
                h - hue_tol,
            ),
            sat_min,
            val_min,
        ]
    )

    upper = np.array(
        [
            min(
                179,
                h + hue_tol,
            ),
            255,
            255,
        ]
    )

    mask = cv2.inRange(
        hsv,
        lower,
        upper,
    )

    return clean_mask(
        mask
    )


def create_black_mask(
    hsv,
    tolerance,
):

    value_limit = int(
        45
        + tolerance * 1.5
    )

    value_limit = max(
        35,
        min(
            125,
            value_limit,
        ),
    )

    mask = cv2.inRange(
        hsv,
        np.array(
            [
                0,
                0,
                0,
            ]
        ),
        np.array(
            [
                179,
                255,
                value_limit,
            ]
        ),
    )

    return clean_mask(
        mask
    )


# ============================================================
# FIND CONTOURS
# ============================================================

def detect_objects(
    mask,
    color,
    x_offset,
    y_offset,
):

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    detections = []

    for contour in contours:

        area = cv2.contourArea(
            contour
        )

        if area < MIN_AREA:
            continue

        x, y, w, h = (
            cv2.boundingRect(
                contour
            )
        )

        moments = cv2.moments(
            contour
        )

        if moments["m00"] != 0:

            cx = (
                moments["m10"]
                / moments["m00"]
            )

            cy = (
                moments["m01"]
                / moments["m00"]
            )

        else:

            cx = x + w / 2
            cy = y + h / 2

        global_contour = (
            contour.copy()
        )

        global_contour[
            :,
            :,
            0
        ] += x_offset

        global_contour[
            :,
            :,
            1
        ] += y_offset

        detections.append(
            {
                "color": color,
                "contour": global_contour,
                "area": area,

                "x": x + x_offset,
                "y": y + y_offset,

                "w": w,
                "h": h,

                "cx": cx + x_offset,
                "cy": cy + y_offset,
            }
        )

    return detections


# ============================================================
# DISTANCE
# ============================================================

def estimate_distance(
    pixel_height,
):

    if pixel_height <= 0:
        return None

    return (
        KNOWN_OBJECT_HEIGHT_CM
        * FOCAL_LENGTH_PX
        / pixel_height
    )


# ============================================================
# CENTERING
# ============================================================

def calculate_centering(
    cx,
    frame_width,
):

    center = (
        frame_width
        / 2.0
    )

    error_pixels = (
        cx
        - center
    )

    error_normalized = (
        error_pixels
        / center
    )

    if (
        abs(error_normalized)
        <= CENTER_DEADZONE
    ):

        direction = "CENTER"

    elif error_normalized < 0:

        direction = "LEFT"

    else:

        direction = "RIGHT"

    return (
        error_pixels,
        error_normalized,
        direction,
    )


# ============================================================
# PD CONTROLLER
# ============================================================

def reset_pd():

    global _previous_error
    global _previous_error_time

    _previous_error = 0.0
    _previous_error_time = None


def calculate_pd_steering(
    error,
    now=None,
):

    global _previous_error
    global _previous_error_time

    if now is None:

        now = time.perf_counter()

    # Apply centre deadzone.
    if (
        abs(error)
        <= CENTER_DEADZONE
    ):

        error = 0.0

    # First sample: no derivative yet.
    if (
        _previous_error_time
        is None
    ):

        derivative = 0.0

    else:

        dt = (
            now
            - _previous_error_time
        )

        if dt <= 0.0:

            derivative = 0.0

        else:

            derivative = (
                error
                - _previous_error
            ) / dt

            derivative = max(
                -MAX_DERIVATIVE,
                min(
                    MAX_DERIVATIVE,
                    derivative,
                ),
            )

    output = (
        KP * error
        + KD * derivative
    )

    output = max(
        STEERING_MIN_DEG,
        min(
            STEERING_MAX_DEG,
            output,
        ),
    )

    _previous_error = error
    _previous_error_time = now

    return output


# ============================================================
# DRIVE SPEED
# ============================================================

def calculate_drive_speed(
    steering_deg,
):

    steering_fraction = (
        abs(steering_deg)
        / 45.0
    )

    speed = (
        BASE_SPEED
        - (
            CORNER_SPEED_REDUCTION
            * steering_fraction
        )
    )

    speed = max(
        MIN_SPEED,
        min(
            MAX_SPEED,
            speed,
        ),
    )

    return int(speed)


# ============================================================
# GET GRID CELL
# ============================================================

def get_cell(
    cx,
    cy,
    width,
    height,
):

    (
        y_top,
        y_middle,
        x_left,
        x_right,
    ) = get_grid(
        width,
        height,
    )

    if cy < y_top:

        row = "top"

    elif cy < y_middle:

        row = "middle"

    else:

        row = "bottom"

    if cx < x_left:

        column = "left"

    elif cx < x_right:

        column = "center"

    else:

        column = "right"

    return (
        f"{row}_{column}"
    )


# ============================================================
# DRAWING - DETECTION
# ============================================================

def draw_detection(
    frame,
    detection,
):

    x, y, w, h = (
        int(
            detection[key]
        )
        for key in (
            "x",
            "y",
            "w",
            "h",
        )
    )

    cx = int(
        detection["cx"]
    )

    cy = int(
        detection["cy"]
    )

    cv2.rectangle(
        frame,
        (
            x,
            y,
        ),
        (
            x + w,
            y + h,
        ),
        (255, 255, 255),
        2,
    )

    cv2.circle(
        frame,
        (
            cx,
            cy,
        ),
        5,
        (255, 255, 255),
        -1,
    )

    distance = (
        estimate_distance(h)
    )

    if distance is None:

        text = (
            f"{detection['color']}"
        )

    else:

        text = (
            f"{detection['color']} "
            f"{distance:.0f}cm"
        )

    cv2.putText(
        frame,
        text,
        (
            x,
            max(
                18,
                y - 7,
            ),
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        2,
    )


# ============================================================
# DRAWING - CONTOUR OUTLINE
# ============================================================

def draw_outline(
    frame,
    detection,
):

    cv2.drawContours(
        frame,
        [
            detection["contour"]
        ],
        -1,
        (255, 255, 255),
        3,
    )

    cx = int(
        detection["cx"]
    )

    cy = int(
        detection["cy"]
    )

    cv2.circle(
        frame,
        (
            cx,
            cy,
        ),
        5,
        (255, 255, 255),
        -1,
    )


# ============================================================
# DRAWING - GRID
# ============================================================

def draw_grid(frame):

    height, width = (
        frame.shape[:2]
    )

    (
        y_top,
        y_middle,
        x_left,
        x_right,
    ) = get_grid(
        width,
        height,
    )

    grid_lines = (
        (
            (
                0,
                y_top,
            ),
            (
                width,
                y_top,
            ),
        ),

        (
            (
                0,
                y_middle,
            ),
            (
                width,
                y_middle,
            ),
        ),

        (
            (
                x_left,
                0,
            ),
            (
                x_left,
                height,
            ),
        ),

        (
            (
                x_right,
                0,
            ),
            (
                x_right,
                height,
            ),
        ),
    )

    for pt1, pt2 in grid_lines:

        cv2.line(
            frame,
            pt1,
            pt2,
            (0, 255, 255),
            GRID_LINE_THICKNESS,
            cv2.LINE_AA,
        )


# ============================================================
# DRAWING - GRID LABELS
# ============================================================

def draw_labels(frame):

    height, width = (
        frame.shape[:2]
    )

    (
        y_top,
        y_middle,
        x_left,
        x_right,
    ) = get_grid(
        width,
        height,
    )

    cv2.putText(
        frame,
        "TOP 40%",
        (
            10,
            30,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )

    cv2.putText(
        frame,
        "MIDDLE 20%",
        (
            10,
            y_top + 30,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
    )

    cv2.putText(
        frame,
        "BOTTOM 40%",
        (
            10,
            y_middle + 30,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )

    cv2.putText(
        frame,
        "LEFT 30%",
        (
            10,
            height - 15,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2,
    )

    cv2.putText(
        frame,
        "CENTER 40%",
        (
            x_left + 15,
            height - 15,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2,
    )

    cv2.putText(
        frame,
        "RIGHT 30%",
        (
            x_right + 10,
            height - 15,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Validate configuration.
    # --------------------------------------------------------

    validate_config()

    # --------------------------------------------------------
    # Open camera.
    # --------------------------------------------------------

    cap = open_camera()

    if cap is None:

        print(
            f"ERROR: Camera index "
            f"{CAMERA_INDEX} could not "
            f"be opened after "
            f"{CAMERA_OPEN_RETRIES} attempts."
        )

        return

    # --------------------------------------------------------
    # Connect ESP32.
    # --------------------------------------------------------

    esp32 = ESP32Controller(
        port=SERIAL_PORT_OVERRIDE,
        baudrate=SERIAL_BAUD,
    )

    esp32_connected = (
        esp32.connect()
    )

    if esp32_connected:

        print(
            "Testing ESP32 communication..."
        )

        if esp32.ping():

            print(
                "ESP32 PING successful."
            )

        else:

            print(
                "WARNING: ESP32 PING failed."
            )

    else:

        print(
            "WARNING: ESP32 is not connected."
        )

        print(
            "Vision will continue in "
            "development mode."
        )

    # --------------------------------------------------------
    # Debug windows.
    # --------------------------------------------------------

    cv2.namedWindow(
        "WRO Vision",
        cv2.WINDOW_NORMAL,
    )

    cv2.namedWindow(
        "Mask",
        cv2.WINDOW_NORMAL,
    )

    cv2.namedWindow(
        "Outline",
        cv2.WINDOW_NORMAL,
    )

    # --------------------------------------------------------
    # HSV tolerance control.
    # --------------------------------------------------------

    cv2.createTrackbar(
        "Tolerance",
        "WRO Vision",
        25,
        80,
        lambda x: None,
    )

    # --------------------------------------------------------
    # FPS timing.
    # --------------------------------------------------------

    previous_time = (
        time.perf_counter()
    )

    # --------------------------------------------------------
    # MAIN LOOP.
    # --------------------------------------------------------

    try:

        while True:

            # ------------------------------------------------
            # Capture frame.
            # ------------------------------------------------

            ret, frame = (
                cap.read()
            )

            if not ret:

                print(
                    "ERROR: Could not "
                    "read camera frame."
                )

                break

            # ------------------------------------------------
            # Frame dimensions.
            # ------------------------------------------------

            height, width = (
                frame.shape[:2]
            )

            # ------------------------------------------------
            # Tolerance.
            # ------------------------------------------------

            tolerance = (
                cv2.getTrackbarPos(
                    "Tolerance",
                    "WRO Vision",
                )
            )

            # ------------------------------------------------
            # Grid.
            # ------------------------------------------------

            (
                y_top,
                y_middle,
                x_left,
                x_right,
            ) = get_grid(
                width,
                height,
            )

            # ------------------------------------------------
            # Pre-process frame.
            # ------------------------------------------------

            blurred = smooth(
                frame
            )

            hsv = cv2.cvtColor(
                blurred,
                cv2.COLOR_BGR2HSV,
            )

            # ------------------------------------------------
            # Full-frame debug mask.
            # ------------------------------------------------

            full_mask = np.zeros(
                (
                    height,
                    width,
                ),
                dtype=np.uint8,
            )

            detections = []

            # ------------------------------------------------
            # Grid rows.
            # ------------------------------------------------

            rows = (
                (
                    "top",
                    0,
                    y_top,
                ),

                (
                    "middle",
                    y_top,
                    y_middle,
                ),

                (
                    "bottom",
                    y_middle,
                    height,
                ),
            )

            # ------------------------------------------------
            # Grid columns.
            # ------------------------------------------------

            columns = (
                (
                    "left",
                    0,
                    x_left,
                ),

                (
                    "center",
                    x_left,
                    x_right,
                ),

                (
                    "right",
                    x_right,
                    width,
                ),
            )

            # ------------------------------------------------
            # Process every grid cell.
            # ------------------------------------------------

            for (
                row_name,
                y1,
                y2,
            ) in rows:

                for (
                    column_name,
                    x1,
                    x2,
                ) in columns:

                    cell = (
                        f"{row_name}_"
                        f"{column_name}"
                    )

                    roi_hsv = (
                        hsv[
                            y1:y2,
                            x1:x2
                        ]
                    )

                    cell_mask = np.zeros(
                        (
                            y2 - y1,
                            x2 - x1,
                        ),
                        dtype=np.uint8,
                    )

                    # ----------------------------------------
                    # Expected colours for this cell.
                    # ----------------------------------------

                    for color in (
                        GRID_COLORS[cell]
                    ):

                        mask = (
                            create_color_mask(
                                roi_hsv,
                                color,
                                tolerance,
                            )
                        )

                        cell_mask = (
                            cv2.bitwise_or(
                                cell_mask,
                                mask,
                            )
                        )

                        detections.extend(
                            detect_objects(
                                mask,
                                color,
                                x1,
                                y1,
                            )
                        )

                    # ----------------------------------------
                    # Black mask where allowed.
                    # ----------------------------------------

                    if BLACK_GRID[cell]:

                        mask = (
                            create_black_mask(
                                roi_hsv,
                                tolerance,
                            )
                        )

                        cell_mask = (
                            cv2.bitwise_or(
                                cell_mask,
                                mask,
                            )
                        )

                        detections.extend(
                            detect_objects(
                                mask,
                                "BLACK",
                                x1,
                                y1,
                            )
                        )

                    # ----------------------------------------
                    # Store mask.
                    # ----------------------------------------

                    full_mask[
                        y1:y2,
                        x1:x2
                    ] = cell_mask

            # ------------------------------------------------
            # Draw all detections.
            # ------------------------------------------------

            for detection in detections:

                draw_detection(
                    frame,
                    detection,
                )

            # ------------------------------------------------
            # Current development target selection.
            #
            # NOTE:
            # This is intentionally the same basic target
            # selection strategy as the existing development
            # version.
            #
            # It will later be replaced with explicit WRO
            # line/pillar strategy.
            # ------------------------------------------------

            pillars = [
                detection
                for detection in detections
                if detection["color"] != "BLACK"
            ]

            target = None

            if pillars:

                target = max(
                    pillars,
                    key=lambda d:
                        (
                            d["area"]
                            * 0.65
                            +
                            d["cy"]
                            * 0.35
                        ),
                )

            # ------------------------------------------------
            # Navigation variables.
            # ------------------------------------------------

            direction = "SEARCH"

            steering_deg = 0.0

            center_error = 0.0

            distance = None

            target_cell = "NONE"

            motor_pwm = 0

            mode = "STOP"

            # ------------------------------------------------
            # Target found.
            # ------------------------------------------------

            if target is not None:

                (
                    _,
                    center_error,
                    direction,
                ) = calculate_centering(
                    target["cx"],
                    width,
                )

                # --------------------------------------------
                # PD steering.
                # --------------------------------------------

                steering_deg = (
                    calculate_pd_steering(
                        center_error
                    )
                )

                # --------------------------------------------
                # Distance estimate.
                # --------------------------------------------

                distance = (
                    estimate_distance(
                        target["h"]
                    )
                )

                # --------------------------------------------
                # Grid cell.
                # --------------------------------------------

                target_cell = (
                    get_cell(
                        target["cx"],
                        target["cy"],
                        width,
                        height,
                    )
                )

                # --------------------------------------------
                # Motor speed.
                # --------------------------------------------

                motor_pwm = (
                    calculate_drive_speed(
                        steering_deg
                    )
                )

                mode = "DRIVE"

            else:

                # No target -> don't continue driving blindly.
                reset_pd()

                steering_deg = 0.0

                motor_pwm = 0

                mode = "STOP"

            # ------------------------------------------------
            # Send command to ESP32.
            # ------------------------------------------------

            if esp32.connected:

                esp32.send(
                    steering_deg=(
                        steering_deg
                    ),
                    motor_pwm=(
                        motor_pwm
                    ),
                    mode=mode,
                )

            # ------------------------------------------------
            # Create outline debug image.
            # ------------------------------------------------

            outline = (
                frame.copy()
            )

            for detection in detections:

                draw_outline(
                    outline,
                    detection,
                )

            # ------------------------------------------------
            # Highlight target.
            # ------------------------------------------------

            if target is not None:

                cx = int(
                    target["cx"]
                )

                cy = int(
                    target["cy"]
                )

                # Target centre.
                cv2.circle(
                    outline,
                    (
                        cx,
                        cy,
                    ),
                    15,
                    (0, 255, 255),
                    3,
                )

                # Error line from image centre.
                cv2.line(
                    outline,
                    (
                        width // 2,
                        cy,
                    ),
                    (
                        cx,
                        cy,
                    ),
                    (0, 255, 255),
                    2,
                )

            # ------------------------------------------------
            # Draw grid.
            # ------------------------------------------------

            draw_grid(
                frame
            )

            draw_grid(
                outline
            )

            draw_labels(
                frame
            )

            # ------------------------------------------------
            # Labels.
            # ------------------------------------------------

            if target is not None:

                target_label = (
                    "TARGET: "
                    f"{target['color'].upper()}"
                )

            else:

                target_label = (
                    "TARGET: NONE"
                )

            if distance is not None:

                distance_label = (
                    f"DISTANCE: "
                    f"{distance:.1f} cm"
                )

            else:

                distance_label = (
                    "DISTANCE: --"
                )

            # ------------------------------------------------
            # ESP32 status.
            # ------------------------------------------------

            if esp32.connected:

                esp32_label = (
                    "ESP32: CONNECTED"
                )

            else:

                esp32_label = (
                    "ESP32: DISCONNECTED"
                )

            # ------------------------------------------------
            # Debug panel.
            # ------------------------------------------------

            panel = [
                target_label,

                f"CELL: "
                f"{target_cell}",

                f"ERROR: "
                f"{center_error:+.3f}",

                f"DIRECTION: "
                f"{direction}",

                f"STEERING: "
                f"{steering_deg:+.1f} deg",

                f"MOTOR: "
                f"{motor_pwm}",

                distance_label,

                f"TOLERANCE: "
                f"{tolerance}",

                esp32_label,
            ]

            # ------------------------------------------------
            # Panel background.
            # ------------------------------------------------

            cv2.rectangle(
                frame,
                (
                    10,
                    50,
                ),
                (
                    360,
                    50
                    + len(panel)
                    * 25
                    + 15,
                ),
                (0, 0, 0),
                -1,
            )

            # ------------------------------------------------
            # Panel text.
            # ------------------------------------------------

            for i, text in enumerate(
                panel
            ):

                cv2.putText(
                    frame,
                    text,
                    (
                        20,
                        75
                        + i * 25,
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    2,
                )

            # ------------------------------------------------
            # FPS.
            # ------------------------------------------------

            now = (
                time.perf_counter()
            )

            dt = (
                now
                - previous_time
            )

            previous_time = now

            fps = (
                1.0 / dt
                if dt > 0
                else 0.0
            )

            cv2.putText(
                frame,
                f"FPS: {fps:.1f}",
                (
                    width - 140,
                    30,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )

            # ------------------------------------------------
            # Outline title.
            # ------------------------------------------------

            cv2.putText(
                outline,
                "ACTUAL CONTOURS",
                (
                    10,
                    30,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            # ------------------------------------------------
            # Mask display.
            # ------------------------------------------------

            mask_display = (
                cv2.cvtColor(
                    full_mask,
                    cv2.COLOR_GRAY2BGR,
                )
            )

            draw_grid(
                mask_display
            )

            cv2.putText(
                mask_display,
                "LEGAL MASK",
                (
                    10,
                    30,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            # ------------------------------------------------
            # Show windows.
            # ------------------------------------------------

            cv2.imshow(
                "WRO Vision",
                frame,
            )

            cv2.imshow(
                "Mask",
                mask_display,
            )

            cv2.imshow(
                "Outline",
                outline,
            )

            # ------------------------------------------------
            # Keyboard input.
            # ------------------------------------------------

            key = (
                cv2.waitKey(1)
                & 0xFF
            )

            # ESC.
            if key == 27:

                break

            # ------------------------------------------------
            # Manual emergency stop from keyboard.
            # ------------------------------------------------

            if key == ord(" "):

                if esp32.connected:

                    esp32.send(
                        steering_deg=0.0,
                        motor_pwm=0,
                        mode="STOP",
                        force=True,
                    )

                reset_pd()

    finally:

        # ----------------------------------------------------
        # ALWAYS STOP ROBOT FIRST.
        # ----------------------------------------------------

        try:

            if esp32.connected:

                print(
                    "Sending STOP "
                    "to ESP32..."
                )

                esp32.stop()

        finally:

            esp32.close()

            cap.release()

            cv2.destroyAllWindows()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
