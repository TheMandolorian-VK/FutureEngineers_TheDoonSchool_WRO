<div align="center">

# Vehicle Design

**Mechanical design of the WRO 2026 Future Engineers vehicle.**


[← Project home](../README.md) · [Electronics](../electronics/README.md) · [Engineering journal](../docs/engineering_journal/README.md)

</div>

---

## Documentation index

- [Rule compliance checklist](rules_checklist.md) - WRO 2026 requirements mapped to the design
- [Ackermann geometry](ackermann_geometry.md) - steering geometry, iterations and cornering analysis
- [Mass budget](mass_budget.md) - component mass estimates and margins
- [Assembly guide](assembly_guide.md) - step-by-step build sequence
- [Mechanical BOM](bom_mechanical.md) - chassis and drivetrain parts
- [Cut file notes](dxf_notes.md) - what wooden_plate.dxf contains today
- [Design decision log](design_decisions.md) - decisions and rejected alternatives
- [Laser cutter setup](laser_cutter_setup.md) - school laser workflow and kerf
- [Camera mount design](camera_mount.md) - camera placement and mount
- [Steering tuning plan](steering_tuning_plan.md) - on-mat steering verification

---

## 1. Design philosophy

Three constraints drive every mechanical choice:

1. **Rule compliance:** WRO 2026 requires a 4-wheel vehicle with **one driving axle and one steering actuator** (Rules 11.3, 11.5, 11.13). Differential drive and one-motor-per-side are disqualified.
2. **Envelope & mass:** ≤ 300×200×300 mm and ≤ 1.5 kg (Rules 11.1–11.2).
3. **Reproducibility:** everything must be rebuildable from files in this repository (LightBurn/DXF, STL, BOM).

The vehicle uses **front Ackermann steering with a servo** and **fully rear-wheel drive with one N20 motor**, on a **laser-cut 3 mm plywood double-stack chassis**. The rear N20 and its wheels are deliberately smaller than the front wheels, which lowers the drive/steering mass and gives the chassis a slight rearward (backward) tilt for stability through the 90° corners.

> [!IMPORTANT]
> **Rule compliance is non-negotiable.** WRO 2026 requires one driving axle and one steering actuator (Rules 11.3, 11.5, 11.13). Differential drive is disqualified. The build must confirm both rear wheels receive drive torque.

---

## 2. Design targets

The values below are **design targets** captured from the CAD layout and the current prototype. They are targets, not verified measurements: physical verification (envelope gauge, scale, and track/wheelbase callipers) is pending and will be logged in the engineering journal.

| Parameter | Target | Notes |
| --- | --- | --- |
| Envelope (L×W×H) | ≤ 300×200×300 mm | Hard rule limit (11.1–11.2); layout keeps margin |
| Wheelbase | ~150 mm | Distance between front and rear axle centres |
| Track (front / rear) | ~140 mm | Wheel centre spacing, kept equal for Ackermann |
| Deck spacing | ~35 mm | Vertical gap between upper and lower plywood decks |
| Ground clearance | ~12 mm | Chassis underside to mat; set by deck height and wheel size |
| Total mass | ≤ 1.5 kg | Target; see mass budget below |

### Mass budget (component mass estimates)

All figures are **design estimates** from datasheets and quoted part weights, not weighed values. The total is kept well under the 1.5 kg rule limit to leave tuning margin.

| Component | Est. mass (g) |
| --- | --- |
| Two plywood decks + brass standoffs | 120 |
| 11 V 3S LiPo battery | 150 |
| N20 6 V motor + gearbox | 30 |
| MG996R servo | 55 |
| Raspberry Pi 4B | 46 |
| Camera Module 3 Wide | 25 |
| ESP32 dev board | 25 |
| TB6612FNG driver + wiring | 15 |
| Four wheels (front ~40 mm, rear ~30 mm) | 60 |
| LEGO rails and mounting hardware | 150 |
| Misc (screws, tie rods, connectors) | 100 |
| **Estimated total** | **776** |

---

## 3. Steering: Ackermann geometry

**Why Ackermann:** at a corner, the inner front wheel must turn tighter than the outer front wheel, so all four wheels roll about a single instant centre. Without this (parallel steering), tyres scrub sideways, grip drops, and the car is unstable at speed: exactly what kills run consistency.

### Steering mechanism

