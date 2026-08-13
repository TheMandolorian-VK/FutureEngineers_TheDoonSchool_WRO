# Software Architecture

Deep-dive into the two-layer software system, grounded in the actual source code. This document is the reference for Criterion 3 (Software Architecture and Obstacle Strategy).

## System split

| Layer | Runs on | Responsibility | Module |
| --- | --- | --- | --- |
| Perception + decision | Raspberry Pi 4B | Camera capture, HSV colour grid, contour detection, target selection, PD steering, dynamic speed, serial commands | `software/raspberry_pi/wromain.py` |
| Execution + safety | ESP32 DevKit | Servo control, motor PWM, communication watchdog, emergency stop, status LEDs | `software/esp32/obstacleChallenge.ino` |

The Pi sends bounded actuator commands at 25 Hz over USB serial (115200 baud); the ESP32 executes them or enters `MODE_FAULT` if the link drops.

## Control loop (Pi)

The main loop in `wromain.py` runs once per camera frame:

```
Capture frame (1280x720 @ 60 fps)
   |
Update IMU / ToF (placeholders today)
   |
Gaussian blur -> HSV conversion
   |
3x3 grid: split frame into 9 cells (top/middle/bottom x left/center/right)
   |
Per-cell: create colour masks for expected colours (GRID_COLORS)
   |
Per-cell: contour extraction -> detections list
   |
Detect pillars (red/green, area >= PILLAR_MIN_AREA)
   |
Detect track lines (orange/blue, bottom 45% of frame)
   |
Target selection:
   - Pillar detected? -> use pillar centring error + bias
   - Line detected?  -> use lane centring error
   - Nothing?        -> SEARCH mode, reset PD
   |
PD steering: error -> steering_deg (clamped +/-45)
   |
Speed: BASE_SPEED - steering_fraction*80 - pillar - close_distance
   |
Send: "CMD,<steer>,<pwm>,<mode>" to ESP32
   |
Debug drawing (grid, detections, panel)
```

### Command rate

`ESP32_COMMAND_HZ = 25.0` (40 ms period). The Pi sends one `CMD` per frame (or faster if the frame rate is lower). The ESP32 watchdog timeout is 350 ms, so up to ~8 commands can be missed before a fault.

## Vision pipeline

### 3x3 colour grid

The frame is divided into 9 cells:

| Row | Height ratio | Vertical range |
| --- | --- | --- |
| Top | 40% | 0 to 40% |
| Middle | 20% | 40% to 60% |
| Bottom | 40% | 60% to 100% |

| Column | Width ratio | Horizontal range |
| --- | --- | --- |
| Left | 30% | 0 to 30% |
| Center | 40% | 30% to 70% |
| Right | 30% | 70% to 100% |

Each cell checks only its expected colours (defined in `GRID_COLORS`):

| Cell | Expected colours |
| --- | --- |
| top_left, top_center, top_right | red, green |
| middle_left, middle_center, middle_right | red, green, purple |
| bottom_left, bottom_center, bottom_right | orange, blue |

Black is checked in all cells except middle_center and bottom_center (per `BLACK_GRID`).

### HSV colour detection

Each colour is defined by a centre point in OpenCV HSV space and a tolerance (adjustable via a live trackbar):

| Colour | H | S | V | HSV range note |
| --- | --- | --- | --- | --- |
| red | 0 | 210 | 180 | wraps around 0/179 |
| green | 60 | 190 | 150 | |
| blue | 110 | 200 | 160 | |
| purple | 145 | 180 | 150 | WRO magenta parking blocks |
| orange | 15 | 220 | 180 | |

The `create_color_mask` function builds an inRange mask from the centre +/- tolerance, with hue tolerance = 35% of tolerance, and min saturation/value = centre - 2*tolerance.

### Contour extraction

`detect_objects` finds external contours on each mask, filters by area >= `MIN_AREA` (100 px), and computes the centroid (cx, cy) and bounding box (x, y, w, h) for each detection.

## Target selection

Priority order (highest wins):

1. **Pillars:** if red or green detections exist with area >= `PILLAR_MIN_AREA` (250 px), select the higher-scored pillar. Score = 0.6 * area + 0.4 * cy (larger and lower in the frame wins). The pillar's centring error becomes the steering input.
2. **Track lines:** if left and/or right orange/blue lines are detected in the bottom 45% of the frame, compute lane centre and error. Left/right split at frame midpoint.
3. **Search:** if nothing is detected, reset the PD controller and steer straight (SEARCH mode).

