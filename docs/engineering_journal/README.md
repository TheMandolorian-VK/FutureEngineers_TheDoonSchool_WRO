<div align="center">

# Engineering Journal

**A chronological record of decisions, iterations, and lessons.**


[← Documentation](../README.md) · [Testing](../testing/README.md) · [Design](../../design/README.md)

</div>

---

## How this journal maps to the WRO 2026 rubric

The WRO documentation evaluation uses five criteria, each scored 0/2/4/6, for a maximum of **30 points**. Each journal entry below is tagged with the criterion it supports.

| Criterion | What judges want | Where it lives |
| --- | --- | --- |
| 1. Mobility & Mechanical Design | Torque/speed reasoning, tradeoffs, testing | Entries 01–05 |
| 2. Power & Sensor Architecture | Single-battery two-rail power, sensor tradeoffs, calibration | Entries 06, 08, 11 |
| 3. Software Architecture & Obstacle Strategy | State machine, algorithm justification, tuning | Entries 08, 09, 10 |
| 4. Systems Thinking & Engineering Decisions | "We chose X instead of Y because…", constraints, risks | Entries 02–10 |
| 5. Reproducibility & GitHub Quality | README ≥5000 chars, commits, CAD, wiring, code | Entries 01–11 + repo structure (root [`README.md`](../../README.md), [`design/wooden_plate.dxf`](../../design/wooden_plate.dxf), [`hardware/wiring-guide/`](../../hardware/wiring-guide/README.md)) |

---

## Entry index

Click an entry number to jump to its section.

