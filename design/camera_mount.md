# Camera Mount Design

Mounting notes for the Camera Module 3 Wide on the upper deck. The mount exists to hold the camera at the design horizon height with the field of view covering the obstacles ahead.

## Placement

| Parameter | Design value | Notes |
| --- | --- | --- |
| Camera | Raspberry Pi Camera Module 3 Wide | Wide-angle lens |
| Deck | Upper deck, forward edge | Above the steering sub-frame, clear of the drive end |
| Horizon height | ~120 mm | From mat to lens centre, design target |
| Viewing distance | 0.5-1.5 m ahead | Reaction distance at the planned cruise speed (~0.55 m/s) |

## Why this placement

- The upper deck keeps the lens above the LEGO steering sub-frame and out of the front wheel arc at full lock.
- ~120 mm height balances a far view for cornering with a near view for parking-gap detection on the mat.
- The wide lens covers the 600 mm corridor walls side to side at the required look-ahead distance, so one camera is enough for wall following and pillar/parking detection.

## Mount construction

- The camera bracket is 3D-printed and fixed to the upper deck through a LEGO rail, so it can move fore and aft in 8 mm steps during tuning.
- The bracket STL is pending in the repository; until it is committed the mount is jigged with LEGO and the position is photographed into [images/robot/](../images/robot/README.md).
- A soft mounting pad between the bracket and deck damps motor vibration reaching the sensor.

## Checks after mounting

| Check | How |
| --- | --- |
| Lens height | Ruler from mat to lens centre |
| Tilt level | Bubble level on the bracket face |
| View ahead clear | Camera preview at max steer, both directions |
| Firmness | No visible shake in the preview when the motor runs |

Results of these checks are logged in the [engineering journal](../docs/engineering_journal/README.md).

## Related documents

- [Design overview](README.md), component placement
- [Assembly guide](assembly_guide.md)
- [Strategy](../strategy/README.md), sensing section
