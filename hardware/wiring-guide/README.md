<div align="center">

# Robotics Platform Power Distribution & Component Interconnections

**Complete power architecture, component interconnections, and signal routing.**

[← Project home](../../README.md) · [Hardware](../README.md) · [Electronics](../../electronics/README.md)

</div>

---

This document serves as the master reference for all physical connections, power plans, and pin assignments for the multi-microcontroller robotics platform. 

> [!CAUTION]
> **DIRECT WIRING VOLTAGE WARNING**
> Because this system does not use a buck regulator, **you cannot use a 7.4V LiPo battery for the logic boards**. Supplying more than 5.25V directly to the Raspberry Pi 4B or ESP32 will instantly destroy them. This guide assumes you are using a **5V USB Power Bank** (or equivalent 5V source) to power the entire system.

## System Overview

This platform uses a direct 5V power source to drive both logic and motors. The **Raspberry Pi 4B** receives main power (via USB-C) and distributes 5V to the **ESP32** and the **TB6612FNG** motor driver's power rail (VM). 

The ESP32 serves as the primary motor and sensor controller (reading the Time of Flight sensor and driving the **N20 motors**), while the Pi 4B handles high-level vision processing via the **Raspberry Pi Camera Module 3 Wide**. 

---

## Power Distribution Architecture

### Voltage Rails

| Rail Name | Voltage | Source | Consumers |
|---|---|---|---|
| **Main 5V** | 5V | 5V USB Power Bank (via Pi 4B USB-C) | Pi 4B SoC, ESP32 Vin, TB6612FNG VM (Motor Power) |
| **+3.3V_Pi** | 3.3V | Pi 4B internal LDO | Pi Camera Module 3 Wide |
| **+3.3V_ESP** | 3.3V | ESP32 internal LDO | ESP32 core, ToF VCC, TB6612FNG VCC (Logic Power) |

---

## Detailed Component Interconnections

```mermaid
architecture-beta
    group power[Power Source]
    group compute[Compute & Control]
    group sensing[Sensing]
    group actuation[Actuation]

    service usb_power[5V USB Power Bank] in power

    service pi[Raspberry Pi 4B] in compute
    service esp32[ESP32] in compute

    service tof[Time of Flight Sensor] in sensing
    service camera[Pi Camera 3 Wide] in sensing

    service driver[TB6612FNG Motor Driver] in actuation
    service motorL[Left N20 Motor] in actuation
    service motorR[Right N20 Motor] in actuation

    usb_power:R --> L:pi
    pi:B --> T:esp32
    pi:R --> L:driver
    pi:B --> T:camera
    esp32:R --> L:tof
    esp32:B --> T:driver
    tof:B --> T:driver
    driver:B --> T:motorL
    driver:B --> T:motorR