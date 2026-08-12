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

## Power Distribution

The electrical system separates the computing/control electronics from the higher-current actuator loads.

```text
Power Source
    │
    ├── Logic / Compute
    │      ├── Raspberry Pi 4B
    │      └── ESP32
    │
    ├── Sensors
    │      ├── PiCam3
    │      ├── IMU
    │      └── ToF
    │
    ├── Motor Driver
    │      └── TB6612FNG
    │               └── N20 6V 600RPM
    │
    └── Steering
           └── MG996R

The N20 is a **6 V, 600 RPM** motor, so its final supply must be appropriate for the motor rather than being assumed to share the logic rail.

The current design also includes an **LM317-based 5 V regulation concept**. Its final implementation, input supply, current capability, and thermal performance will be verified once the physical power system is assembled.

All subsystems sharing signal connections should use an appropriate common ground, while high-current motor and servo paths should be kept separate from sensitive signal paths where practical.

```
```