| # | Date | Topic | Criterion |
| --- | --- | --- | --- |
| [01](#01-system-architecture-two-controller-split-2026-07-15-by-dhrubo-m) | 2026-07-15 | System architecture: two-controller split (Pi + ESP32) | 1, 4, 5 |
| [02](#02-chassis-material-and-fabrication-2026-07-18-by-dhrubo-m) | 2026-07-18 | Chassis material and fabrication: 3 mm plywood + LightBurn | 1, 4, 5 |
| [03](#03-drive-system-n20-600-rpm-motor-2026-07-22-by-vivaan-k) | 2026-07-22 | Drive system: N20 600 RPM motor, torque and speed reasoning | 1, 4, 5 |
| [04](#04-steering-geometry-ackermann-31-40-2026-07-27-by-dhrubo-m) | 2026-07-27 | Steering geometry: Ackermann, 31° → 40° iteration | 1, 4, 5 |
| [05](#05-double-stack-layout-wood-lego-brass-offsets-2026-08-02-by-yug-j) | 2026-08-02 | Double-stack layout: wood + LEGO + brass offsets | 1, 4, 5 |
| [06](#06-motor-driver-l298n-tb6612fng-2026-08-05-by-yug-j) | 2026-08-05 | Motor driver: L298N → TB6612FNG (dropout and heat) | 2, 4, 5 |
| [07](#07-power-architecture-two-rail-two-battery-design-2026-08-07-by-yug-j) | 2026-08-07 | Power architecture: two-rail, two-battery design (historical, superseded by 11) | 4, 5 |
| [08](#08-sensor-selection-2026-08-09-by-vivaan-k) | 2026-08-09 | Sensor selection: camera, HC-SR04, VL53L0X, MPU6050 | 2, 3, 4, 5 |
| [09](#09-software-state-machine-and-obstacle-strategy-2026-08-11-by-vivaan-k--dhrubo-m) | 2026-08-11 | Software state machine and obstacle strategy | 3, 4, 5 |
| [10](#10-risk-register-and-failure-mode-analysis-2026-08-12-by-the-team) | 2026-08-12 | Risk register and failure-mode analysis | 3, 4, 5 |
| [11](#11-consolidated-confirmed-configuration-2026-08-13-by-dhrubo-m) | 2026-08-13 | Consolidated confirmed configuration (11 V 3S, rear tilt, LEGO Ackermann) | 2, 4, 5 |

> [!IMPORTANT]
> Every entry records the **problem**, **options considered**, **chosen direction with reasoning**, **available evidence** (calculation / simulation / observation / measured test), and **next action**. The vehicle is in an active development and iteration cycle; entries are written as the work happens, not retrofitted.

## Journal entries

### 01: System architecture: two-controller split (2026-07-15, by Dhrubo M.)

**Problem:** the vehicle must perceive colour cues (red/green pillars, orange/blue lines, magenta parking blocks), decide a route, and control steering + drive in real time: all within a 300×200×300 mm envelope and under 1.5 kg.

**Options considered:**
- A) Single Raspberry Pi 4B doing everything (camera, control loop).
- B) Single ESP32 doing everything (camera + control).
- C) Split: Pi 4B for vision + decision, ESP32 for time-critical actuator control.

**Chosen: C.** The Pi's OpenCV pipeline runs comfortably at its own pace while the ESP32 closes the motor/servo loop at millisecond rates over USB serial (115200 baud). This mirrors the separation of perception and control used in real automotive ECUs. The ESP32 also guarantees a safe stop (fault state) even if the Pi's vision loop stalls: a single-controller design could not provide this independently.

**Evidence:** the Pi↔ESP32 interface is a 115200-baud USB serial link. The Pi sends wire tokens `DRIVE`, `PARK`, `FINISH`, `STOP`, and `PING` (format `CMD,<steer>,<pwm>,<mode>`); the `MODE_*` names are internal ESP32 firmware states and are never sent on the wire. The protocol is specified in [`strategy/README.md`](../../strategy/README.md) and the power/interface layout in [`electronics/README.md`](../../electronics/README.md); it is implemented in `software/esp32/obstacleChallenge.ino`.

**Next action:** harden the serial protocol with checksums.

---

### 02: Chassis material and fabrication (2026-07-18, by Dhrubo M.)

**Problem:** a rigid, light, cheaply-reproducible chassis that fits 300×200 mm and can be made with the school's tools.

**Options considered:**
- A) 3 mm acrylic, laser-cut.
- B) 3 mm plywood, laser-cut via **LightBurn** (school cutter).
- C) Fully 3D-printed frame.
- D) Aluminium sheet.

**Chosen: B, with C for brackets.** Plywood is lighter than acrylic of equal stiffness, damps motor vibration better, and cuts cleanly on the school's laser cutter. Acrylic cracks at screw holes under servo load. The DXF export is committed (currently a placeholder rectangle; full deck patterns pending). Small brackets and sensor mounts are 3D-printed (PLA) where complex geometry is needed.

**Tradeoff:** plywood absorbs moisture and can warp: mitigated by sealing edges with two thin coats of clear varnish and keeping the chassis in the transport case between sessions.

**Evidence:** DXF export committed (see [cut file notes](../../design/dxf_notes.md)); vehicle renders in [`images/robot/`](../../images/robot/README.md). Photographs of cut parts will be added as the decks are cut.

**Next action:** test a 2.4 mm plywood variant to compare stiffness-to-mass.

---

### 03: Drive system: N20 600 RPM motor (2026-07-22, by Vivaan K.)

**Problem:** choose a drive motor with enough speed to complete 3 laps inside 3 minutes and enough torque to accelerate the vehicle reliably.

> [!NOTE]
> Corrected 2026-08-13 to match the confirmed configuration (Entry 11): the driven rear wheels are the smaller ~30 mm ones; front wheels ~40 mm.

**Calculation (speed):** N20 at 6 V free-runs at 600 RPM (10 rev/s). On the ~30 mm driven rear wheels (circumference ≈ π × 30 mm ≈ 94 mm) this gives a theoretical no-load speed ≈ 0.94 m/s. Real cruise speed will be lower under load; the plan is to cruise near 0.55 m/s for consistency, well inside the 3-minute round.

**Calculation (torque):** the N20 stall torque is datasheet-typical and will be confirmed by bench test. Rolling-resistance force for the vehicle mass is to be measured on the mat. The design is expected to be speed-limited, not torque-limited: correct for a flat, low-friction mat.

**Tradeoff:** higher-RPM variants (1000 RPM) would shorten lap time but worsen precision at stop lines and during parking. We prioritise **consistency** over peak speed, matching the rubric's "stability of mission solving".

**Chosen:** N20 6 V 600 RPM, one drive motor on the rear axle through the gearbox.

**Next action:** log actual wheel speed with an encoder on the rear axle.

---

### 04: Steering geometry: Ackermann, 31° → 40° (2026-07-27, by Dhrubo M.)

**Problem:** the track has 90° corners and (in the Open Challenge) corridors as narrow as 600 mm ± 100 mm. The car must steer the corner radius reliably without losing grip or scraping the walls.

**Options considered:**
- A) Differential steering (two side motors): **disallowed by the 2026 rules** (Rule 11.5).
- B) Single-centre pivot (caster-style): unstable at speed.
- C) **Ackermann steering**: front wheels steer with different angles: inner wheel tighter, outer wheel following a larger arc, so all four wheels roll about one instant centre without scrubbing.

**Chosen: C, driven by a TowerPro MG996R servo.**

**Iteration: 31° vs 40°:**
- Prototype 1 set maximum steer angle to 31°: the car tracked the ideal arc in the middle of a 1000 mm corridor, but in the 600 mm configuration the turning radius was too large and the rear inner corner clipped the wall line during a tight 90°.
- Prototype 2 raised the lock angle to 40°: the car negotiated the 600 mm corners with ~80 mm of clearance to both walls, at the cost of slightly harsher servo transitions. The Ackermann ratio was tuned (inner/outer angle difference) to keep all four wheels rolling without slip.
- Result: 40° selected for narrow-corridor reliability; the controller treats angles near lock as a distinct state so the PD gain can be softened and the car does not jerk.

**Evidence:** geometry and analysis documented in [`design/`](../../design/README.md) (Ackermann spec and turning-radius calculations); a dated steering-sweep record is pending in [testing T1](../testing/README.md).

**Next action:** add toe-in verification per side after every reassembly.

---

### 05: Double-stack layout: wood + LEGO + brass offsets (2026-08-02, by Yug J.)

**Problem:** fit two controllers, camera, four sensor families, servo, driver and the battery pack into 300×200 mm and keep the centre of mass low and the mass budget under 1.5 kg.

**Chosen: a two-deck chassis.**
- **Lower deck** (3 mm plywood): ESP32, TB6612FNG driver, the battery pack (lowest centre of mass).
- **Upper deck** (3 mm plywood): Raspberry Pi 4B + Camera Module 3 Wide, raised on brass standoff offsets.
- **Mounting fusion:** LEGO beams and pins are used as universal mounting rails (they provide precise, repeatable hole grids), brass standoff spacers set deck height, and the plywood decks are laser-cut. This "wood + LEGO + brass" system means a mount can be moved in 8 mm increments without re-cutting the chassis: very useful during sensor-placement iteration.

**Tradeoff:** the double stack raises the camera to a good horizon height (~120 mm) while the deck adds ~60 g. Placement was chosen to keep the combined centre of mass above the rear axle's roll centre.

**Next action:** measure the actual mass and CG; the DXF placeholder is committed as `design/wooden_plate.dxf`.

---

### 06: Motor driver: L298N → TB6612FNG (2026-08-05, by Yug J.)

**Problem:** initial bench prototype used an **L298N** module. In testing it ran hot and showed noticeable voltage dropout (≈1.5–2 V per channel under load), which reduced effective motor voltage and made the speed-PID inconsistent as batteries sagged.

**Options considered:**
- A) Keep L298N (cheap, available).
- B) **TB6612FNG** dual motor driver (1 A/channel, <0.5 V dropout, logic-level drive, small footprint).

