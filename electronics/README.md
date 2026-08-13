<div align="center">

# Electronics

**Pin assignments and basic power-distribution reference for the WRO Future Engineers vehicle.**


[← Project home](../README.md) · [Hardware](../hardware/README.md) · [Wiring Guide](../hardware/wiring-guide/README.md) · [Diagrams](../docs/diagrams/README.md)

</div>

---

## Pinout

### ESP32

| Component | Function | ESP32 Pin |
| --- | --- | ---: |
| MG996R | Steering signal | GPIO 13 |
| TB6612FNG | PWMA | GPIO 25 |
| TB6612FNG | AIN1 | GPIO 26 |
| TB6612FNG | AIN2 | GPIO 27 |
| TB6612FNG | STBY | GPIO 32 |
| Green LED | Status | GPIO 2 |
| Red LED | Status | GPIO 4 |

The ESP32 controls the low-level actuators. The vehicle uses one N20 motor through the TB6612FNG.

### Raspberry Pi 4B

| Component | Connection / Interface | Purpose |
| --- | --- | --- |
| Pi Camera 3 Wide | Camera interface | Visual perception |
| ESP32 | USB | Control communication |
| 6-axis IMU | Sensor interface | Motion sensing |
| ToF sensor | Sensor interface | Distance sensing |

The exact IMU and ToF pin assignments will be added after the final physical modules and connections are confirmed.

---

> [!NOTE]
> This folder defines the submitted electronics and power configuration. Wiring evidence is tracked in the hardware area. The vehicle is in the development and integration phase; estimated / design target values will be confirmed and recorded as subsystems are verified during integration.

## 1. Bill of materials

| # | Part | Qty | Role | Status |
| --- | --- | --- | --- | --- |
| 1 | Raspberry Pi 4B | 1 | Vision, decision, high-level control | Owned |
| 2 | Raspberry Pi Camera Module 3 **Wide** | 1 | Colour + geometry perception (pillars, lines, blocks) | Owned |
| 3 | ESP32 (DevKit) | 1 | Real-time motor/servo control, safety state machine | Owned |
| 4 | Dual Motor Driver Module **TB6612FNG** (1 A) | 1 | Drive motor H-bridge (replaces L298N) | Owned |
| 5 | **N20 6 V 600 RPM** Micro Metal Gear Motor | 1 + spare | Rear-axle drive | Owned |
| 6 | **TowerPro MG996R** Digital High Torque Servo | 1 + spare | Ackermann steering | Owned |
| 7 | **DFRobot Fermion MPU6050** 6-Axis Breakout | 1 | IMU: yaw for corners, parking alignment | Owned |
| 8 | **VL53L0X** ToF Laser Distance Sensor | 1 | Front distance: pillars, parking gap | Owned |
| 9 | HC-SR04 ultrasonic | 1 | Redundant wall/obstacle proximity | Owned |
| 10 | 11 V 3S LiPo pack (single pack feeding both rails; motor/servo rail buck-regulated to ~6 V, logic rail buck-regulated to 5 V) | 1 | Two-rail power from one pack (WRO Appendix D guidance) | Owned |
| 11 | 5 V regulator / buck | 2 | Logic rail regulation | Owned |
| 12 | MG996R servo horn + Ackermann links (3D-printed) | 1 set | Steering linkage | Printed |
| 13 | 3 mm plywood decks (LightBurn-cut) + brass standoffs | 1 set | Chassis (see [design](../design/README.md)) | Cut |

**Design rationale for key parts** is documented in the [engineering journal](../docs/engineering_journal/README.md): entries 03 (motor), 04 (steering), 06 (TB6612FNG over L298N), 07 (power), 08 (sensors).

## 2. Power architecture (two-rail from one 11V 3S pack)

| Rail | Source | Consumers | Protection |
| --- | --- | --- | --- |
| Motor/servo rail | 11 V 3S LiPo pack → buck-regulated to ~6 V (within N20 6V and MG996R 4.8-7.2V ratings) | N20 motor, MG996R servo | 2 A fuse |
| Logic rail | 11 V pack → 5 V buck regulator | Pi 4B, ESP32, HC-SR04, VL53L0X, MPU6050 | 2 A fuse |

