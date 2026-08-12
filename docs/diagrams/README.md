````markdown
<div align="center">

# Wiring Guide

**Physical wiring, power distribution, pin assignments, and component interconnections.**

[← Project home](../../README.md) · [Hardware](../README.md) · [Electronics](../../electronics/README.md) · [Diagrams](../../docs/diagrams/README.md)

</div>

---

The `hardware/wiring-guide/` directory contains the physical electrical reference for the WRO Future Engineers vehicle.

It documents the intended connections between the Raspberry Pi 4B, Pi Camera 3 Wide, ESP32, IMU, ToF sensor, MG996R steering servo, TB6612FNG motor driver, and N20 drive motor.

The final wiring configuration will be verified and updated against the assembled robot.

## System Overview

```text
Pi Camera 3 Wide
       ↓
Raspberry Pi 4B
       │
       │ USB Serial
       ↓
     ESP32
    /     \
MG996R   TB6612FNG
           ↓
      N20 6V 600RPM
````

The Raspberry Pi handles high-level perception and navigation. The ESP32 handles low-level actuator control.

## Hardware Configuration

| Component        | Function                 |
| ---------------- | ------------------------ |
| Raspberry Pi 4B  | High-level computation   |
| Pi Camera 3 Wide | Visual perception        |
| ESP32            | Low-level control        |
| 6-axis IMU       | Motion sensing           |
| ToF sensor       | Distance sensing         |
| MG996R           | Front steering           |
| TB6612FNG        | DC motor driver          |
| N20              | 6 V, 600 RPM drive motor |

The vehicle uses **one N20 motor** for the rear drivetrain rather than independent left and right drive motors.

## ESP32 Pinout

### Steering

```text
MG996R signal → GPIO 13
```

The servo power is supplied through the appropriate power rail; GPIO 13 provides the control signal only.

### TB6612FNG

```text
PWMA  → GPIO 25
AIN1  → GPIO 26
AIN2  → GPIO 27
STBY  → GPIO 32
```

The TB6612FNG drives the single N20 motor.

### Status LEDs

```text
Green LED → GPIO 2
Red LED   → GPIO 4
```

## Raspberry Pi and Camera

The Pi Camera 3 Wide connects directly to the Raspberry Pi 4B camera interface.

It is used for:

* track perception;
* colour-grid processing;
* red and green pillar detection;
* orange and blue line detection;
* visual positioning.

The camera's final physical mounting position will be documented with the completed sensor-layout diagram.

## Raspberry Pi ↔ ESP32 Communication

The Raspberry Pi and ESP32 communicate through **USB serial** at:

```text
115200 baud
```

The Pi sends actuator commands to the ESP32.

Example:

```text
CMD,-15.50,140,DRIVE
```

Additional commands include:

```text
STOP
PING
```

The ESP32 includes a communication watchdog so that loss of valid commands results in a motor stop and steering-centre response.

## Sensor Connections

The final wiring record will document the physical connections and placement of:

* **6-axis IMU**
* **ToF distance sensor**

The exact pinout and interface of these sensors will be recorded once the final physical modules and connections are confirmed.

The IMU is intended for motion and yaw-rate information, while the ToF sensor provides direct distance measurements to complement camera-based perception.

## Power Architecture

The final wiring documentation will record:

* battery / input supply;
* regulated rails;
* Raspberry Pi supply;
* ESP32 supply;
* motor supply;
* servo supply;
* sensor supply;
* grounding arrangement;
* decoupling;
* motor-noise considerations.

The N20 is a **6 V, 600 RPM motor**, so the final motor supply must be compatible with its specification and must not simply be assumed to be the same as the logic rail.

The existing design record includes an LM317-based 5 V regulation concept using:

```text
R1 = 240 Ω
R2 = 720 Ω
```

with:

```text
0.1 µF input decoupling
10 µF output decoupling
```

This remains part of the design record until the final physical power architecture is verified.

## Grounding and Cable Routing

The final wiring should use a controlled common-ground arrangement.

High-current motor and servo returns should be routed so that they do not unnecessarily share sensitive sensor or logic paths.

Cable routing should prevent interference with:

* steering;
* wheels;
* drivetrain;
* moving mechanical parts.

Motor and sensor signal wiring should be separated where practical.

## Verification

The electrical system will be brought online progressively:

```text
Power
  ↓
ESP32
  ↓
Steering
  ↓
Motor
  ↓
Sensors
  ↓
Pi ↔ ESP32 communication
  ↓
Complete system
```

Initial actuator tests should be performed with the drive wheels lifted from the surface.

Before final operation, the following should be verified:

* power polarity;
* regulator output;
* motor-supply voltage;
* servo supply;
* ESP32 pin assignments;
* TB6612FNG connections;
* sensor connections;
* USB communication;
* mechanical cable clearance;
* communication-loss failsafe.

## Reproducibility

The completed wiring package will include the final wiring diagram, pinout, power-distribution information, sensor connections, photographs, and verification records.

Any hardware change must be reflected consistently in:

```text
Wiring
   ↓
Pinout
   ↓
Firmware
   ↓
Pi software
   ↓
Diagrams
   ↓
Engineering journal
```

This README is the **physical wiring reference**. Visual architecture diagrams are maintained separately in `docs/diagrams/`, while electrical component reasoning is maintained in `electronics/`.

```
```
