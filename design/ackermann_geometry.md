# Ackermann Steering Geometry

The vehicle uses front Ackermann steering with a single MG996R servo. This document records the geometry parameters, the prototype iterations, and the cornering analysis behind the current 40 degree setting.

## Why Ackermann

In a corner the inner front wheel travels on a tighter arc than the outer front wheel. Ackermann geometry angles the two front wheels differently (inner steers further than outer) so that all four wheels roll about a single instant centre. With parallel steering the tyres scrub sideways, grip drops, and the vehicle is unstable at speed. Ackermann is what keeps the run consistent through the competition's 90 degree corners.

## Geometry parameters

| Parameter | Value | Notes |
| --- | --- | --- |
| Wheelbase | ~150 mm | Front to rear axle centres (design target) |
| Track | ~140 mm | Wheel centre spacing, kept equal front and rear (design target) |
| Steer angle, outer wheel (current) | 40° | Prototype 2 |
| Steer angle, outer wheel (prototype 1) | 31° | Superseded |
| Linkage | Servo horn to tie rod to knuckles | Knuckles 3D-printed; geometry jigged on a LEGO 8 mm grid |

## The Ackermann condition

For a given turn, the inner and outer steer angles relate through:

```
cot(outer) - cot(inner) = track / wheelbase
```

With track ~140 mm and wheelbase ~150 mm the required angle difference is small but necessary. The knuckle steering-arm angles and tie-rod length are set in the CAD/LightBurn layout to match this condition, then verified mechanically by measuring the inner and outer angles at full lock.

## Prototype iterations

| Parameter | Prototype 1 | Prototype 2 | Decision |
| --- | --- | --- | --- |
| Max outer steer angle | 31° | 40° | 40° selected |
| Turning radius (design estimate) | ~250 mm | ~180 mm | 40° |
| 600 mm corridor 90° corner clearance | Clipped wall line (~0 mm) | ~80 mm each side | 40° |
| Servo transition harshness | Soft | Slightly harsher | PD softened near lock |

## Turning radius

For small slip the turning radius follows R = wheelbase / tan(outer steer angle).

- At 31°: 150 mm / tan(31°) ≈ 250 mm (design estimate)
- At 40°: 150 mm / tan(40°) ≈ 180 mm (design estimate)

The 40 degree lock is what makes the sharp 90° corners of the 600 mm corridor configuration reachable with margin. The PD controller softens the servo gain near lock so the slightly harsher transition at 40° does not produce jerky steering.

## Verification plan

1. Measure inner and outer steer angle at full lock with a protractor against the wheel face.
2. Measure actual turning radius on the mat (left and right, should be symmetric).
3. Confirm no tyre scrubbing at full lock in a slow straight roll.
4. Log results in the [tuning log](../docs/other/pid_tuning_log.md) and the [engineering journal](../docs/engineering_journal/README.md).

## Related documents

- [Design overview](README.md), steering section
- [Steering tuning plan](steering_tuning_plan.md)
- [Mechanical BOM](bom_mechanical.md)
