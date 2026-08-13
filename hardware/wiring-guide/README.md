<div align="center">

# Wiring Guide

**Physical wiring, power distribution, pin assignments, and component interconnections for the WRO Future Engineers vehicle.**

[← Project home](../../README.md) · [Hardware](../README.md) · [Electronics](../../electronics/README.md) · [Diagrams](../../docs/diagrams/README.md)

</div>

---

The `hardware/wiring-guide/` directory contains the physical wiring reference for the robot.

Unlike `docs/diagrams/`, which explains the overall architecture visually, this document focuses on **what connects to what, which pins are used, how power is distributed, and how the final electrical system is verified**.

The wiring configuration will be updated as the physical robot is assembled and tested.

## Hardware

| Component | Function |
| --- | --- |
| Raspberry Pi 4B | High-level computation and navigation |
| Pi Camera 3 Wide | Visual perception |
| ESP32 | Low-level actuator control |
| 6-axis IMU | Motion sensing |
| ToF sensor | Distance sensing |
| MG996R | Front steering |
| TB6612FNG | Motor driver |
| N20 | 6 V, 600 RPM drive motor |

The drivetrain uses **one N20 motor**, mechanically connected to the rear drive wheels.

## Controller Architecture

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
The Raspberry Pi handles perception and navigation.

The ESP32 handles low-level steering, motor control, and communication safety.

## ESP32 Pinout

### MG996R Steering

```text
MG996R signal → GPIO 13
```

GPIO 13 is the steering control signal. The servo receives power through the appropriate supply rail rather than from the GPIO.

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

The Pi Camera 3 Wide connects to the Raspberry Pi 4B camera interface.

The camera provides the primary visual input for:

* the 3×3 colour-grid system;
* orange and blue line detection;
* red and green pillar detection;
* visual positioning;
* navigation.

The final camera position and mounting will be recorded after physical assembly.

## Pi ↔ ESP32 Communication

The Raspberry Pi and ESP32 communicate through **USB serial**.

```text
Raspberry Pi 4B
      │
      │ USB
      ▼
    ESP32
```

The current communication speed is:

```text
115200 baud
```

Commands use the format:

```text
CMD,<steering_deg>,<motor_pwm>,<mode>
```

Example:

```text
CMD,-15.50,140,DRIVE
```

Additional commands:

```text
STOP
PING
```

The ESP32 includes a communication watchdog. If valid commands stop arriving, the motor is stopped and the steering is centred.

## Sensor Connections

The vehicle includes a:

* **6-axis IMU** for motion and rotational information;
* **ToF sensor** for direct distance measurement.

The final sensor wiring will record:

* supply;
* ground;
* communication interface;
* signal pins;
* physical mounting position.

The exact pin assignments will be added once the final sensor modules and connections are confirmed.

## Power Distribution

The final wiring documentation will distinguish between:

```text
Power Source
     │
     ├── Logic / Compute
     │      ├── Raspberry Pi
     │      └── ESP32
     │
     ├── Sensors
     │
     ├── Motor Driver
     │      └── N20
     │
     └── Steering
            └── MG996R
```

The actual battery, regulator, rail voltages, and current requirements will be documented after the final power system is physically verified.

The N20 is a **6 V, 600 RPM motor**, so the motor supply must be compatible with its specification and should not automatically be treated as the same rail used for logic electronics.

An earlier design record contained an LM317-based 5 V regulation concept using:

```text
R1 = 240 Ω
R2 = 720 Ω
```

with:

```text
0.1 µF input decoupling
10 µF output decoupling
```

This was **dropped**: a linear regulator on the 11 V input runs hot and wastes power. The current design uses a single 11 V 3S LiPo pack feeding two buck regulators (motor/servo rail ~6 V, logic rail 5 V), per [electronics/](../../electronics/README.md).

## Grounding and Cable Routing

The final wiring will use a controlled common-ground arrangement.

Motor and servo current paths should be kept separate from sensitive sensor and logic paths where practical.

Cables should also be routed so that they cannot interfere with:

* steering;
* wheels;
* drivetrain;
* moving mechanical components.

Motor wiring and sensitive signal wiring should be separated where practical.

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
Pi ↔ ESP32
  ↓
Complete system
```

Initial motor tests should be performed with the drive wheels lifted from the ground.

The final verification process will include:

* checking power polarity;
* measuring supply rails;
* verifying ESP32 pin assignments;
* checking motor-driver connections;
* checking steering connections;
* checking sensor connections;
* testing USB communication;
* checking cable clearance;
* testing the communication failsafe.

## Reproducibility

The completed wiring documentation will contain the final:

* wiring diagram;
* pinout;
* power distribution;
* sensor connections;
* component connections;
* physical wiring evidence;
* verification results.

Any hardware change must be reflected consistently in the wiring, pinout, firmware, diagrams, and engineering journal.

## Document Boundary

This document is the **physical wiring and connection reference**.

For visual system architecture and engineering diagrams, see:

`docs/diagrams/`

For electrical design decisions and component reasoning, see:

`electronics/`

For mechanical design and fabrication, see:

`design/`

