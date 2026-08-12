<div align="center">

# Vehicle Design

**Mechanical design of the WRO 2026 Future Engineers vehicle.**

[← Project home](../README.md) · [Electronics](../electronics/README.md) · [Engineering journal](../docs/engineering_journal/README.md)

</div>

---

## 1. Design philosophy

Three constraints drive every mechanical choice:

1. **Rule compliance:** WRO 2026 requires a 4-wheel vehicle with **one driving axle and one steering actuator** (Rules 11.3, 11.5, 11.13). Differential drive and one-motor-per-side are disqualified.
2. **Envelope & mass:** ≤ 300×200×300 mm and ≤ 1.5 kg (Rules 11.1–11.2).
3. **Reproducibility:** everything must be rebuildable from files in this repository (LightBurn/DXF, STL, BOM).

The vehicle uses **front Ackermann steering with a servo** and **rear-axle drive with one N20 motor**, on a **laser-cut 3 mm plywood double-stack chassis**.

---

## 2. Steering: Ackermann geometry

**Why Ackermann:** at a corner, the inner front wheel must turn tighter than the outer front wheel, so all four wheels roll about a single instant centre. Without this (parallel steering), tyres scrub sideways, grip drops, and the car is unstable at speed — exactly what kills run consistency.

### Steering mechanism

- **Actuator:** TowerPro MG996R digital servo (high torque, metal gears).
- **Linkage:** servo horn → tie rod → steering knuckles (3D-printed), forming the Ackermann trapezoid.
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

## 3. Chassis: laser-cut 3 mm plywood (LightBurn)

- **Material:** 3 mm plywood — lighter than acrylic at equal stiffness, damps motor vibration, doesn't crack at screw points, cuts cleanly and fast.
- **Tool:** school laser cutter, designed in **LightBurn** (source `.lbrn` + exported DXF/PDF published in `models/chassis/`).
- **Edge treatment:** two thin coats of clear varnish seal the cut edges against moisture and warp.
- **Alternative considered:** acrylic (cracks under load), fully 3D-printed (slow, less rigid), aluminium (harder to cut, heavier).

### Double-stack layout — space utilisation

The 300×200 mm footprint is used vertically to fit the full system:

| Deck | Contents | Why |
| --- | --- | --- |
| **Lower deck** | ESP32, TB6612FNG motor driver, batteries | Low centre of mass, short motor/servo wiring |
| **Upper deck** | Raspberry Pi 4B, Camera Module 3 Wide | Camera horizon height ~120 mm; Pi clear of motor noise sources |

The two decks are separated and supported by **brass standoff offsets**, giving a rigid, ventilated sandwich that uses the height envelope efficiently.

### Wood + LEGO + brass offsets mounting system

Instead of drilling new holes for every iteration, we fuse three systems:

- **Wood (plywood decks):** primary structure, laser-cut precisely.
- **LEGO beams and pins:** universal mounting rails with a precise 8 mm hole grid — sensors, drivers and brackets can be moved in 8 mm steps without re-cutting the chassis. Quick, repeatable repositioning during testing.
- **Brass standoffs / offsets:** set deck spacing and create rigid mounting pillars; brass threads are far more durable than wood screws when parts are repeatedly removed.

This hybrid makes the mechanical design **iterative by construction**: a camera or sensor that needs a different position is moved in minutes, and the change is photographed for the engineering journal.

---

## 4. Drive: rear axle, single N20 motor

- **Motor:** N20 6 V 600 RPM micro metal gear motor (spare unit carried).
- **Transmission:** motor drives the rear axle through the gearbox in a mechanically coupled layout (compliant with Rule 11.13 — drive wheels are physically connected through the axle; no independent side motors).
- **Wheel:** ~40 mm diameter, high-traction rubber.

### Speed / torque reasoning

- **Speed:** 3 laps ≈ 36–40 m; at 0.55 m/s cruise ≈ 66–72 s — well inside the 3-minute round, leaving margin for corners and parking. N20 free-run at 600 RPM ≈ 1.2 m/s theoretical; we cruise below it for consistency.
- **Torque:** rolling resistance for 1.3 kg ≈ 1.3–2.6 N → required torque ≈ 0.03–0.06 kg·cm at the wheel. N20 stall torque ≈ 0.8–1.0 kg·cm — >10× margin. The design is speed-limited, not torque-limited, which is correct for a flat, low-friction mat.

---

## 5. Component placement

| Component | Location | Justification |
| --- | --- | --- |
| Camera Module 3 Wide | Upper deck, forward | Sees pillars 0.5–1.5 m ahead; reaction distance at cruise speed |
| VL53L0X ToF | Front centre | Pillar + parking-gap distance, mm-accurate, colour-independent |
| HC-SR04 ultrasonic | Front corner | Redundant wall proximity (independent bus from I²C sensors) |
| MPU6050 IMU | Centre of mass | Minimal lever-arm coupling into gyro; heading for turns/parking |
| Raspberry Pi 4B | Upper deck | Vision processing, high-level decisions |
| ESP32 | Lower deck | Real-time motor/servo control, safety state machine |
| MG996R servo | Front axle, centre | Drives Ackermann linkage; shortest linkage run |
| Batteries | Lower deck, rear | Low CG; counterbalances steering assembly |

---

## 6. Current development status

The mechanical design is through its second iteration (31°→40° steering, double-stack chassis assembled, drive train bench-tested). Integration and tuning are ongoing at the school lab; every change is logged in the [engineering journal](../docs/engineering_journal/README.md) and photographed in [images/robot/](../images/robot/README.md). LightBurn and CAD source files are published with the design records as they stabilise.
