<div align="center">

# Challenge Strategy

**How the team plans to reason about the Open and Obstacle Challenges.**

![WRO](https://img.shields.io/badge/WRO-2026-0057B8?style=for-the-badge&logo=robotframework&logoColor=white)
![Category](https://img.shields.io/badge/Category-Future%20Engineers-7A2E8E?style=for-the-badge)
![Strategy](https://img.shields.io/badge/Strategy-PD%20Steering-7A2E8E?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Development%20Phase-F59E0B?style=for-the-badge)
![Updated](https://img.shields.io/badge/Updated-2026--08--13-555555?style=for-the-badge)

[← Project home](../README.md) · [Software](../software/README.md) · [Diagrams](../docs/diagrams/README.md)

</div>

---

This folder holds the team's challenge plans, flow diagrams, pseudocode, assumptions, and design decisions. The strategy is implemented in `software/raspberry_pi/wromain.py` (decision layer) and `software/esp32/obstacleChallenge.ino` (execution layer).

> [!IMPORTANT]
> **Safety is built in.** The ESP32 enters `MODE_FAULT` on serial timeout or an invalid command, so a vision or link failure stops the vehicle instead of letting it run uncontrolled.

## 1. System decision flow

```text
Camera frame
   │
   ▼
3×3 colour grid (red / green / blue / orange / purple / black)
   │
   ▼
Contour detection → target selection
   │
   ▼
Centering error → PD steering → drive speed
   │
   ▼
USB serial (115200) → ESP32
   │
   ▼
MODE_DRIVE / MODE_PARK / MODE_STOP / MODE_FINISH / MODE_FAULT
   │
   ▼
MG996R steering servo + TB6612FNG → N20 drive motor
```

**Why PD, not PID:** the field has no sustained steady-state error, so the integral term would only add windup; the derivative term damps oscillation at corners. Logging the number of interventions per lap gives a measurable performance metric for tuning (see `other/pid_tuning_log.md`).

## 2. Open Challenge strategy (3 laps, randomised walls)

- **Lane keeping:** centre the vehicle on the corridor using the vision centring error + VL53L0X wall-distance check. Speed is reduced when a wall is closer than the safety margin (proximity-driven speed control).
- **Corners:** detect the corner by wall geometry; steer with the PD controller; near the 40° lock the gain is softened to avoid jerky transitions.
- **Lap counting:** count crossings of section boundary markers (orange/blue lines): 8 sections per lap.
- **Finish:** after 3 laps, stop autonomously inside the finish section and hold position.

## 3. Obstacle Challenge strategy (3 laps + pillars + parking)

**Pillar rule (WRO 2026):** pass the **red** pillar on its **right**, the **green** pillar on its **left**. The pillars must not be moved.

1. **Detection:** camera grid detects pillar colour; VL53L0X confirms distance.
2. **Passing logic:** the centring target is biased toward the correct side of the pillar; the ToF verifies clearance, then the car re-centres. If the pillar is closer than the emergency margin, the car biases away immediately.
3. **Lap count** as in Open Challenge; pillars only have to be obeyed on the three official laps (per Appendix A, they may be bypassed either side afterwards).
4. **Parking (after 3 laps):**
   - Detect the magenta parking-limit blocks with the camera.
   - Align parallel to the outer wall using MPU6050 heading.
   - Enter the lot in small steps; VL53L0X measures the gap and stops the car inside the 20 cm-wide lot, parallel within the 2 cm tolerance.
   - Overshoot handling: back up in small IMU-controlled steps, never touching the magenta blocks (touching them ends the round with no parking points).

## 4. Edge cases and recovery

| Case | Behaviour |
| --- | --- |
| 🔍 Line/colour lost | Re-acquire by a slow sweep, then resume |
| 🔌 Serial timeout Pi ↔ ESP32 | `MODE_FAULT`: safe stop (fails safe by design) |
| 🚧 Pillar too close | Emergency bias away from pillar |
| ↩️ Parking overshoot | Small IMU-controlled reverse steps |
| 🧱 Wall too close (600 mm corridor) | Speed reduction + steer correction |
| 🎲 Surprise rule (Day 2) | Strategy parameters isolated in a single config file so a new rule can be prepared without a code rewrite |

## 5. Safety behaviour

- One power switch + one start button only (rules-compliant starting procedure).
- ESP32 fails safe on any communication loss or invalid command.
- The vehicle stops autonomously when the round end condition is met; no wireless communication is used at any point.