## PD controller

```python
error = lateral offset normalized to [-1, 1]
if abs(error) <= CENTER_DEADZONE (0.05): error = 0

derivative = (error - prev_error) / dt
derivative = clamp(derivative, -MAX_DERIVATIVE, +MAX_DERIVATIVE)  # 3.0

output = KP * error + KD * derivative  # KP=32, KD=10
output = clamp(output, -45, +45)  # degrees
```

The derivative clamp prevents spike-induced jerks. The deadzone (5% of frame width) avoids small corrections at centre.

## Pillar bias

When a pillar is active, `apply_pillar_strategy` adds a fixed bias to the steering output:

- Red pillar: +12 degrees (pass right)
- Green pillar: -12 degrees (pass left)

If the pillar is already on the required side of the frame centre, the bias is reduced to 35% (36% of 12 = ~4.2 degrees).

## Speed control

```python
steering_fraction = abs(steering_deg) / 45
speed = 165 - 80 * steering_fraction  # base 165, reduction 80 at full lock
if pillar_active: speed -= 15
if distance < 30 cm: speed -= 25  # monocular estimate today
speed = clamp(speed, 75, 210)  # PWM value
```

## ESP32 firmware

### State machine

```
MODE_STOP (initial)
   |
   v
MODE_DRIVE <-- CMD,...,DRIVE
MODE_PARK  <-- CMD,...,PARK
MODE_FINISH <-- CMD,...,FINISH
   |
   v (timeout or bad command)
MODE_FAULT (motor off, centred steering, red LED on)
```

### Serial protocol

| Command | Format | Response |
| --- | --- | --- |
| Drive/park | `CMD,<steer>,<pwm>,<mode>` | `ACK,CMD` |
| Stop | `STOP` | `ACK,STOP` |
| Ping | `PING` | `PONG` |
| Bad prefix | any | `ERR,BAD_PREFIX` |
| Bad steering | non-numeric | `ERR,BAD_STEERING` |
| Bad motor PWM | out of range | `ERR,BAD_MOTOR` |
| Bad mode | not DRIVE/PARK/FINISH/STOP | `ERR,BAD_MODE` |
| Buffer overflow | >128 chars | `ERR,BUFFER_OVERFLOW` |
| Unknown | anything else | `ERR,UNKNOWN_COMMAND` |

### Watchdog

`COMMAND_TIMEOUT_MS = 350`. If no valid command arrives within 350 ms, the ESP32 enters `MODE_FAULT`: motor stopped, steering centred, red LED on, green LED off.

### Status LEDs

| State | Green LED (GPIO 2) | Red LED (GPIO 4) |
| --- | --- | --- |
| Healthy (command recent, no fault) | ON | OFF |
| Fault or timeout | OFF | ON |

### Debug output

Every 1000 ms, the ESP32 prints a status line on serial:

```
STATUS,mode=DRIVE,steering=0.0,motor=150,command_age_ms=42
```

## Honest gaps (not yet implemented)

The following are placeholder interfaces in `wromain.py` and do not affect behaviour:

| Placeholder | Code location | What it does today |
| --- | --- | --- |
| IMU (MPU6050) | `IMUInterface` class | `available = False`; `gyro_z_dps = 0.0` |
| ToF (VL53L0X) | `ToFInterface` class | `available = False`; `distance_cm = None` |
| Start-zone detector | `start_zone_detected` variable | Always `False` (lap count never increments) |
| Parking manoeuvre | Main loop: `if lap_count >= TARGET_LAPS: mode = "PARK"` | Sets mode but no parking logic; the vehicle just keeps driving |
| Monocular distance | `estimate_distance` function | Active (KNOWN_OBJECT_HEIGHT_CM=20, FOCAL_LENGTH_PX=700); returns an approximate cm value used for speed reduction |

Until these are wired and implemented, the vehicle runs on vision + PD only. The code is structured so each placeholder can be filled in without changing the rest of the system.

## Related documents

- [Strategy overview](README.md)
- [Testing procedures](../testing/procedures.md)
- [Engineering journal entry 09](../engineering_journal/README.md)
