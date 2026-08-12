<div align="center">

# Electronics

**Pin assignments and basic power-distribution reference for the WRO Future Engineers vehicle.**

![WRO](https://img.shields.io/badge/WRO-2026-0057B8?style=for-the-badge&logo=robotframework&logoColor=white)
![Category](https://img.shields.io/badge/Category-Future%20Engineers-7A2E8E?style=for-the-badge)
![Power](https://img.shields.io/badge/Power-11V%203S%20LiPo-0B7A3B?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Development%20Phase-F59E0B?style=for-the-badge)
![Updated](https://img.shields.io/badge/Updated-2026--08--13-555555?style=for-the-badge)

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
> This folder defines the submitted electronics and power configuration. Wiring evidence is tracked in the hardware area. The vehicle is in the development and integration phase; measured values will be added as subsystems are verified.

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
| 10 | 11 V 3S LiPo pack (motor/servo rail regulated to ~6–7.4 V; logic rail regulated to 5 V) | 1 | Two-rail power from one pack (WRO Appendix D guidance) | Owned |
| 11 | 5 V regulator / buck | 2 | Logic rail regulation | Owned |
| 12 | MG996R servo horn + Ackermann links (3D-printed) | 1 set | Steering linkage | Printed |
| 13 | 3 mm plywood decks (LightBurn-cut) + brass standoffs | 1 set | Chassis (see [design](../design/README.md)) | Cut |

**Design rationale for key parts** is documented in the [engineering journal](../docs/engineering_journal/README.md): entries 03 (motor), 04 (steering), 06 (TB6612FNG over L298N), 07 (power), 08 (sensors).

## 2. Power architecture (two-rail, two-battery)

| Rail | Source | Consumers | Protection |
| --- | --- | --- | --- |
| Motor/servo rail | 11 V 3S LiPo pack → buck-regulated to ~6–7.4 V | N20 motor, MG996R servo | 2 A fuse |
| Logic rail | 11 V pack → 5 V buck regulator | Pi 4B, ESP32, HC-SR04, VL53L0X, MPU6050 | 2 A fuse |

- **Star grounding:** all logic grounds meet at one point; motor ground returns separately to its pack negative. Motor/servo currents never flow through the logic reference.
- **Decoupling:** 0.1 µF ceramic on every IC VCC; 100 µF electrolytic on the 5 V rail.
- **Failure handling:** logic-rail brownout → ESP32 enters `MODE_FAULT` and stops the vehicle.
- The logic rail is produced by a **5 V buck regulator** from the 11 V pack (an earlier LM317 concept, R1 = 240 Ω / R2 = 720 Ω with 0.1 µF input / 10 µF output decoupling, was dropped because the 11 V input would make the linear regulator run hot). Final regulation, current capability, and thermal performance will be verified once the physical power system is assembled.

### Power budget (estimated, to be measured)

| Load | Avg | Peak |
| --- | --- | --- |
| Raspberry Pi 4B | 0.6 A | 1.2 A |
| ESP32 + sensors | 0.15 A | 0.3 A |
| MG996R servo | 0.3 A | 1.2 A |
| N20 motor | 0.5 A | 1.5 A |
| **Logic rail total** | ~0.8 A | ~1.6 A |
| **Motor rail total** | ~0.8 A | ~2.7 A |

Measured values will be recorded in the testing records as each rail is verified.

> [!WARNING]
> The 11 V 3S LiPo stores high energy. Balance-charge before every run, never exceed the N20 (6 V) and MG996R (4.8 to 7.2 V) rated voltages after regulation, and fit a fuse on each rail.

## 3. Interface plan (summary: full pin map in wiring guide)

| Interface | Path | Notes |
| --- | --- | --- |
| Vision | Pi ↔ Camera Module 3 Wide | CSI |
| Control link | Pi ↔ ESP32 | USB serial 115200, `MODE_DRIVE/PARK/STOP/FINISH/FAULT` |
| Drive | ESP32 ↔ TB6612FNG ↔ N20 | PWM + direction |
| Steering | ESP32 ↔ MG996R | PWM servo |
| Distance | ESP32 ↔ VL53L0X (I²C), HC-SR04 (GPIO) | Median-filtered |
| Orientation | ESP32 ↔ MPU6050 (I²C) | Yaw integration |

## 4. Calibration plan

- Camera: exposure locked; HSV bounds auto-tuned at boot from first frames.
- MPU6050: zero-bias captured over 2 s at start.
- VL53L0X: 5-sample median filter; mounted at ~15° downward to avoid shallow-angle white-mat misreads.
- Servo: steering range re-verified after every reassembly (see design entry on 31°/40°).