**Chosen: B.** The TB6612FNG fits the space budget, loses far less voltage to the motor, and can be driven directly by the ESP32's 3.3 V logic without level shifting. The vehicle's N20 stalls below the driver's 1 A/channel continuous rating in normal running (see power budget).

**Evidence:** measured rail-to-motor voltage on both drivers during a stall test: the L298N dropped ~1.8 V; the TB6612FNG dropped ~0.4 V.

**Next action:** fuse the motor rail at 2 A to protect the driver.

---

### 07: Power architecture: two-rail, two-battery design (2026-08-07, by Yug J.)

> [!NOTE]
> Historical record only. This two-battery design was the configuration at the time of writing. It is **superseded** by the single 11 V 3S LiPo two-rail design in [Entry 11](#11-consolidated-confirmed-configuration-2026-08-13-by-dhrubo-m); the two-battery layout is no longer the current design.

**Problem:** a single shared battery caused motor transients to brown out the Pi during bench tests (servo stall + motor start together).

**Chosen: two separate supplies, per WRO Appendix D guidance.**
- **Motor rail:** 2S LiPo (7.4 V) → TB6612FNG → N20 motor and MG996R servo.
- **Logic rail:** separate battery pack → regulated 5 V rail → Raspberry Pi 4B, ESP32, HC-SR04, VL53L0X, MPU6050.
- Star grounding: all logic grounds meet at a single point; motor ground returns separately to its pack negative, keeping servo/motor currents out of the logic reference.
- Decoupling: 0.1 µF ceramic on every IC VCC; 100 µF electrolytic on the 5 V rail.

**Power budget (to be measured):** component currents per rail to be measured with a multimeter once the physical system is assembled (see [electronics/](../../electronics/README.md) power budget section). Both rails fused.

**Failure consideration:** a logic-rail brownout resets the ESP32, which starts in `MODE_STOP` (motor off, steering centred), so the vehicle does not run uncontrolled. `MODE_FAULT` is triggered by a serial timeout (>350 ms) or an invalid command.

**Next action:** record measured currents per rail in the power section of `electronics/README.md` as each subsystem is verified.

---

### 08: Sensor selection (2026-08-09, by Vivaan K.)

**Problem:** sense three things reliably: (a) colour cues on the field, (b) distance to walls/pillars/parking blocks, (c) orientation for turns and parking.

| Need | Option | Chosen | Why |
| --- | --- | --- | --- |
| Colour (pillars, lines, blocks) | TCS34725 colour sensor / **camera** | **Raspberry Pi Camera Module 3 Wide** | colour + geometry in one sensor; OpenCV HSV masks for red, green, blue, orange, magenta |
| Short-range distance (walls, pillars) | HC-SR04 ultrasonic | **VL53L0X ToF** (primary), HC-SR04 (redundant) | ToF is unaffected by surface colour and gives mm-precision up to ~1.2 m; ultrasonic is cheap but slow and spread-beam. HC-SR04 retained as independent redundancy because it does not share the I²C bus. |
| Orientation | N/A | **DFRobot Fermion MPU6050** | 6-axis IMU; yaw integration for 90° corner turns and straight-line correction during parking alignment |

**Placement justification (field geometry):** the camera is mounted forward on the upper deck to see pillars ~0.5–1.5 m ahead (reaction distance at 0.55 m/s ≈ 0.9–2.7 m). The VL53L0X is front-centre for pillar/parking gap measurement; the HC-SR04 is front-corner for wall proximity. MPU6050 is placed at the centre of mass to minimise lever-arm coupling into the gyro.

**Calibration (plan):** camera exposure locked; HSV tolerance is adjustable live (trackbar) in `wromain.py`, with boot-time auto-tuning to be added. MPU6050 zero-bias capture over 2 s at start and the VL53L0X 5-sample median filter are planned once the modules are wired; nothing is calibrated in code yet.

**Next action:** add I²C bus test + VL53L0X address-shift to avoid conflicts with the IMU.

---

### 09: Software state machine and obstacle strategy (2026-08-11, by Vivaan K. & Dhrubo M.)

**Problem:** structure the software so behaviour is predictable and judges can read the design.

**Chosen: two-layer state machine.**

*Raspberry Pi layer (perception + decision)*: `software/raspberry_pi/wromain.py`:
- Camera frames → 3×3 colour grid → per-cell colour masks (red/green/blue/orange/purple) → contour detection → target selection → centering error → **PD steering** (proportional + derivative on lateral offset) → dynamic drive speed.
- PD (rather than full PID) is used deliberately: the field has no sustained steady-state error that requires the integral term, and D-only damping prevents oscillation at corners without windup.

*ESP32 layer (execution + safety)*: `software/esp32/obstacleChallenge.ino`:
- The Pi sends wire tokens `DRIVE`, `PARK`, `FINISH`, `STOP`, and `PING` over a 115200-baud serial protocol (format `CMD,<steer>,<pwm>,<mode>`). These map to the internal firmware states `MODE_DRIVE`, `MODE_PARK`, `MODE_STOP`, `MODE_FINISH`, and `MODE_FAULT`. Fault mode is entered on serial timeout or invalid command: the vehicle always fails safe. The `MODE_*` names are internal states and are never sent on the wire.

**Obstacle strategy (Obstacle Challenge):**
1. Lane-follow by centring on the corridor (PD steering on vision offset; wall-distance check via VL53L0X planned once the ToF is wired).
2. Pillar handling: red pillar → pass on its **right**; green pillar → pass on its **left** (colour from camera grid). The code biases the centring target toward the correct side (+12°, reduced to 35% when the pillar is already on the required side). The ToF clearance re-check before re-centring is planned.
3. After 3 laps → the Pi sends `PARK`. The parking manoeuvre itself is **planned, not yet in code**: detect magenta parking-limit blocks with the camera, align parallel using the IMU heading, and use the ToF to stop at the correct depth inside the 20 cm-wide lot.
4. Open Challenge: corner handling via the PD controller today; wall-geometry corner detection and orange/blue section-line lap counting are planned. The lap counter depends on a start-zone detector that is not yet wired.

**Edge cases handled:** lost line (re-acquire by sweeping), serial timeout (fault stop), pillar too close (emergency bias). Planned: parking overshoot (back up in small IMU-controlled steps once the IMU is integrated).

**Testing/tuning method:** per-lap intervention count is logged; PD gains are set (KP = 32, KD = 10) and will be tuned against that metric, with results recorded in the [PID tuning log](../other/pid_tuning_log.md) (currently empty).

**Next action:** wire the start-zone detector and the parking manoeuvre in `wromain.py` (the IMU and ToF interfaces are currently placeholders).

---

### 10: Risk register and failure-mode analysis (2026-08-12, by the team)

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Camera glare / lighting change | Medium | High | exposure lock + boot-time HSV recalibration (planned); to be tested under fluorescent + spot lighting (T4) |
| Battery sag under servo+motor peak | Medium | High | single 11 V 3S LiPo feeding two-rail buck power; fused rails; pack with adequate C rating |
| Wall collision in 600 mm corridor | Medium | High | 40° steering, speed reduction near walls (planned: proximity-driven speed via VL53L0X once wired), ToF wall check (planned) |
| Serial dropout Pi↔ESP32 | Low | High | watchdog fault state + re-sync on checksum failure; USB cable strain-relieved |
| ToF misread on white mat at shallow angle | Medium | Medium | 5-sample median filter (planned); mount at 15° downward |
| Wheel slip during parking | Medium | Medium | low speed, IMU heading feedback (planned), short move steps |
| Sudden rule change (surprise rule, Day 2) | Medium | Medium | modular code: strategy params in one config file; reserve a config slot per round |

---

### 11: Consolidated confirmed configuration (2026-08-13, by Dhrubo M.)

**Context:** this entry records the final, confirmed mechanical + power configuration after the build stabilised. It **supersedes Entry 07**, replacing its two-battery design with a single 11 V 3S LiPo pack feeding two buck-regulated rails.

**Confirmed configuration:**
- **Structure:** laser-cut 3 mm plywood double-stack chassis (DXF export `design/wooden_plate.dxf` is a placeholder; `.lbrn` master and full deck patterns pending), brass standoff offsets between decks, LEGO beams/pins as adjustable mounting rails.
- **Decks:** upper deck = Raspberry Pi 4B + Camera Module 3 Wide; lower deck = 11 V 3S LiPo pack + ESP32 + TB6612FNG.
- **Drive:** rear-wheel drive, one N20 6 V 600 RPM motor on the rear axle. Rear wheels are smaller than the front, giving the chassis a slight rearward tilt.
- **Steering:** front TowerPro MG996R servo driving an Ackermann linkage built from LEGO beams/pins; outer lock 40° (Entry 04).
- **Sensing:** Pi Camera Module 3 Wide (colour/geometry), VL53L0X ToF (front distance), HC-SR04 (redundant wall proximity), DFRobot Fermion MPU6050 IMU (yaw).
- **Power:** single 11 V 3S LiPo → motor/servo rail bucked to ~6 V for N20 + MG996R; logic rail bucked to 5 V for Pi/ESP32/sensors (two-rail, star-grounded, fused).

**Why this is the final form:** every choice above is the result of the iterations logged in Entries 01–10 (two-controller split, plywood + LightBurn, N20 rear drive, 31°→40° Ackermann, L298N→TB6612FNG, two-rail power, sensor set). The smaller rear wheels + rearward tilt were adopted to lower the drive mass and improve corner stability without adding weight.

**Evidence:** DXF placeholder and wiring guide committed; physical build and measured values to be added as on-mat testing proceeds.

**Next action:** complete on-mat integration tests (T3–T10) and record measured rail currents and lap times.

---

## Process note

We add entries as we work on the design. Each entry explains what we considered, what we chose, and why.
