# Chassis Assembly Guide

Step-by-step build sequence for the laser-cut plywood chassis. A future team rebuilds the vehicle by following this guide with the cut file and the [mechanical BOM](bom_mechanical.md).

Read the [design overview](README.md) first. Follow the [electronics guide](../electronics/README.md) for the wiring that is referenced below.

## Tools and consumables

- School laser cutter (see [laser cutter setup](laser_cutter_setup.md))
- 3 mm plywood, clear varnish, small brush
- Screwdriver set (M2/M3), pliers, small ruler, marker
- Brass standoffs (M3, ~35 mm effective deck spacing)
- LEGO beams, pins, axle and connector assortment
- Adhesive pads or double-sided tape for the electronics

## Steps

### 1. Cut the decks

Cut the two plywood decks from [wooden_plate.dxf](wooden_plate.dxf) geometry, following the [laser cutter setup](laser_cutter_setup.md) power/speed settings. The lower deck carries the drivetrain and electronics cut-outs; the upper deck carries the Pi and camera-mount cut-outs and the standoff holes.

### 2. Seal the edges

Apply two thin coats of clear varnish to the cut edges. This stops moisture warp and splintering during handling and rework.

### 3. Lower deck: drivetrain

- Fit the rear axle and both rear wheels (~30 mm) onto the lower deck, aligned to the axle cut-outs.
- Mount the N20 6 V motor so its gearbox drives the rear axle directly.
- Mount the ESP32, TB6612FNG driver and battery tray per the [electronics layout](../electronics/README.md). Battery sits rear for CG.
- Check both rear wheels rotate freely and that nothing binds on the deck.

### 4. Steering sub-frame (front)

- Build the front sub-frame from LEGO beams on the front of the lower deck. The 8 mm grid lets the geometry be re-jigged without re-cutting.
- Fit the MG996R servo on the centre line of the front axle.
- Connect the servo horn to the tie rod and the tie rod to both 3D-printed steering knuckles to form the Ackermann trapezoid (see [Ackermann geometry](ackermann_geometry.md)).
- Set full-lock steer angles to the current setting (40°) and check inner/outer symmetry.

### 5. Standoffs and upper deck

- Fix the brass standoffs to the lower deck at the marked holes.
- Lower the upper deck onto the standoffs and secure it. Deck spacing ends up ~35 mm.
- Mount the Raspberry Pi 4B and the camera on the upper deck, forward, at the design horizon height (~120 mm). See [camera mount](camera_mount.md).

### 6. Wire the vehicle

- Route power and signal wires from the lower-deck electronics to the upper-deck Pi and to the servo and motor, following the [electronics wiring guide](../electronics/README.md).
- Keep servo and drive currents off the logic reference, and keep the power leads short.

### 7. Photograph and log

- Photograph each finished stage into [images/robot/](../images/robot/README.md).
- Log deviations from this guide in the [engineering journal](../docs/engineering_journal/README.md).

## Checks after assembly

| Check | How | Record to |
| --- | --- | --- |
| Envelope ≤ 300x200x300 mm | Envelope gauge | Engineering journal |
| Mass ≤ 1.5 kg | Scale | [Mass budget](mass_budget.md) |
| Both rear wheels driven | Lifted slow run | Engineering journal |
| Steering symmetric | Protractor on wheel faces | [Tuning log](../docs/other/pid_tuning_log.md) |
| No binding at full lock | Slow roll full left and right | Engineering journal |

## Related documents

- [Mechanical BOM](bom_mechanical.md)
- [Laser cutter setup](laser_cutter_setup.md)
- [Rule compliance checklist](rules_checklist.md)
