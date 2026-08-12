"""
====================================================================
WRO FUTURE ENGINEERS 2026
THE DOON SCHOOL

RASPBERRY PI AUTONOMOUS CONTROLLER
Version 2.0

HARDWARE
--------
Raspberry Pi 4B
Pi Camera 3 Wide
6-axis IMU
VL ToF distance sensor
USB-connected ESP32

ESP32 HARDWARE
--------------
MG996R steering servo
TB6612FNG
1x N20 6V 600RPM drive motor

WRO STRATEGY
------------
RED PILLAR   -> PASS RIGHT
GREEN PILLAR -> PASS LEFT

VISION
------
3x3 structured colour grid
Red / Green / Purple / Orange / Blue / Black

TRACK
-----
Orange and blue track lines are detected independently from
the pillar system.

CONTROL
-------
PD steering controller

COMMUNICATION
-------------
Raspberry Pi -> USB Serial -> ESP32

NOT CLAIMED FINAL
-----------------
Exact IMU driver and VL ToF driver are deliberately isolated until
the exact sensor boards/modules and bus configuration are confirmed.

====================================================================
"""

# ============================================================
# IMPORTS
# ============================================================

import sys
import time
import math

import cv2
import numpy as np

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    serial = None


# ============================================================
# CAMERA
# ============================================================

CAMERA_INDEX = 0

CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS_REQUEST = 60

CAMERA_BACKEND_OVERRIDE = None

CAMERA_OPEN_RETRIES = 3
CAMERA_OPEN_RETRY_DELAY_S = 0.5


# ============================================================
# ESP32 USB SERIAL
# ============================================================

SERIAL_BAUD = 115200

SERIAL_PORT_OVERRIDE = None

SERIAL_CONNECT_RETRIES = 5
SERIAL_CONNECT_DELAY_S = 1.0

ESP32_COMMAND_HZ = 25.0
ESP32_COMMAND_PERIOD = (
    1.0 / ESP32_COMMAND_HZ
)


# ============================================================
# IMAGE GRID
# ============================================================

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

MIN_AREA = 100


# ============================================================
# VISION DEADZONE
# ============================================================

CENTER_DEADZONE = 0.05


# ============================================================
# DISTANCE ESTIMATION
# ============================================================
#
# Temporary monocular estimate.
#
# VL ToF integration is deliberately isolated until its exact
# sensor module/interface is confirmed.
# ============================================================

KNOWN_OBJECT_HEIGHT_CM = 20.0
FOCAL_LENGTH_PX = 700.0


# ============================================================
# PD CONTROLLER
# ============================================================

KP = 32.0
KD = 10.0

STEERING_MIN_DEG = -45.0
STEERING_MAX_DEG = 45.0

MAX_DERIVATIVE = 3.0

previous_error = 0.0
previous_error_time = None


# ============================================================
# SPEED
# ============================================================

BASE_SPEED = 165

MIN_SPEED = 75
MAX_SPEED = 210

STEERING_SPEED_REDUCTION = 80


# ============================================================
# PILLAR STRATEGY
# ============================================================

# WRO:
#
# RED   -> pass RIGHT
# GREEN -> pass LEFT

PILLAR_BIAS_DEG = 12.0

PILLAR_CLOSE_DISTANCE_CM = 45.0

PILLAR_MIN_AREA = 250


# ============================================================
# TRACK LINE STRATEGY
# ============================================================

LINE_MIN_AREA = 80

# The bottom part of the image is most useful for immediate
# lane-position estimation.
LINE_ROI_TOP = 0.55

ORANGE_LINE_WEIGHT = 1.0
BLUE_LINE_WEIGHT = 1.0


# ============================================================
# COLOUR CENTERS
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
# 3x3 GRID COLOUR RULES
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
# BLACK GRID RULES
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
# NAVIGATION STATE
# ============================================================

class NavigationMode:
    SEARCH = "SEARCH"
    TRACK = "TRACK"
    RED_PILLAR = "RED_PILLAR"
    GREEN_PILLAR = "GREEN_PILLAR"
    PARK = "PARK"
    FINISH = "FINISH"
    STOP = "STOP"


current_navigation_mode = (
    NavigationMode.SEARCH
)


# ============================================================
# LAP STATE
# ============================================================

lap_count = 0

