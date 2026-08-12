# Power Budget

Estimated current draw per subsystem at **nominal operating point**. Source: datasheet values and lab measurements. Update measured columns as real readings are logged (see `test_log.csv`).

## 1. Estimated totals

| Subsystem | Voltage | Est. current (avg) | Est. current (peak) | Notes |
|---|---|---|---|---|
| Raspberry Pi 4B | 5 V | 0.6 A | 1.2 A | Boot peak higher; use 5 V/3 A rail |
| Pi Camera Module 3 Wide | 3.3 V | 0.25 A | 0.3 A | CSI-supplied |
| ESP32 DevKit C | 5 V | 0.08 A | 0.4 A | WiFi/BT disabled (rule 11.10) |
| BNO055 IMU | 3.3 V | 0.012 A | 0.012 A | I2C |
| VL53L1X ToF ×4 | 3.3 V | 0.02 A each | 0.04 A each | I2C via TCA9548A |
| TCS34725 | 3.3 V | 0.0003 A | 0.0003 A | I2C |
| MG996R steering servo | 5 V | 0.3 A | 1.2 A | Stall 2.5 A — spike at turn onset |
| JG25-370 drive motor | 7.4 V | 0.5 A | 3.0 A | Stall at ~3 A, limited by current fuse |
| **Total logic rail (5 V)** | 5 V | **~1.26 A** | **~3.1 A** | Fuse: 5 A |
| **Total motor rail (2S)** | 7.4 V | **~0.5 A** | **~3.0 A** | Fuse: 5 A |

## 2. Design rules

1. **Two separate batteries** (Appendix D): one for logic (Pi + ESP32 + sensors), one for motors. Motor transients must never sag the Pi rail.
2. **Fuse every rail**: 5 A logic, 5 A motor. A stalled motor must trip the fuse, never brown out the Pi.
3. **Grounding**: star ground — all logic grounds meet at one point on the battery side; motor ground runs separately to the driver. See `schemes/wiring-guide/README.md`.
4. **Decoupling**: 0.1 µF ceramic on every IC VCC; 10 µF electrolytic on the 5 V rail and on the motor driver VM pin.
5. **Servo peak handling**: servo + Pi simultaneously on one 5 V rail can exceed 4 A — use the 5 V/5 A UBEC for the Pi+servo group, or a separate UBEC for the servo.

## 3. Runtime estimate

| Battery | Capacity | Rail load | Est. runtime |
|---|---|---|---|
| 2S 1300 mAh (motor) | 1.3 Ah @7.4 V | ~0.5 A avg | > 2 h of practice runs |
| 3S 1000 mAh (logic) | 1.0 Ah @11.1 V | ~1.3 A @5 V ≈ 0.6 A @11 V | > 1.5 h continuous |

Three-minute rounds are far inside battery limits; the constraint is peak current, not capacity.

## 4. Weight budget (total ≤ 1.5 kg per rule 11.2)

| Group | Est. mass |
|---|---|
| Chassis (acrylic + 3D prints + fasteners) | 280 g |
| Drive motor + gearbox + axle + wheels | 260 g |
| Steering servo + linkage | 65 g |
| Raspberry Pi + camera + SD | 60 g |
| ESP32 + sensors + wiring | 60 g |
| Batteries ×2 | 160 g |
| UBECs + fuses + connectors | 40 g |
| **Total** | **~925 g** (margin ~575 g) |
