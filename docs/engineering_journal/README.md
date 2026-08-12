<div align="center">

# Engineering Journal

**A chronological record of decisions, iterations, and lessons.**

![WRO](https://img.shields.io/badge/WRO-2026-0057B8?style=for-the-badge&logo=robotframework&logoColor=white)
![Category](https://img.shields.io/badge/Category-Future%20Engineers-7A2E8E?style=for-the-badge)
![Journal](https://img.shields.io/badge/Journal-11%20Entries-16803A?style=for-the-badge)
![Rubric](https://img.shields.io/badge/Rubric-5%20Criteria%20×%206-16803A?style=for-the-badge)
![Updated](https://img.shields.io/badge/Updated-2026--08--13-555555?style=for-the-badge)

[← Documentation](../README.md) · [Testing](../testing/README.md) · [Design](../../design/README.md)

</div>

---

## How this journal maps to the WRO 2026 rubric

The WRO documentation evaluation uses five criteria, each scored 0/2/4/6, for a maximum of **30 points**. Each journal entry below is tagged with the criterion it supports.

| Criterion | What judges want | Where it lives |
| --- | --- | --- |
| 1. Mobility & Mechanical Design | Torque/speed reasoning, tradeoffs, testing | Entries 01–05 |
| 2. Power & Sensor Architecture | Power budget, sensor tradeoffs, calibration | Entries 06–08 |
| 3. Software Architecture & Obstacle Strategy | State machine, algorithm justification, tuning | Entry 09 |
| 4. Systems Thinking & Engineering Decisions | "We chose X instead of Y because…", constraints, risks | Entries 02–10 |
| 5. Reproducibility & GitHub Quality | README ≥5000 chars, commits, CAD, wiring, code | Root README + [`design/wooden_plate.dxf`](../../design/wooden_plate.dxf), [`hardware/wiring-guide/`](../../hardware/wiring-guide/README.md) |

---

## Entry index

| # | Date | Topic | Criterion |
| --- | --- | --- | --- |
| 01 | 2026-07-15 | System architecture: two-controller split (Pi + ESP32) | 3, 4 |
| 02 | 2026-07-18 | Chassis material and fabrication: 3 mm plywood + LightBurn | 1, 4 |
| 03 | 2026-07-22 | Drive system: N20 600 RPM motor, torque and speed reasoning | 1, 4 |
| 04 | 2026-07-27 | Steering geometry: Ackermann, 31° → 40° iteration | 1, 4 |
| 05 | 2026-08-02 | Double-stack layout: wood + LEGO + brass offsets | 1, 4 |
| 06 | 2026-08-05 | Motor driver: L298N → TB6612FNG (dropout and heat) | 2, 4 |
| 07 | 2026-08-07 | Power architecture: two-rail, two-battery design | 2, 4 |
| 08 | 2026-08-09 | Sensor selection: camera, HC-SR04, VL53L0X, MPU6050 | 2, 4 |
| 09 | 2026-08-11 | Software state machine and obstacle strategy | 3, 4 |
| 10 | 2026-08-12 | Risk register and failure-mode analysis | 4 |
| 11 | 2026-08-13 | Consolidated confirmed configuration (11 V 3S, rear tilt, LEGO Ackermann) | 1, 2, 4, 5 |

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

**Evidence:** the interface is defined in `src` protocol (`MODE_DRIVE`, `MODE_PARK`, `MODE_STOP`, `MODE_FINISH`, `MODE_FAULT`) and implemented in `software/esp32/obstacleChallenge.ino`.

**Next action:** harden the serial protocol with checksums.

---

### 02: Chassis material and fabrication (2026-07-18, by Dhrubo M.)

**Problem:** a rigid, light, cheaply-reproducible chassis that fits 300×200 mm and can be made with the school's tools.

**Options considered:**
- A) 3 mm acrylic, laser-cut.
- B) 3 mm plywood, laser-cut via **LightBurn** (school cutter).
- C) Fully 3D-printed frame.
- D) Aluminium sheet.

**Chosen: B, with C for brackets.** Plywood is lighter than acrylic of equal stiffness, damps motor vibration better, and cuts cleanly at speed on the school's laser cutter. Acrylic cracks at screw holes under servo load; plywood does not. The `.lbrn`/DXF source files are published so the chassis is fully reproducible. Small brackets and sensor mounts are 3D-printed (PLA) where complex geometry is needed (servo horn mount, camera mount).

**Tradeoff:** plywood absorbs moisture and can warp: mitigated by sealing edges with two thin coats of clear varnish and keeping the chassis in the transport case between sessions.

**Evidence:** LightBurn source files in the repo; cut parts photographed in `images/robot/`.

**Next action:** test a 2.4 mm plywood variant to compare stiffness-to-mass.

---

### 03: Drive system: N20 600 RPM motor (2026-07-22, by Vivaan K.)

**Problem:** choose a drive motor with enough speed to complete 3 laps inside 3 minutes and enough torque to accelerate a ~1.3 kg car reliably.

**Calculation (speed):** track centre-line lap ≈ 11–13 m ⇒ 3 laps ≈ 36–40 m. At a cruise of 0.55 m/s, 3 laps ≈ 66–72 s, leaving ~110 s of margin for corners and parking. N20 at 6 V free-runs at 600 RPM; with a ~40 mm wheel this is ≈ 1.2 m/s theoretical, so we operate comfortably mid-throttle.

**Calculation (torque):** N20 gearbox output torque is roughly 0.8–1.0 kg·cm at stall for this ratio. Rolling-resistance force for 1.3 kg ≈ 1.3–2.6 N; wheel radius 0.02 m ⇒ required torque ≈ 0.03–0.06 kg·cm. Stall torque exceeds requirement by >10×, so the limit is speed, not torque: correct for a flat, low-friction mat.

**Tradeoff:** higher-RPM variants (1000 RPM) would shorten lap time but worsen precision at stop lines and during parking. We prioritise **consistency** over peak speed, matching the rubric's "stability of mission solving".

**Chosen:** N20 6 V 600 RPM, one drive motor on the rear axle through the gearbox, in a mechanically coupled layout (compliant with WRO 2026 Rule 11.3/11.13: one driving axle; two motors are not used independently per side).

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

**Evidence:** steering sweep measurements and turn-radius logs captured during bench tests; geometry documented in `design/`.

**Next action:** add toe-in verification per side after every reassembly.

---

### 05: Double-stack layout: wood + LEGO + brass offsets (2026-08-02, by Yug J.)

**Problem:** fit two controllers, camera, four sensor families, servo, driver and batteries into 300×200 mm and keep the centre of mass low and the mass budget under 1.5 kg.

**Chosen: a two-deck chassis.**
- **Lower deck** (3 mm plywood): ESP32, TB6612FNG driver, batteries (lowest centre of mass).
- **Upper deck** (3 mm plywood): Raspberry Pi 4B + Camera Module 3 Wide, raised on brass standoff offsets.
- **Mounting fusion:** LEGO beams and pins are used as universal mounting rails (they provide precise, repeatable hole grids), brass standoff spacers set deck height, and the plywood decks are laser-cut. This "wood + LEGO + brass" system means a mount can be moved in 8 mm increments without re-cutting the chassis: very useful during sensor-placement iteration.

**Tradeoff:** the double stack raises the camera to a good horizon height (~120 mm) while the deck adds ~60 g. Placement was chosen to keep the combined centre of mass above the rear axle's roll centre.

**Next action:** measure the actual mass and CG; the chassis CAD is committed as `design/wooden_plate.dxf`.

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

**Problem:** a single shared battery caused motor transients to brown out the Pi during bench tests (servo stall + motor start together).

**Chosen: two separate supplies, per WRO Appendix D guidance.**
- **Motor rail:** 2S LiPo (7.4 V) → TB6612FNG → N20 motor and MG996R servo.
- **Logic rail:** separate battery pack → regulated 5 V rail → Raspberry Pi 4B, ESP32, HC-SR04, VL53L0X, MPU6050.
- Star grounding: all logic grounds meet at a single point; motor ground returns separately to its pack negative, keeping servo/motor currents out of the logic reference.
- Decoupling: 0.1 µF ceramic on every IC VCC; 100 µF electrolytic on the 5 V rail.

**Power budget (estimated, to be verified):** Pi 4B ~0.6 A avg; ESP32 ~0.1 A; sensors ~0.05 A; servo ~0.3 A avg (1.2 A peak); N20 ~0.5 A avg (1.5 A stall). Total logic rail ≈ 0.8 A, motor rail ≈ 0.8 A avg / 2.7 A peak. Both rails fused.

**Failure consideration:** if the logic rail browns out, the ESP32's `MODE_FAULT` logic stops the vehicle rather than letting it run uncontrolled.

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

**Calibration:** camera exposure locked; HSV bounds auto-tuned at boot against the first frames. MPU6050 zero-bias captured for 2 s at start. ToF readings median-filtered (5 samples).

**Next action:** add I²C bus test + VL53L0X address-shift to avoid conflicts with the IMU.

---

### 09: Software state machine and obstacle strategy (2026-08-11, by Vivaan K. & Dhrubo M.)

**Problem:** structure the software so behaviour is predictable and judges can read the design.

**Chosen: two-layer state machine.**

*Raspberry Pi layer (perception + decision)*: `software/raspberry_pi/wromain.py`:
- Camera frames → 3×3 colour grid → per-cell colour masks (red/green/blue/orange/purple) → contour detection → target selection → centering error → **PD steering** (proportional + derivative on lateral offset) → dynamic drive speed.
- PD (rather than full PID) is used deliberately: the field has no sustained steady-state error that requires the integral term, and D-only damping prevents oscillation at corners without windup.

*ESP32 layer (execution + safety)*: `software/esp32/obstacleChallenge.ino`:
- Modes `MODE_DRIVE`, `MODE_PARK`, `MODE_STOP`, `MODE_FINISH`, `MODE_FAULT`, driven over a 115200-baud serial protocol. Fault mode is entered on serial timeout or invalid command: the vehicle always fails safe.

**Obstacle strategy (Obstacle Challenge):**
1. Lane-follow by centring on the corridor (PD steering on vision offset, wall-distance check via VL53L0X).
2. Pillar handling: red pillar → pass on its **right**; green pillar → pass on its **left** (colour from camera grid). The car biases the centring target toward the correct side and verifies clearance with the ToF before re-centring.
3. After 3 laps → `MODE_PARK`: detect magenta parking-limit blocks with the camera, align parallel using the IMU heading, and use the ToF to stop at the correct depth inside the 20 cm-wide lot.
4. Open Challenge: corner detection from wall geometry + lap counting by crossing section lines (orange/blue), then autonomous stop in the finish section.

**Edge cases handled:** lost line (re-acquire by sweeping), serial timeout (fault stop), pillar too close (emergency bias), parking overshoot (back up in small IMU-controlled steps).

**Testing/tuning method:** per-lap intervention count is logged; the PD gains were tuned to minimise interventions (see `other/pid_tuning_log.md`).

**Next action:** complete orange/blue line following and lap counting (tracked in the code header's "not yet implemented" list).

---

### 10: Risk register and failure-mode analysis (2026-08-12, by the team)

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Camera glare / lighting change | Medium | High | exposure lock + boot-time HSV recalibration; tested under fluorescent + spot lighting |
| Battery sag under servo+motor peak | Medium | High | two-rail power; fused rails; LiPo packs with adequate C rating |
| Wall collision in 600 mm corridor | Medium | High | 40° steering, speed reduction near walls (proximity-driven speed), ToF wall check |
| Serial dropout Pi↔ESP32 | Low | High | fault state + re-sync on checksum failure; USB cable strain-relieved |
| ToF misread on white mat at shallow angle | Medium | Medium | 5-sample median filter; mount at 15° downward |
| Wheel slip during parking | Medium | Medium | low speed, IMU heading feedback, short move steps |
| Sudden rule change (surprise rule, Day 2) | Medium | Medium | modular code: strategy params in one config file; reserve a config slot per round |

---

### 11: Consolidated confirmed configuration (2026-08-13, by Dhrubo M.)

**Context:** this entry records the final, confirmed mechanical + power configuration after the build stabilised, and supersedes the 7.4 V figure quoted in Entry 07.

**Confirmed configuration:**
- **Structure:** laser-cut 3 mm plywood double-stack chassis (LightBurn source → `design/wooden_plate.dxf`), brass standoff offsets between decks, LEGO beams/pins as adjustable mounting + steering rails.
- **Decks:** upper deck = Raspberry Pi 4B + Camera Module 3 Wide; lower deck = 11 V 3S LiPo pack + ESP32 + TB6612FNG.
- **Drive:** fully rear-wheel drive, one N20 6 V 600 RPM motor on the rear axle (Rule 11.3/11.13 compliant: one driving axle, no independent side motors). Rear wheels and the rear N20 are smaller than the front wheels, giving the chassis a slight rearward tilt.
- **Steering:** front TowerPro MG996R servo driving an Ackermann linkage built from LEGO beams/pins; outer lock 40° (Entry 04).
- **Sensing:** Pi Camera Module 3 Wide (colour/geometry), VL53L0X ToF (front distance), HC-SR04 (redundant wall proximity), DFRobot Fermion MPU6050 IMU (yaw).
- **Power:** single 11 V 3S LiPo → motor/servo rail bucked to ~6–7.4 V for N20 + MG996R; logic rail bucked to 5 V for Pi/ESP32/sensors (two-rail, star-grounded, fused).

**Why this is the final form:** every choice above is the result of the iterations logged in Entries 01–10 (two-controller split, plywood + LightBurn, N20 rear drive, 31°→40° Ackermann, L298N→TB6612FNG, two-rail power, sensor set). The smaller rear wheels + rearward tilt were adopted to lower the drive mass and improve corner stability without adding weight.

**Evidence:** chassis DXF and wiring guide committed in the repository; physical build and measured values to be added to `docs/testing/README.md` and `evidence/README.md` as on-mat testing proceeds.

**Next action:** complete on-mat integration tests (T3–T10) and record measured rail currents and lap times.

---

## Process note

Entries are added as the design is developed and tested. Each entry lists what was considered, what was chosen, why, and what evidence exists. The repository is the living engineering record; the journal, testing records, and evidence archive together show the iteration cycle the rubric asks for.