# These are structural placeholders until the start-line/section
# sensor geometry is calibrated on the actual field.
start_zone_detected = False
previous_start_zone = False

# Prevent multiple counts from one visual detection.
last_lap_event_time = 0.0

LAP_EVENT_COOLDOWN_S = 3.0

TARGET_LAPS = 3


# ============================================================
# SERIAL CONTROLLER
# ============================================================

class ESP32Controller:

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
    # Find serial port
    # --------------------------------------------------------

    def find_port(self):

        if self.port_override:
            return self.port_override

        if serial is None:
            return None

        ports = list(
            serial.tools.list_ports.comports()
        )

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

            if "usb" in device:
                score += 2

            if "usb" in description:
                score += 2

            if "cp210" in description:
                score += 3

            if "cp210" in manufacturer:
                score += 3

            if "ch340" in description:
                score += 3

            if "ch340" in manufacturer:
                score += 3

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

        if candidates:
            return candidates[0][1]

        return None

    # --------------------------------------------------------
    # Connect
    # --------------------------------------------------------

    def connect(self):

        if serial is None:

            print(
                "WARNING: pyserial is not installed."
            )

            return False

        for attempt in range(
            1,
            SERIAL_CONNECT_RETRIES + 1,
        ):

            port = self.find_port()

            if port is None:

                print(
                    "WARNING: ESP32 not found "
                    f"(attempt {attempt}/"
                    f"{SERIAL_CONNECT_RETRIES})"
                )

                time.sleep(
                    SERIAL_CONNECT_DELAY_S
                )

                continue

            try:

                print(
                    f"Connecting ESP32 on "
                    f"{port}..."
                )

                self.serial = serial.Serial(
                    port=port,
                    baudrate=self.baudrate,
                    timeout=0.02,
                    write_timeout=0.05,
                )

                # USB serial may reset the ESP32.
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
                    f"WARNING: ESP32 connection "
                    f"failed: {exc}"
                )

                self.serial = None
                self.connected = False

                time.sleep(
                    SERIAL_CONNECT_DELAY_S
                )

        return False

    # --------------------------------------------------------
    # Send command
    # --------------------------------------------------------

    def send(
        self,
        steering_deg,
        motor_pwm,
        mode,
        force=False,
    ):

        if (
            not self.connected
            or self.serial is None
        ):
            return False

        now = time.perf_counter()

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
                    motor_pwm,
                ),
            )
        )

        packet = (
            "CMD,"
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
                f"ERROR: ESP32 serial failure: "
                f"{exc}"
            )

            self.connected = False

            return False

    # --------------------------------------------------------
    # Stop
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

        except (
            serial.SerialException,
            OSError,
        ):

            pass

    # --------------------------------------------------------
    # Ping
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
    # Poll responses
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

                if response.startswith(
                    "ERR"
                ):

                    print(
                        f"ESP32: {response}"
                    )

        except (
            serial.SerialException,
            OSError,
        ):

            self.connected = False

    # --------------------------------------------------------
    # Close
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
# CONFIG VALIDATION
# ============================================================

def validate_config():

    vertical_sum = (
        TOP_RATIO
        + MIDDLE_RATIO
        + BOTTOM_RATIO
    )

    horizontal_sum = (
        LEFT_RATIO
        + CENTER_RATIO
        + RIGHT_RATIO
    )

    if not np.isclose(
        vertical_sum,
        1.0,
    ):

        raise ValueError(
            "Vertical grid ratios "
            "must sum to 1.0"
        )

    if not np.isclose(
        horizontal_sum,
        1.0,
    ):

        raise ValueError(
            "Horizontal grid ratios "
            "must sum to 1.0"
        )

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
            "GRID_COLORS does not contain "
            "exactly the 9 required cells."
        )

    if (
        set(BLACK_GRID.keys())
        != expected_cells
    ):

        raise ValueError(
            "BLACK_GRID does not contain "
            "exactly the 9 required cells."
        )

    for cell, colours in (
        GRID_COLORS.items()
    ):

        for colour in colours:

            if colour not in COLOR_CENTERS:

                raise ValueError(
                    f"Unknown colour "
                    f"'{colour}' in {cell}"
                )


# ============================================================
# CAMERA BACKEND
# ============================================================

