<div align="center">

# ESP32 Control Layer

**Low-level actuator control and Raspberry Pi communication.**

[← Software](../README.md) · [Hardware Wiring](../../hardware/wiring-guide/README.md) · [Electronics](../../electronics/README.md)

</div>

---

The ESP32 is the low-level controller for the vehicle.

The Raspberry Pi performs perception and navigation, while the ESP32 receives bounded steering and speed commands and converts them into actuator outputs.

## Current Contents

- `obstacleChallenge.ino` — ESP32 vehicle-control firmware.

## Responsibilities

The ESP32 handles:

- MG996R steering control;
- TB6612FNG motor control;
- N20 drive-motor control;
- USB serial communication with the Raspberry Pi;
- command validation;
- communication-loss failsafe;
- emergency stop;
- low-level vehicle state.

The ESP32 does **not** perform camera-based perception. Vision and navigation remain on the Raspberry Pi.

## Hardware

```text
Raspberry Pi 4B
       │
       │ USB Serial
       ▼
     ESP32
    /     \
MG996R   TB6612FNG
             │
             ▼
        N20 6V 600RPM