# PID Tuning Log

Method: **Ziegler–Nichols** for a starting point, then manual refinement on the actual track at realistic speed.

## Procedure

1. Set Kd = 0, Ki = 0. Raise Kp until the robot **sustains equal-amplitude oscillation** on a straight. Record `Ku` (ultimate gain).
2. Measure the oscillation period `Tu` (seconds).
3. Use the table below for an initial set, then hand-tune.

| Controller | Kp | Ki | Kd |
|---|---|---|---|
| Classic Z-N (PID) | 0.6 · Ku | 1.2 · Kp / Tu | Kp · Tu / 8 |

## Tuning rules that actually work

- **Raise speed slowly.** Tune at 60% speed first, then climb. The optimum set usually sits 5–10 runs before the failure point.
- **Sensor height is the biggest variable.** 2–4 mm above the surface. Check it before every run — a flexing chassis changes calibration mid-run.
- **Loop time must be < 10 ms.** If the derivative term operates on stale data it causes oscillation. Measure loop time with `micros()`.
- **Anti-windup:** clamp the integral term; reset it after each turn.
- **Direction conventions:** log signed error + output so the team can debug sign flips.

## Log table

| Date | Version | Kp | Ki | Kd | Base speed | Max speed | Corner performance | Line lost? | Notes / next change |
|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |  |