- **Star grounding:** all logic grounds meet at one point; motor ground returns separately to its pack negative. Motor/servo currents never flow through the logic reference.
- **Decoupling:** 0.1 µF ceramic on every IC VCC; 100 µF electrolytic on the 5 V rail.
- **Failure handling:** logic-rail brownout → ESP32 enters `MODE_FAULT` and stops the vehicle.
- The logic rail is produced by a **5 V buck regulator** from the 11 V pack (an earlier LM317 concept, R1 = 240 Ω / R2 = 720 Ω with 0.1 µF input / 10 µF output decoupling, was dropped because the 11 V input would make the linear regulator run hot). Final regulation, current capability, and thermal performance will be verified once the physical power system is assembled.

### Power budget (estimated / design target; to be measured during integration)

All figures below are estimates, not measured values.

| Load | Rail | Avg (estimated) | Peak (estimated) |
| --- | --- | --- | --- |
| Raspberry Pi 4B | Logic 5 V | 0.6 A | 1.2 A |
| ESP32 | Logic 5 V | 0.12 A | 0.2 A |
| Sensors (HC-SR04, VL53L0X, MPU6050) | Logic 5 V | 0.03 A | 0.1 A |
| MG996R servo | Motor/servo ~6 V | 0.3 A | 1.2 A |
| N20 motor | Motor/servo ~6 V | 0.5 A | 1.5 A |
| **Logic rail total (estimated)** | 5 V | ~0.75 A | ~1.5 A |
| **Motor rail total (estimated)** | ~6 V | ~0.8 A | ~2.7 A |

Estimated / design target values will be confirmed and recorded during integration as each rail is measured.

### Two-rail, single-pack confirmation

Both rails are derived from the SAME single 11 V 3S LiPo pack. The pack feeds two independent buck regulators: one to the ~6 V motor/servo rail and one to the 5 V logic rail. This satisfies the WRO requirement of a single on-board power source while keeping high-current actuator loads electrically separated from sensitive logic, with star grounding and per-rail fuses.

### Sensor rationale

- **VL53L0X (primary distance):** laser time-of-flight giving millimetre-accurate, colour-independent ranging, so it is the main sensor for pillars, walls and parking gaps. Limitation: glass and very dark (black) surfaces can absorb or let the laser pass, returning unreliable readings, so we use a slight downward tilt and median filtering.
- **HC-SR04 (redundant distance):** ultrasonic proximity on an independent GPIO/trig-echo bus, used as a cross-check and fallback if the ToF reading is lost. It is less precise and affected by soft or angled surfaces, but its independence from the I2C bus adds fault tolerance.
- **MPU6050 (orientation):** 6-axis IMU providing heading and tilt for turning and parking alignment, used for yaw integration to confirm turn completion and parking squareness.

Exact module pin assignments (I2C addresses and GPIO/trig-echo wiring) will be finalised after the physical sensor modules are confirmed.

> [!WARNING]
> The 11 V 3S LiPo stores high energy. Balance-charge before every run, never exceed the N20 (6 V) and MG996R (4.8 to 7.2 V) rated voltages after regulation, and fit a fuse on each rail.

## 3. Interface plan (summary: full pin map in wiring guide)

| Interface | Path | Notes |
| --- | --- | --- |
| Vision | Pi ↔ Camera Module 3 Wide | CSI |
| Control link | Pi ↔ ESP32 | USB serial 115200, `CMD,<steer>,<pwm>,<mode>` with `<mode>` ∈ {`DRIVE`, `PARK`, `FINISH`, `STOP`} + bare `STOP`/`PING`; firmware internal states `MODE_DRIVE`…`MODE_FAULT` |
| Drive | ESP32 ↔ TB6612FNG ↔ N20 | PWM + direction |
| Steering | ESP32 ↔ MG996R | PWM servo |
| Distance | ESP32 ↔ VL53L0X (I²C), HC-SR04 (GPIO) | Median-filtered |
| Orientation | ESP32 ↔ MPU6050 (I²C) | Yaw integration |

## 4. Calibration plan

- Camera: exposure locked; HSV bounds auto-tuned at boot from first frames.
- MPU6050: zero-bias captured over 2 s at start.
- VL53L0X: 5-sample median filter; mounted at ~15° downward to avoid shallow-angle white-mat misreads.
- Servo: steering range re-verified after every reassembly (see design entry on 31°/40°).