def pick_default_backend():

    if (
        CAMERA_BACKEND_OVERRIDE
        is not None
    ):

        return CAMERA_BACKEND_OVERRIDE

    if sys.platform.startswith(
        "win"
    ):

        return cv2.CAP_DSHOW

    if sys.platform.startswith(
        "linux"
    ):

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
            f"WARNING: camera open failed "
            f"(attempt {attempt}/"
            f"{CAMERA_OPEN_RETRIES})"
        )

        time.sleep(
            CAMERA_OPEN_RETRY_DELAY_S
        )

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
# GRID
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

    return f"{row}_{column}"


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


# ============================================================
# COLOUR MASK
# ============================================================

def create_color_mask(
    hsv,
    color,
    tolerance,
):

    center = COLOR_CENTERS[
        color
    ]

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

    if color == "red":

        mask_a = cv2.inRange(
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

        mask_b = cv2.inRange(
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

        return clean_mask(
            cv2.bitwise_or(
                mask_a,
                mask_b,
            )
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

    return clean_mask(
        cv2.inRange(
            hsv,
            lower,
            upper,
        )
    )


# ============================================================
# BLACK MASK
# ============================================================

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

    return clean_mask(
        cv2.inRange(
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
    )


# ============================================================
# CONTOUR EXTRACTION
# ============================================================

def detect_objects(
    mask,
    color,
    x_offset=0,
    y_offset=0,
    min_area=MIN_AREA,
):

    contours, _ = (
        cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )
    )

    detections = []

    for contour in contours:

        area = cv2.contourArea(
            contour
        )

        if area < min_area:
            continue

        x, y, w, h = (
            cv2.boundingRect(
                contour
            )
        )

        moments = cv2.moments(
            contour
        )

        if moments["m00"]:

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
                "contour":
                    global_contour,

                "area": area,

                "x":
                    x + x_offset,

                "y":
                    y + y_offset,

                "w": w,
                "h": h,

                "cx":
                    cx + x_offset,

                "cy":
                    cy + y_offset,
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
# PILLAR DETECTION
# ============================================================

def detect_pillars(
    detections
):

    red = [
        d
        for d in detections
        if (
            d["color"] == "red"
            and d["area"]
            >= PILLAR_MIN_AREA
        )
    ]

    green = [
        d
        for d in detections
        if (
            d["color"] == "green"
            and d["area"]
            >= PILLAR_MIN_AREA
        )
    ]

    red_target = (
        max(
            red,
            key=lambda d: (
                d["area"]
                * 0.6
                +
                d["cy"]
                * 0.4
            ),
        )
        if red
        else None
    )

    green_target = (
        max(
            green,
            key=lambda d: (
                d["area"]
                * 0.6
                +
                d["cy"]
                * 0.4
            ),
        )
        if green
        else None
    )

    return (
        red_target,
        green_target,
    )


# ============================================================
# TRACK LINE DETECTION
# ============================================================

def detect_track_lines(
    hsv,
    width,
    height,
    tolerance,
):

    """
    Detect orange and blue WRO track lines in the lower
    camera region.

    The WRO rules specify orange and blue lines as 20 mm
    track markings.

    Returns:
        left_line
        right_line
        primary_line
    """

    roi_y = int(
        height
        * LINE_ROI_TOP
    )

    roi = hsv[
        roi_y:height,
        0:width
    ]

    orange_mask = (
        create_color_mask(
            roi,
            "orange",
            tolerance,
        )
    )

    blue_mask = (
        create_color_mask(
            roi,
            "blue",
            tolerance,
        )
    )

    orange_objects = (
        detect_objects(
            orange_mask,
            "ORANGE_LINE",
            0,
            roi_y,
            LINE_MIN_AREA,
        )
    )

    blue_objects = (
        detect_objects(
            blue_mask,
            "BLUE_LINE",
            0,
            roi_y,
            LINE_MIN_AREA,
        )
    )

    lines = (
        orange_objects
        + blue_objects
    )

    # Ignore tiny / extremely narrow noise.
    lines = [
        line
        for line in lines
        if (
            line["w"] >= 5
            and line["h"] >= 5
        )
    ]

    if not lines:

        return (
            None,
            None,
            None,
            orange_mask,
            blue_mask,
        )

    # Calculate the x position of each detected line.
    for line in lines:

        line["center_x"] = (
            line["cx"]
        )

    left_candidates = [
        line
        for line in lines
        if line["center_x"]
        < width * 0.50
    ]

    right_candidates = [
        line
        for line in lines
        if line["center_x"]
        >= width * 0.50
    ]

    left_line = (
        max(
            left_candidates,
            key=lambda d:
                d["area"],
        )
        if left_candidates
        else None
    )

    right_line = (
        max(
            right_candidates,
            key=lambda d:
                d["area"],
        )
        if right_candidates
        else None
    )

    primary_line = max(
        lines,
        key=lambda d:
            d["area"],
    )

    return (
        left_line,
        right_line,
        primary_line,
        orange_mask,
        blue_mask,
    )


# ============================================================
# LANE ERROR
# ============================================================

def calculate_line_error(
    left_line,
    right_line,
    width,
):

    image_center = (
        width / 2.0
    )

    if (
        left_line is not None
        and right_line is not None
    ):

        lane_center = (
            left_line["center_x"]
            + right_line["center_x"]
        ) / 2.0

    elif left_line is not None:

        # A single left line implies
        # the car should remain to its right.
        estimated_lane_width = (
            width * 0.40
        )

        lane_center = (
            left_line["center_x"]
            + estimated_lane_width
        )

    elif right_line is not None:

        estimated_lane_width = (
            width * 0.40
        )

        lane_center = (
            right_line["center_x"]
            - estimated_lane_width
        )

    else:

        return None

    error_pixels = (
        lane_center
        - image_center
    )

    error_normalized = (
        error_pixels
        / image_center
    )

    return max(
        -1.0,
        min(
            1.0,
            error_normalized,
        ),
    )


# ============================================================
# CENTRING
# ============================================================

def calculate_centering(
    cx,
    frame_width,
):

    center = (
        frame_width / 2.0
    )

    error_pixels = (
        cx - center
    )

    normalized = (
        error_pixels
        / center
    )

    if abs(
        normalized
    ) <= CENTER_DEADZONE:

        direction = "CENTER"

    elif normalized < 0:

        direction = "LEFT"

    else:

        direction = "RIGHT"

    return (
        error_pixels,
        normalized,
        direction,
    )


# ============================================================
# PD
# ============================================================

def reset_pd():

    global previous_error
    global previous_error_time

    previous_error = 0.0
    previous_error_time = None


def calculate_pd(
    error,
    now=None,
):

    global previous_error
    global previous_error_time

    if now is None:
        now = time.perf_counter()

    if (
        abs(error)
        <= CENTER_DEADZONE
    ):

        error = 0.0

    if (
        previous_error_time
        is None
    ):

        derivative = 0.0

    else:

        dt = (
            now
            - previous_error_time
        )

        if dt <= 0:

            derivative = 0.0

        else:

            derivative = (
                error
                - previous_error
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

    previous_error = error
    previous_error_time = now

    return output


# ============================================================
# PILLAR SIDE BIAS
# ============================================================

def apply_pillar_strategy(
    steering_deg,
    pillar_color,
    pillar_x,
    width,
):

    if pillar_color == "red":

        # RED -> pass RIGHT.
        #
        # Steering away from the pillar means moving right
        # when the pillar is on the left/forward path.
        required_side = "RIGHT"

        bias = PILLAR_BIAS_DEG

    elif pillar_color == "green":

        # GREEN -> pass LEFT.
        required_side = "LEFT"

        bias = -PILLAR_BIAS_DEG

    else:

        return (
            steering_deg,
            "NONE",
        )

    # Bias can be reduced when the pillar is already on
    # the required side.

    image_center = (
        width / 2.0
    )

    if required_side == "RIGHT":

        if pillar_x < image_center:

            steering_deg += bias

        else:

            steering_deg += (
                bias * 0.35
            )

    elif required_side == "LEFT":

        if pillar_x > image_center:

            steering_deg += bias

        else:

            steering_deg += (
                bias * 0.35
            )

    steering_deg = max(
        STEERING_MIN_DEG,
        min(
            STEERING_MAX_DEG,
            steering_deg,
        ),
    )

    return (
        steering_deg,
        required_side,
    )


# ============================================================
# SPEED CONTROL
# ============================================================

def calculate_speed(
    steering_deg,
    pillar_active=False,
    distance=None,
):

    steering_fraction = (
        abs(steering_deg)
        / STEERING_MAX_DEG
    )

    speed = (
        BASE_SPEED
        -
        STEERING_SPEED_REDUCTION
        * steering_fraction
    )

    if pillar_active:

        speed -= 15

    if (
        distance is not None
        and distance < 30.0
    ):

        speed -= 25

    speed = max(
        MIN_SPEED,
        min(
            MAX_SPEED,
            speed,
        ),
    )

    return int(speed)


# ============================================================
# LAP TRACKING
# ============================================================

def update_lap_counter(
    start_section_visible,
):

    global lap_count
    global previous_start_zone
    global last_lap_event_time

    now = time.perf_counter()

    entered = (
        start_section_visible
        and not previous_start_zone
    )

    if entered:

        if (
            now
            - last_lap_event_time
            > LAP_EVENT_COOLDOWN_S
        ):

            if lap_count < TARGET_LAPS:

                lap_count += 1

                last_lap_event_time = now

    previous_start_zone = (
        start_section_visible
    )


# ============================================================
# FUTURE IMU INTERFACE
# ============================================================

class IMUInterface:

    """
    Interface placeholder for the 6-axis IMU.

    Once the exact IMU board/model is confirmed, the implementation
    goes here.

    Expected useful outputs:

        gyro_z_dps
        accel_x
        accel_y
        accel_z

    A 6-axis IMU does NOT provide magnetometer heading directly.
    The gyro can provide yaw-rate damping for the PD controller.
    """

    def __init__(self):

        self.available = False

        self.gyro_z_dps = 0.0

        self.accel_x = 0.0
        self.accel_y = 0.0
        self.accel_z = 0.0

    def update(self):

        # Hardware-specific implementation will be inserted here.
        return False

    def get_yaw_rate(self):

        return self.gyro_z_dps


# ============================================================
# FUTURE TOF INTERFACE
# ============================================================

class ToFInterface:

    """
    Interface placeholder for the VL ToF sensor.

    Exact implementation depends on the confirmed sensor
    breakout/model and bus interface.

    distance_cm:
        None when unavailable.
    """

    def __init__(self):

        self.available = False
        self.distance_cm = None

    def update(self):

        # Hardware-specific implementation will be inserted here.
        return False

    def get_distance(self):

        return self.distance_cm


# ============================================================
# DEBUG DRAWING
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

    lines = (
        (
            (0, y_top),
            (width, y_top),
        ),

        (
            (0, y_middle),
            (width, y_middle),
        ),

        (
            (x_left, 0),
            (x_left, height),
        ),

        (
            (x_right, 0),
            (x_right, height),
        ),
    )

    for p1, p2 in lines:

        cv2.line(
            frame,
            p1,
            p2,
            (0, 255, 255),
            GRID_LINE_THICKNESS,
            cv2.LINE_AA,
        )


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

    labels = (
        (
            "TOP 40%",
            10,
            30,
        ),

        (
            "MIDDLE 20%",
            10,
            y_top + 30,
        ),

        (
            "BOTTOM 40%",
            10,
            y_middle + 30,
        ),

        (
            "LEFT 30%",
            10,
            height - 15,
        ),

        (
            "CENTER 40%",
            x_left + 15,
            height - 15,
        ),

        (
            "RIGHT 30%",
            x_right + 10,
            height - 15,
        ),
    )

    for text, x, y in labels:

        cv2.putText(
            frame,
            text,
            (
                x,
                y,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
        )


def draw_detection(
    frame,
    detection,
    label=None,
):

    x = int(
        detection["x"]
    )

    y = int(
        detection["y"]
    )

    w = int(
        detection["w"]
    )

    h = int(
        detection["h"]
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

    if label is None:

        label = (
            detection["color"]
        )

    cv2.putText(
        frame,
        label,
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
# MAIN
# ============================================================

def main():

    validate_config()

    cap = open_camera()

    if cap is None:

        print(
            "ERROR: Camera could not be opened."
        )

        return

    esp32 = ESP32Controller(
        port=SERIAL_PORT_OVERRIDE,
        baudrate=SERIAL_BAUD,
    )

    esp32_connected = (
        esp32.connect()
    )

    if esp32_connected:

        if esp32.ping():

            print(
                "ESP32: PONG"
            )

        else:

            print(
                "WARNING: ESP32 ping failed."
            )

    else:

        print(
            "WARNING: ESP32 unavailable. "
            "Starting vision-only mode."
        )

    imu = IMUInterface()
    tof = ToFInterface()

    # --------------------------------------------------------
    # Debug windows
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

    cv2.createTrackbar(
        "Tolerance",
        "WRO Vision",
        25,
        80,
        lambda x: None,
    )

    previous_time = (
        time.perf_counter()
    )

    try:

        while True:

            # =================================================
            # CAMERA
            # =================================================

            ret, frame = (
                cap.read()
            )

            if not ret:

                print(
                    "ERROR: camera frame read failed."
                )

                break

            height, width = (
                frame.shape[:2]
            )

            tolerance = (
                cv2.getTrackbarPos(
                    "Tolerance",
                    "WRO Vision",
                )
            )

            # =================================================
            # SENSOR UPDATE
            # =================================================

            imu.update()
            tof.update()

            tof_distance = (
                tof.get_distance()
            )

            # =================================================
            # VISION
            # =================================================

            blurred = smooth(
                frame
            )

            hsv = cv2.cvtColor(
                blurred,
                cv2.COLOR_BGR2HSV,
            )

            full_mask = np.zeros(
                (
                    height,
                    width,
                ),
                dtype=np.uint8,
            )

            detections = []

            # =================================================
            # 3x3 GRID
            # =================================================

            (
                y_top,
                y_middle,
                x_left,
                x_right,
            ) = get_grid(
                width,
                height,
            )

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

                    cell_name = (
                        f"{row_name}_"
                        f"{column_name}"
                    )

                    roi_hsv = hsv[
                        y1:y2,
                        x1:x2
                    ]

                    cell_mask = np.zeros(
                        (
                            y2 - y1,
                            x2 - x1,
                        ),
                        dtype=np.uint8,
                    )

                    # ----------------------------------------
                    # Expected colours
                    # ----------------------------------------

                    for colour in (
                        GRID_COLORS[
                            cell_name
                        ]
                    ):

                        mask = (
                            create_color_mask(
                                roi_hsv,
                                colour,
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
                                colour,
                                x1,
                                y1,
                                MIN_AREA,
                            )
                        )

                    # ----------------------------------------
                    # Black
                    # ----------------------------------------

                    if BLACK_GRID[
                        cell_name
                    ]:

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
                                MIN_AREA,
                            )
                        )

                    full_mask[
                        y1:y2,
                        x1:x2
                    ] = cell_mask

            # =================================================
            # PILARS
            # =================================================

            (
                red_pillar,
                green_pillar,
            ) = detect_pillars(
                detections
            )

            # =================================================
            # TRACK LINES
            # =================================================

            (
                left_line,
                right_line,
                primary_line,
                orange_mask,
                blue_mask,
            ) = detect_track_lines(
                hsv,
                width,
                height,
                tolerance,
            )

            line_error = (
                calculate_line_error(
                    left_line,
                    right_line,
                    width,
                )
            )

            # =================================================
            # NAVIGATION DECISION
            # =================================================

            steering_error = 0.0

            pillar_active = False

            active_pillar = None

            pillar_side = "NONE"

            distance = tof_distance

            # -------------------------------------------------
            # Prefer pillars when clearly detected.
            # -------------------------------------------------

            if (
                red_pillar is not None
                or
                green_pillar is not None
            ):

                pillar_active = True

                if (
                    red_pillar is not None
                    and
                    green_pillar is not None
                ):

                    # Choose the nearer/stronger image target.
                    red_score = (
                        red_pillar["area"]
                        * 0.6
                        +
                        red_pillar["cy"]
                        * 0.4
                    )

                    green_score = (
                        green_pillar["area"]
                        * 0.6
                        +
                        green_pillar["cy"]
                        * 0.4
                    )

                    if (
                        red_score
                        >= green_score
                    ):

                        active_pillar = (
                            red_pillar
                        )

                    else:

                        active_pillar = (
                            green_pillar
                        )

                elif red_pillar is not None:

                    active_pillar = (
                        red_pillar
                    )

                else:

                    active_pillar = (
                        green_pillar
                    )

                pillar_colour = (
                    active_pillar[
                        "color"
                    ]
                )

                _, pillar_error, _ = (
                    calculate_centering(
                        active_pillar[
                            "cx"
                        ],
                        width,
                    )
                )

                steering_error = (
                    pillar_error
                )

                (
                    _,
                    pillar_side,
                ) = apply_pillar_strategy(
                    0.0,
                    pillar_colour,
                    active_pillar[
                        "cx"
                    ],
                    width,
                )

                current_navigation_mode = (
                    NavigationMode.RED_PILLAR
                    if pillar_colour
                    == "red"
                    else
                    NavigationMode.GREEN_PILLAR
                )

                pillar_distance = (
                    estimate_distance(
                        active_pillar["h"]
                    )
                )

                if (
                    distance is None
                ):

                    distance = (
                        pillar_distance
                    )

            # -------------------------------------------------
            # Otherwise follow track.
            # -------------------------------------------------

            elif line_error is not None:

                steering_error = (
                    line_error
                )

                current_navigation_mode = (
                    NavigationMode.TRACK
                )

            # -------------------------------------------------
            # Nothing detected.
            # -------------------------------------------------

            else:

                steering_error = 0.0

                current_navigation_mode = (
                    NavigationMode.SEARCH
                )

                reset_pd()

            # =================================================
            # PD
            # =================================================

            if (
                current_navigation_mode
                != NavigationMode.SEARCH
            ):

                steering_deg = (
                    calculate_pd(
                        steering_error
                    )
                )

            else:

                steering_deg = 0.0

            # =================================================
            # PILLAR BIAS
            # =================================================

            if active_pillar is not None:

                steering_deg, pillar_side = (
                    apply_pillar_strategy(
                        steering_deg,
                        active_pillar[
                            "color"
                        ],
                        active_pillar[
                            "cx"
                        ],
                        width,
                    )
                )

            # =================================================
            # SPEED
            # =================================================

            motor_pwm = (
                calculate_speed(
                    steering_deg,
                    pillar_active,
                    distance,
                )
            )

            mode = "DRIVE"

            # =================================================
            # DEBUG TARGET
            # =================================================

            target_cell = "NONE"

            if active_pillar is not None:

                target_cell = get_cell(
                    active_pillar[
                        "cx"
                    ],
                    active_pillar[
                        "cy"
                    ],
                    width,
                    height,
                )

            elif primary_line is not None:

                target_cell = get_cell(
                    primary_line[
                        "cx"
                    ],
                    primary_line[
                        "cy"
                    ],
                    width,
                    height,
                )

            # =================================================
            # LAP STATE
            # =================================================
            #
            # Do not claim a lap here yet.
            #
            # The exact field-specific start-zone detector needs
            # calibration against the actual starting section.
            #
            # This function is ready for that detector.
            # =================================================

            update_lap_counter(
                start_zone_detected
            )

            # If target lap count is reached, transition toward
            # parking/finish logic once the parking detector exists.
            if lap_count >= TARGET_LAPS:

                current_navigation_mode = (
                    NavigationMode.PARK
                )

                mode = "PARK"

            # =================================================
            # SEND ESP32 COMMAND
            # =================================================

            if esp32.connected:

                esp32.send(
                    steering_deg,
                    motor_pwm,
                    mode,
                )

            # =================================================
            # DEBUG DRAWING
            # =================================================

            outline = (
                frame.copy()
            )

            for detection in (
                detections
            ):

                draw_detection(
                    outline,
                    detection,
                )

            # -------------------------------------------------
            # Draw orange / blue line candidates.
            # -------------------------------------------------

            if left_line is not None:

                cv2.circle(
                    outline,
                    (
                        int(
                            left_line[
                                "center_x"
                            ]
                        ),
                        int(
                            left_line[
                                "cy"
                            ]
                        ),
                    ),
                    10,
                    (0, 255, 255),
                    2,
                )

            if right_line is not None:

                cv2.circle(
                    outline,
                    (
                        int(
                            right_line[
                                "center_x"
                            ]
                        ),
                        int(
                            right_line[
                                "cy"
                            ]
                        ),
                    ),
                    10,
                    (255, 255, 0),
                    2,
                )

            # -------------------------------------------------
            # Draw lane centre.
            # -------------------------------------------------

            if (
                left_line is not None
                and
                right_line is not None
            ):

                lane_center = int(
                    (
                        left_line[
                            "center_x"
                        ]
                        +
                        right_line[
                            "center_x"
                        ]
                    )
                    / 2.0
                )

                cv2.line(
                    outline,
                    (
                        lane_center,
                        height - 20,
                    ),
                    (
                        width // 2,
                        height - 20,
                    ),
                    (0, 255, 255),
                    3,
                )

            # -------------------------------------------------
            # Draw grid.
            # -------------------------------------------------

            draw_grid(
                frame
            )

            draw_grid(
                outline
            )

            draw_labels(
                frame
            )

            # -------------------------------------------------
            # Highlight pillar.
            # -------------------------------------------------

            if active_pillar is not None:

                px = int(
                    active_pillar[
                        "cx"
                    ]
                )

                py = int(
                    active_pillar[
                        "cy"
                    ]
                )

                cv2.circle(
                    outline,
                    (
                        px,
                        py,
                    ),
                    18,
                    (0, 255, 255),
                    3,
                )

                cv2.line(
                    outline,
                    (
                        width // 2,
                        py,
                    ),
                    (
                        px,
                        py,
                    ),
                    (0, 255, 255),
                    2,
                )

            # -------------------------------------------------
            # Distance label.
            # -------------------------------------------------

            if distance is not None:

                distance_text = (
                    f"{distance:.1f} cm"
                )

            else:

                distance_text = "--"

            # -------------------------------------------------
            # Panel
            # -------------------------------------------------

            panel = [
                (
                    "MODE: "
                    f"{current_navigation_mode}"
                ),

                (
                    "PILLAR: "
                    (
                        active_pillar[
                            "color"
                        ].upper()
                        if active_pillar
                        is not None
                        else "NONE"
                    )
                ),

                (
                    "PASS: "
                    f"{pillar_side}"
                ),

                (
                    "CELL: "
                    f"{target_cell}"
                ),

                (
                    "LINE ERROR: "
                    f"{(
                        line_error
                        if line_error
                        is not None
                        else 0.0
                    ):+.3f}"
                ),

                (
                    "STEERING: "
                    f"{steering_deg:+.1f} deg"
                ),

                (
                    "MOTOR: "
                    f"{motor_pwm}"
                ),

                (
                    "TOF: "
                    f"{distance_text}"
                ),

                (
                    "LAPS: "
                    f"{lap_count}/"
                    f"{TARGET_LAPS}"
                ),

                (
                    "IMU: "
                    (
                        "AVAILABLE"
                        if imu.available
                        else
                        "NOT CONNECTED"
                    )
                ),

                (
                    "ESP32: "
                    (
                        "CONNECTED"
                        if esp32.connected
                        else
                        "DISCONNECTED"
                    )
                ),
            ]

            cv2.rectangle(
                frame,
                (
                    10,
                    50,
                ),
                (
                    390,
                    (
                        50
                        + len(panel)
                        * 24
                        + 15
                    ),
                ),
                (0, 0, 0),
                -1,
            )

            for i, text in enumerate(
                panel
            ):

                cv2.putText(
                    frame,
                    text,
                    (
                        20,
                        73
                        + i * 24,
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.48,
                    (255, 255, 255),
                    2,
                )

            # -------------------------------------------------
            # FPS
            # -------------------------------------------------

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

            # -------------------------------------------------
            # Mask
            # -------------------------------------------------

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
                "COLOUR / BLACK MASK",
                (
                    10,
                    30,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
            )

            # -------------------------------------------------
            # Windows
            # -------------------------------------------------

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

            # -------------------------------------------------
            # Keyboard
            # -------------------------------------------------

            key = (
                cv2.waitKey(1)
                & 0xFF
            )

            # ESC
            if key == 27:

                break

            # SPACE = emergency stop
            if key == ord(" "):

                if esp32.connected:

                    esp32.send(
                        0.0,
                        0,
                        "STOP",
                        force=True,
                    )

                reset_pd()

    finally:

        try:

            if esp32.connected:

                print(
                    "Sending STOP..."
                )

                esp32.stop()

        finally:

            esp32.close()

            cap.release()

            cv2.destroyAllWindows()


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":
    main()