- **Actuator:** TowerPro MG996R digital servo (high torque, metal gears).
- **Linkage:** servo horn → tie rod → steering knuckles (3D-printed), forming the Ackermann trapezoid. The steering arms, knuckles and tie-rod geometry are built from **LEGO beams and pins** on a front sub-frame, giving an adjustable, repeatable Ackermann trapezoid that can be re-jigged in 8 mm steps during tuning without re-cutting the chassis.
- **Geometry parameters (current):**
  - Maximum outer-wheel steer angle: **31°** (prototype 1)
  - Maximum outer-wheel steer angle: **40°** (prototype 2, current)
  - Inner/outer angle difference follows the Ackermann condition
    `cot(δ_o) − cot(δ_i) = track / wheelbase`.

### 31° → 40° iteration

| Parameter | Prototype 1 | Prototype 2 | Decision |
| --- | --- | --- | --- |
| Max steer angle | 31° | 40° | 40° selected |
| Turning radius (1000 mm corridor) | OK | Tighter | 40° |
| 600 mm corridor 90° corner clearance | clipped wall line (~0 mm) | ~80 mm each side | 40° |
| Servo transition harshness | Soft | Slightly harsher | Softened in PD control near lock |

The 40° lock lets the car execute the sharp 90° corners of the 600 mm corridor configuration while the PD controller softens gain near lock to avoid jerky transitions.

---

## 4. Chassis: laser-cut 3 mm plywood (LightBurn)

- **Material:** 3 mm plywood: lighter than acrylic at equal stiffness, damps motor vibration, doesn't crack at screw points, cuts cleanly and fast.
- **Tool:** school laser cutter, designed in **LightBurn**. The authoritative 2D cut file is committed as [`wooden_plate.dxf`](wooden_plate.dxf). The editable `.lbrn` LightBurn project is team-maintained and will be added to the repository so the chassis is reproducible from the repo alone (currently kept with the design records, not yet committed).
- **Edge treatment:** two thin coats of clear varnish seal the cut edges against moisture and warp.

> [!NOTE]
> The DXF is a 2D laser-cut flat pattern (the cut geometry), not a full 3D CAD model of the vehicle. It is the authoritative file for re-cutting the plywood decks. The editable `.lbrn` master will be committed alongside it so a future team can reproduce the chassis from this repository without external design files.

### Material tradeoff

| Material | Stiffness/weight | Cutting/fab | Durability | Verdict |
| --- | --- | --- | --- | --- |
| 3 mm plywood | Good stiffness per gram | Laser-cuts fast and clean | Damps vibration, resists screw cracking | **Selected** |
| Acrylic | Similar weight, more brittle | Laser-cuts well | Cracks at screw points under load | Rejected |
| 3D-printed (PLA/PETG) | Lower stiffness at low mass | Slow, layer-dependent | Flexible, warps near motors | Rejected for structure |
| Aluminium | Highest stiffness | Needs CNC/mill, not the school laser | Very durable, but heavier | Rejected (mass + tooling) |

The chassis prioritises low mass, fast iteration, and vibration damping on the school laser cutter. Plywood wins on all three against the alternatives above.

### LightBurn cut workflow (reproducibility)

The chassis is drawn in **LightBurn** and cut on the school laser cutter from 3 mm plywood. Reproducibility (Criterion 5) depends on the cut files carrying everything needed to re-cut the chassis identically:

- **Layers:** the lower deck carries the drivetrain/electronics cut-outs; the upper deck carries the Pi + camera-mount cut-outs and the brass-standoff holes.
- **Parameters recorded per file:** material (3 mm plywood), kerf compensation, and the cutter's power/speed setting for that material.
- **Files:** the authoritative, version-controlled cut file is [`wooden_plate.dxf`](wooden_plate.dxf). The editable `.lbrn` master is team-maintained and will be committed so the geometry is fully reproducible from the repository. The DXF defines the same flat geometry as the `.lbrn`; the `.lbrn` adds the cut layers, kerf and power/speed settings needed to drive the cutter.

### Double-stack layout: space utilisation

The 300×200 mm footprint is used vertically to fit the full system:

| Deck | Contents | Why |
| --- | --- | --- |
|  **Lower deck** | 11 V 3S LiPo pack, ESP32, TB6612FNG motor driver | Battery low for CG; short motor/servo wiring; servo + drive currents kept off the logic reference |
|  **Upper deck** | Raspberry Pi 4B, Camera Module 3 Wide | Camera horizon height ~120 mm; Pi clear of motor noise sources |

The two decks are separated and supported by **brass standoff offsets**, giving a rigid, ventilated sandwich that uses the height envelope efficiently.

### Wood + LEGO + brass offsets mounting system

Instead of drilling new holes for every iteration, we fuse three systems:

