# PID / Control Tuning Log

**Honest template for PD gain and control-loop tuning records.**

This file will hold the team's PD (proportional + derivative) gain and control-tuning records as the vehicle is tuned on the mat. It is referenced from:

- [`../engineering_journal/README.md`](../engineering_journal/README.md) (Entry 09, software state machine)
- [`../../strategy/README.md`](../../strategy/README.md) (PD steering rationale)
- [`../testing/README.md`](../testing/README.md) (test T3)

## How to use this log

Each tuning change gets one row in the table below. Record the date, the parameter changed, the previous value, the new value, the reason for the change, and the measured result. Only log values that were actually tried on the vehicle or in a bench test; do not pre-fill predicted numbers.

## Tuning record

| Date | Parameter | Previous | New | Reason | Result |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

Suggested parameters to track as tuning proceeds (example columns, not pre-filled):

- `Kp_steer` (steering proportional gain, deg per unit lateral error)
- `Kd_steer` (steering derivative gain, deg per unit error rate)
- `drive_pwm_straight` (cruise PWM on open corridor)
- `drive_pwm_corner` (PWM near 40° lock / narrow corridor)
- `wall_safety_m` (VL53L0X proximity margin before speed reduction)

> [!NOTE]
> No entries yet - to be populated during vehicle tuning. Nothing here is fabricated.
