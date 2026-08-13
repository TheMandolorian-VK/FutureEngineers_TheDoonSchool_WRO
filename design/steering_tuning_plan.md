# Steering Tuning Plan

How the steering is tuned and verified once the vehicle is on the mat. This plan is to be executed at the school lab; results are logged in the [tuning log](../docs/other/pid_tuning_log.md) and the [engineering journal](../docs/engineering_journal/README.md). Nothing here is a claim of results.

## Goals

- Confirm the 40 degree full-lock steer angle reaches the 600 mm corridor corners with ~80 mm clearance each side.
- Confirm the PD controller softens the servo near lock so the transition is not jerky.
- Confirm left and right steering symmetry.

## Pre-run mechanical checks

| Check | Pass criteria |
| --- | --- |
| Toe angle | Wheels straight and parallel at centre |
| Inner/outer angle at lock | Ackermann condition holds within protractor accuracy |
| Steering slop | No free play in the tie rod joints |
| Full-lock binding | Slow roll at full lock, both sides, no binding |

## Run sequence

1. **Straight-line hold:** run straight, measure lateral drift over 2 m. Adjust centre trim.
2. **Constant-radius circle:** fixed steering command, record circle diameter left and right. Symmetry check.
3. **600 mm corridor 90° corner:** approach at cruise speed, record wall clearance left and right, adjust PD gain near lock.
4. **S-curve:** two corners back to back to check the servo transitions.
5. **Parking approach:** slow speed, camera + ToF, record final gap error.

## Parameters that may be tuned

| Parameter | Where | Logged to |
| --- | --- | --- |
| Centre trim offset | Steering | Tuning log |
| PD proportional gain | Steering | Tuning log |
| PD derivative gain | Steering | Tuning log |
| Softening near lock | Steering | Tuning log |
| Cruise speed | Drive | Tuning log |

## Definition of done

The 600 mm corridor run is completed repeatedly without touching the walls, and the parking approach ends inside the gap tolerance, at which point the results are recorded and the design is locked for the event.

## Related documents

- [Ackermann geometry](ackermann_geometry.md)
- [Tuning log](../docs/other/pid_tuning_log.md)
- [Testing overview](../docs/testing/README.md)
