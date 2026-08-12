<div align="center">

# Robotics Platform Power Distribution & Component Interconnections

**Complete power architecture, component interconnections, and signal routing.**

[← Project home](../../README.md) · [Hardware](../README.md) · [Electronics](../../electronics/README.md)

</div>

---

This document serves as the master reference for all physical connections, power plans, pin assignments, sensor connections, and critical grounding matrices for the multi-microcontroller robotics platform.

| Reference | Purpose |
| --- | --- |
| Power Architecture | Voltage rails, regulation stages, decoupling paths, and current limits |
| Interconnections | Exact pin-to-pin mappings for Pi, ESP32, ToF sensor, and motor driver |
| Critical Integrations | Star grounding rules, UART crossing, and mandatory motor noise isolation |

> [!NOTE]
> This guide defines the definitive power and electronics configuration. Do not deviate from the grounding matrix or bypass the motor EMI isolation capacitors.

## System Overview

This platform uses a 2S LiPo battery (7.4V nominal) as the primary power source, distributed through a 5V buck regulator to logic-level devices (Raspberry Pi, ESP32) and a raw battery motor rail to the TB6612FNG motor driver. The ESP32 serves as the primary motor and sensor controller, while the Raspberry Pi handles high-level vision processing via a CSI camera. Power domains are strictly isolated to prevent motor noise from corrupting sensor and communication buses.

---

## Power Distribution Architecture

### Primary Power Stages

**Battery to Regulation:**
*   **LiPo (2S, 7.4V nominal):** Supplies two parallel distribution paths.
*   **Logic path:** Raw battery → 5V/3A buck regulator (LM2596) → +5V rail.
*   **Motor path:** Raw battery → TB6612FNG VM pins (unregulated, high current capacity).

**Logic Rail Decoupling:**
The +5V buck output feeds two independent LDO regulators:
*   **Raspberry Pi internal LDO:** 5V → 3.3V_Pi (powers Pi and CSI camera).
*   **ESP32 internal LDO:** 5V → 3.3V_ESP (powers ESP32 core and onboard regulators).

**Motor Power Bus:**
The VM rail receives raw battery voltage with a 100µF electrolytic capacitor soldered directly across the VM and GND pins of the TB6612FNG. This capacitor is critical — it absorbs voltage transients when the motor load switches on/off, preventing brown-outs on the logic rails.

### Voltage Rails

| Rail Name | Voltage | Source | Consumers |
|---|---|---|---|
| **V_Batt** | 7.4V | LiPo (2S) | Buck regulator input, TB6612FNG VM input |
| **+5V** | 5V | LM2596 buck output | Pi Vin, ESP32 Vin |
| **+3.3V_Pi** | 3.3V | Pi internal LDO | Pi SoC, CSI camera |
| **+3.3V_ESP** | 3.3V | ESP32 internal LDO | ESP32 core, GPIO logic, I2C pull-ups, VL53L1X VCC, TB6612FNG VCC |
| **VM** | 7.4V (raw) | LiPo (2S) | TB6612FNG motor outputs (AO1, AO2, BO1, BO2) |

---

## Detailed Component Interconnections

```mermaid
architecture-beta
    group power[Power Distribution]
    group compute[Compute & Control]
    group sensing[Sensing]
    group actuation[Actuation]

    service battery[LiPo Battery 2S 7.4V] in power
    service buck[5V 3A Buck Regulator] in power
    service cap_vm[100uF Capacitor VM Bus] in power

    service pi[Raspberry Pi 4/5] in compute
    service esp32[ESP32 WROOM 32E] in compute

    service tof[VL53L1X ToF Sensor] in sensing
    service camera[Pi Camera Module 3 CSI] in sensing

    service driver[TB6612FNG Motor Driver] in actuation
    service motorL[Left N20 Motor] in actuation
    service motorR[Right N20 Motor] in actuation

    battery:R --> L:buck
    battery:B --> T:cap_vm
    buck:R --> L:pi
    buck:B --> T:esp32
    cap_vm:B --> T:driver
    pi:B --> T:camera
    esp32:R --> L:tof
    esp32:B --> T:driver
    tof:B --> T:driver
    driver:B --> T:motorL
    driver:B --> T:motorR