- **Wood (plywood decks):** primary structure, laser-cut precisely.
- **LEGO beams and pins:** universal mounting rails with a precise 8 mm hole grid: sensors, drivers and brackets can be moved in 8 mm steps without re-cutting the chassis. Quick, repeatable repositioning during testing.
- **Brass standoffs / offsets:** set deck spacing and create rigid mounting pillars; brass threads are far more durable than wood screws when parts are repeatedly removed.

This hybrid makes the mechanical design **iterative by construction**: a camera or sensor that needs a different position is moved in minutes, and the change is photographed for the engineering journal.

---

## 5. Why this layout satisfies the rules

- **One driving axle:** a single N20 6 V motor is mechanically coupled to the rear axle through its gearbox, driving both rear wheels via that one axle (Rule 11.3/11.5). There are no independent side motors and no differential, so the design is not differential/per-side drive, which the rules disqualify.
- **One steering actuator:** a single TowerPro MG996R servo drives the front Ackermann linkage; there is no second steering motor or caster actuator (Rule 11.13).
- **No wireless:** all control and power stays on the vehicle; there is no radio link between the car and an external controller, consistent with the no-wireless requirement.
- **Envelope and mass:** the double-stack plywood layout is designed to stay within ≤ 300×200×300 mm and ≤ 1.5 kg (Rules 11.1–11.2), with the mass budget in §2 kept under the limit.

---

## 6. Drive: rear axle, single N20 motor

- **Motor:** N20 6 V 600 RPM micro metal gear motor (spare unit carried).
- **Transmission:** motor drives the rear axle through the gearbox in a mechanically coupled layout (compliant with Rule 11.13: drive wheels are physically connected through the axle; no independent side motors).
- **Wheel:** front wheels ~40 mm diameter, high-traction rubber; **rear wheels are smaller (~30 mm design estimate)**, matched to the smaller rear N20. The rear bias lightens the drive end and produces the slight rearward chassis tilt described in §1; the axle is mechanically coupled (Rule 11.13 compliant: one driving axle, no independent side motors).

### Speed / torque reasoning

- **Top speed (driven wheel):** the driven rear wheels are the smaller ones (~30 mm design estimate), not the ~40 mm front wheels. Circumference ≈ π × 30 mm ≈ 94.2 mm. At the N20 free-run speed of 600 RPM (10 rev/s), the **theoretical no-load speed (design estimate)** is ≈ 94.2 mm × 10 ≈ 0.94 m/s. Real cruise speed is lower because of load, tyre slip, and the PD speed controller leaving margin for corners and parking. We plan to cruise near 0.55 m/s for consistency, well inside the 3-minute round.
- **Torque:** rolling resistance for ~0.8 kg (design mass estimate) ≈ 0.8–1.6 N → required torque ≈ 0.012–0.024 N·m at the wheel. The N20 stall torque is **datasheet-typical, to be confirmed by bench test** (≈ 0.08–0.10 N·m typical); this gives a comfortable margin on a flat, low-friction mat. The design is speed-limited, not torque-limited.

---

## 7. Component placement

| Component | Location | Justification |
| --- | --- | --- |
|  Camera Module 3 Wide | Upper deck, forward | Sees pillars 0.5–1.5 m ahead; reaction distance at cruise speed |
|  VL53L0X ToF | Front centre | Pillar + parking-gap distance, mm-accurate, colour-independent |
|  HC-SR04 ultrasonic | Front corner | Redundant wall proximity (independent bus from I²C sensors) |
|  MPU6050 IMU | Centre of mass | Minimal lever-arm coupling into gyro; heading for turns/parking |
|  Raspberry Pi 4B | Upper deck | Vision processing, high-level decisions |
|  ESP32 | Lower deck | Real-time motor/servo control, safety state machine |
|  MG996R servo | Front axle, centre | Drives Ackermann linkage; shortest linkage run |
|  11 V 3S LiPo battery | Lower deck, rear | Low CG; counterbalances steering assembly; sole energy source for the motor/servo rail |

---

## 8. Current development status

The mechanical design is through its second iteration (31°→40° steering, double-stack chassis assembled, drive train bench-tested). Integration and tuning are ongoing at the school lab; every change is logged in the [engineering journal](../docs/engineering_journal/README.md) and photographed in [images/robot/](../images/robot/README.md). The authoritative cut file [`wooden_plate.dxf`](wooden_plate.dxf) is committed; the editable `.lbrn` LightBurn project is team-maintained and will be added so the chassis is reproducible from the repository alone.
