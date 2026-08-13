<div align="center">

# Challenge Strategy

**How the team plans to reason about the Open and Obstacle Challenges.**


[← Project home](../README.md) · [Software](../software/README.md) · [Diagrams](../docs/diagrams/README.md)

</div>

---

This folder holds the team's challenge plans, flow diagrams, pseudocode, assumptions, and design decisions. The strategy is implemented in `software/raspberry_pi/wromain.py` (decision layer) and `software/esp32/obstacleChallenge.ino` (execution layer).

> [!IMPORTANT]
> **Safety is built in.** The ESP32 enters `MODE_FAULT` on serial timeout (350 ms) or an invalid command, so a vision or link failure stops the vehicle instead of letting it run uncontrolled. The Pi sends only the wire tokens `DRIVE`, `PARK`, `FINISH`, `STOP`, or `PING`; the `MODE_*` names are internal firmware states and are never sent over the serial link.

## 1. System decision flow

```text
Camera frame
   │
   ▼
3×3 colour grid (red / green / purple / orange / blue / black)
   │
   ▼
Contour detection → target selection
   │
   ▼
Centering error → PD steering → dynamic drive speed
   │
   ▼
USB serial (115200) → ESP32
   │
   ▼
Wire: "CMD,<steer_deg>,<pwm>,<mode>"  (mode ∈ DRIVE, PARK, FINISH)
   │
   ▼
Firmware states: MODE_DRIVE / MODE_PARK / MODE_STOP / MODE_FINISH / MODE_FAULT
   │
   ▼
MG996R steering servo + TB6612FNG → N20 drive motor
```

**Why PD, not PID:** the field has no sustained steady-state error, so the integral term would only add windup and risk saturation. The derivative term damps oscillation at corners, which is the dominant stability concern during lane following. Logging the number of interventions per lap gives a measurable performance metric for tuning (see the [PID tuning log](../docs/other/pid_tuning_log.md)).

**Why dynamic drive speed:** a fixed speed either wastes time on straights or becomes unstable in corners and near walls. Drive PWM is lowered when the vision centring error is large, when a corner is detected, or when the VL53L0X wall distance drops below the safety margin. This keeps the control loop stable without sacrificing lap time on open corridor sections.

## 2. Module map

`software/raspberry_pi/wromain.py` (decision layer, runs on the Pi):
- **Perception / grid:** captures the camera frame and builds a 3x3 colour grid of cells.
- **Colour masks:** OpenCV HSV masks for red, green, purple, orange, blue, black (black is the neutral/background cell). Note the WRO magenta parking blocks are labelled `purple` in the code (the `COLOR_CENTERS` key is `"purple"`), so strategy and code stay consistent.
- **Target selection:** picks the centring target (corridor centre, pillar side, or parking reference) from the grid and ToF input.
- **PD controller:** converts lateral error into a steering angle and a dynamic drive speed.
- **Serial interface:** sends `CMD,<steer_deg>,<pwm>,<mode>` (mode `DRIVE` or `PARK`) and replies to `PING`; never sends `MODE_*` tokens.

`software/esp32/obstacleChallenge.ino` (execution layer, runs on the ESP32):
- **Serial parser:** reads `CMD,<steer>,<pwm>,<mode>` and the bare commands `STOP`, `PING`. Unknown mode returns `ERR,BAD_MODE` and stays safe.
- **State machine:** `MODE_DRIVE`, `MODE_PARK`, `MODE_STOP`, `MODE_FINISH`, `MODE_FAULT`. Only `DRIVE`/`PARK` arrive on the wire (plus `STOP`/`FINISH`/`PING` as bare or mode forms); invalid or timed-out input drives `MODE_FAULT`.
- **Actuator drivers:** MG996R steering servo and TB6612FNG motor driver for the N20 motor.
- **Watchdog:** 350 ms serial timeout forces `MODE_FAULT` (motor stop + centring steer), so the car fails safe.

## 3. Open Challenge strategy (3 laps, randomised walls)

- **Lane keeping:** centre the vehicle on the corridor using the vision centring error + VL53L0X wall-distance check. Speed is reduced when a wall is closer than the safety margin (proximity-driven speed control).
- **Corners:** detect the corner by wall geometry; steer with the PD controller; near the 40° lock the gain is softened to avoid jerky transitions.
- **Lap counting:** count crossings of section boundary markers (orange/blue lines): 8 sections per lap.
- **Finish:** after 3 laps, stop autonomously inside the finish section and hold position.

## 4. Obstacle Challenge strategy (3 laps + pillars + parking)

**Pillar rule (WRO 2026):** pass the **red** pillar on its **right**, the **green** pillar on its **left**. The pillars must not be moved.

1. **Detection:** camera grid detects pillar colour; VL53L0X confirms distance.
2. **Passing logic:** the centring target is biased toward the correct side of the pillar; the ToF verifies clearance, then the car re-centres. If the pillar is closer than the emergency margin, the car biases away immediately.
3. **Lap count** as in Open Challenge; pillars only have to be obeyed on the three official laps (per Appendix A, they may be bypassed either side afterwards).
4. **Parking (after 3 laps):**
    - Detect the purple (the WRO magenta parking blocks) parking-limit blocks with the camera.
    - Align parallel to the outer wall using MPU6050 heading.
    - Enter the lot in small steps; VL53L0X measures the gap and stops the car inside the 20 cm-wide lot, parallel within the 2 cm tolerance.
    - Overshoot handling: back up in small IMU-controlled steps, never touching the purple (the WRO magenta parking blocks) blocks (touching them ends the round with no parking points).

## 5. Edge cases and recovery

| Case | Behaviour |
| --- | --- |
| Line / colour lost | Slow sweep to re-acquire the grid; resume lane following once the corridor centre is found again |
| Serial dropout (Pi to ESP32) | Watchdog trips at 350 ms → `MODE_FAULT`: motor stop + centre steering (fails safe) |
| Invalid wire command | Firmware replies `ERR,BAD_MODE`, ignores the command, and stays in its current safe state |
| Pillar too close | Emergency bias away from pillar; clearance re-verified by ToF before re-centring |
| Parking overshoot | Small IMU-controlled reverse steps to bring the heading and position back inside tolerance, without touching the blocks |
| Wall too close (600 mm corridor) | Speed reduction + steer correction driven by the VL53L0X reading |
| Surprise rule (Day 2) | Strategy parameters isolated in a single config file so a new rule can be prepared without a code rewrite |

## 6. Wire protocol examples

The Pi sends the following on the USB serial link (115200 baud). These are the only valid wire tokens. The `MODE_*` names below are internal firmware states and are NOT sent.

| Pi sends | Meaning |
| --- | --- |
| `CMD,-15.50,140,DRIVE` | Steer -15.50 deg, PWM 140, drive mode |
| `CMD,0,0,FINISH` | Stop and mark round finished |
| `STOP` | Bare stop command (motor off, steer centred) |
| `PING` | Liveness check; firmware replies to confirm link |
| `CMD,0,90,PARK` | Steer centred, PWM 90, parking mode |

Any message with a mode other than `DRIVE`, `PARK`, `FINISH`, `STOP`, or a bare `PING`/`STOP` is rejected with `ERR,BAD_MODE` and the firmware remains safe.

## 7. Safety behaviour

- One power switch + one start button only (rules-compliant starting procedure).
- ESP32 fails safe on any communication loss or invalid command (watchdog 350 ms, or `MODE_FAULT` on bad input).
- The vehicle stops autonomously when the round end condition is met; no wireless communication is used at any point.
