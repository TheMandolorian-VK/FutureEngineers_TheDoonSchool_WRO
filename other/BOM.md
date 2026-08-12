# Bill of Materials (BOM)

Living component list for the WRO 2026 Future Engineers vehicle. Update the **Status** column as parts are ordered, received, and mounted.

> **Compliance note (WRO 2026 Rule 11):** the vehicle must be a 4-wheeled car with **one driving axle** and **one steering actuator**. Differential drive (one motor per side) and omnidirectional wheels are disqualified. This BOM reflects the compliant Ackermann-style layout: one drive motor + one steering servo.

## 1. Competition robot (mounted)

| # | Part | Qty | Role | Status |
|---|------|-----|------|--------|
| 1 | Raspberry Pi 4B / 5 | 1 | High-level vision + decisions (OpenCV) | Ordered |
| 2 | Pi Camera Module 3 **Wide** | 1 | Sees red/green pillars, orange/blue lines, magenta parking blocks | Ordered |
| 3 | 64 GB high-endurance microSD | 2 | OS + backup image | Ordered |
| 4 | ESP32 DevKit C | 1 | Low-level motor/servo/sensor loop | Owned |
| 5 | JG25-370 gear motor 12 V ~300 RPM + Hall encoder | 1 | Single rear-axle drive motor | Ordered |
| 6 | 5 mm axle, flanged bearings, coupling | 1 set | Solid rear drive axle (live axle) | Ordered |
| 7 | MG996R metal-gear servo + horn | 1 | Front Ackermann steering | Ordered |
| 8 | 65–70 mm rubber wheels | 4 | Traction on mat | Ordered |
| 9 | Cytron MDD10A (10 A) motor driver | 1 | Drive motor PWM/direction | Ordered |
| 10 | VL53L1X ToF distance sensors | 4 | Wall distance (L/R), obstacle, parking gap | Ordered |
| 11 | TCA9548A I2C multiplexer | 1 | Four ToF sensors on one bus | Ordered |
| 12 | BNO055 9-axis IMU | 1 | Heading for turns + parking alignment | Ordered |
| 13 | TCS34725 RGB color sensor | 1 | Downward orange/blue line detection | Ordered |
| 14 | HC-SR04 ultrasonic | 1 | Redundant short-range wall check | Owned |
| 15 | Push button (start) + rocker switch (power) | 2 | Rules: exactly ONE start button, ONE power switch | Ordered |
| 16 | Buzzer + status LEDs | 1 set | Start / section / failure audio feedback | Owned |
| 17 | Laser-cut acrylic Ackermann chassis + 3D-printed mounts | 1 | Structure (CAD in `models/`) | In progress |

## 2. Power system

| # | Part | Qty | Role | Status |
|---|------|-----|------|--------|
| 1 | 2S 1300 mAh 30–50C LiPo | 2 | Motor supply (one spare) | Ordered |
| 2 | 3S 1000 mAh LiPo | 2 | Logic supply: Pi + ESP32 + sensors | Ordered |
| 3 | UBEC 5 V / 5 A | 2 | Pi power rail (needs stable 5 V / 3 A) | Ordered |
| 4 | UBEC 5 V / 3 A + adjustable buck 5 A | 2 | ESP32 + sensor rails | Ordered |
| 5 | XT60 + JST-XH + fuses (3/5/10 A) + switches | 1 set | Distribution + protection | Ordered |
| 6 | iMAX B6 charger + balance board + LiPo safe bag | 1 | Charging + safety | Ordered |

## 3. Practice field (school lab)

| # | Part | Qty | Role | Status |
|---|------|-----|------|--------|
| 1 | 3×3 m white mat / MDF boards | 1 | Track floor (matches rules 13.1–13.2) | Pending |
| 2 | Black foam-board strips, 100 mm tall | ~40 m | Exterior + interior walls (rules 13.3–13.6) | Pending |
| 3 | 20 mm orange + blue tape | 2 rolls | Corner/line markers (rule 13.9) | Pending |
| 4 | Red + green pillars (3D-printed) | 6 | Traffic signs (rules 13.19+) | In progress |
| 5 | Magenta blocks 200×20×100 mm | 2 | Parking lot limits (rule 13.25) | Pending |

## 4. Tools, spares, transport

Multimeter · soldering iron + solder · heat-shrink · Dupont + silicone wire kit · M2/M3 screw/standoff kit · zip ties · double-sided tape · spare motor ×1 · spare servo ×1 · spare driver ×1 · spare ESP32 ×1 · spare SD card ×1 · foam-lined transport case · offline copies of all libraries and Python wheels.

> **Rule 11.21:** teams must bring enough spare parts. **Rule 11.26:** only one vehicle is allowed in the competition area — spares, not a second robot.
