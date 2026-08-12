<div align="center">

# Hardware

**Physical vehicle integration, hardware configuration, and assembly reference.**

[← Project home](../README.md) · [Electronics](../electronics/README.md) · [Wiring Guide](wiring-guide/README.md) · [Design](../design/README.md)

</div>

---

The `hardware/` directory contains the physical hardware configuration and vehicle-integration information for the WRO Future Engineers robot.

The current intended system uses a Raspberry Pi 4B for high-level computation, an ESP32 for low-level actuator control, a Pi Camera 3 Wide for visual perception, a 6-axis MPU6050 IMU, a VL53L0X ToF sensor, an HC-SR04 ultrasonic sensor, an MG996R steering servo, a TB6612FNG motor driver, and one N20 6 V 600 RPM drive motor.

## Hardware Configuration

| Component | Function |
| --- | --- |
| Raspberry Pi 4B | High-level computation and navigation |
| Pi Camera 3 Wide | Visual perception |
| ESP32 | Low-level actuator control |
| MPU6050 | 6-axis motion sensing |
| VL53L0X | Time-of-flight distance sensing |
| HC-SR04 | Redundant proximity sensing |
| MG996R | Front Ackermann steering |
| TB6612FNG | Drive-motor controller |
| N20 6 V 600 RPM | Rear drivetrain |

The vehicle uses **one N20 motor** for the rear drivetrain.

## Physical Integration

The robot combines front Ackermann steering with a single rear drive motor. The mechanical structure uses 3 mm plywood, LightBurn-cut components, LEGO elements, and brass standoffs/offsets as documented in the design records.

Detailed mechanical decisions, fabrication files, dimensions, and design iterations are maintained in [`design/`](../design/).

## Wiring

The complete physical connection reference is maintained in [`wiring-guide/`](wiring-guide/).

This includes:

- ESP32 pin assignments;
- motor-driver connections;
- steering connections;
- power-distribution information;
- sensor interfaces;
- grounding;
- communication wiring.

## Electronics

The electrical component and power reference is maintained in [`electronics/`](../electronics/).

## Evidence

Physical photographs and measurements added to this directory should represent the actual vehicle and identify the relevant date/configuration.

Concept renders and planned configurations must not be presented as physical verification.

## Status

The hardware documentation represents the intended vehicle configuration and will be updated as the physical robot is assembled, wired, tested, and refined.