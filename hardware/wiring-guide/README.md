<div align="center">

# Robotics Platform Power Distribution & Component Interconnections

**Complete power architecture, component interconnections, and signal routing.**

[← Project home](../../README.md) · [Hardware](../README.md) · [Electronics](../../electronics/README.md)

</div>

---

This document serves as the master reference for all physical connections, power plans, and pin assignments for the multi-microcontroller robotics platform.

| Reference | Purpose |
| --- | --- |
| Power Architecture | Voltage regulation via LM317, rail breakdown, and current management |
| Interconnections | Pin-to-pin mappings for Pi 4B, ESP32, ToF sensor, and motor driver |
| Critical Integrations | Star grounding rules, UART crossing, and motor noise decoupling |

> [!NOTE]
> This guide defines the definitive power and electronics configuration. Do not deviate from the grounding matrix or bypass decoupling capacitors.

## System Overview

This platform uses an **LM317 adjustable linear voltage regulator** to step down raw input power (e.g., 7.4V 2S LiPo or 9V–12V DC input) down to a stable **5V system rail**. This regulated 5V rail feeds both compute modules (**Raspberry Pi 4B** and **ESP32**) as well as the motor supply voltage (VM) on the **TB6612FNG** motor driver.

The ESP32 serves as the primary motor and sensor controller (reading the Time of Flight sensor and driving the **N20 motors**), while the Pi 4B handles high-level vision processing via the **Raspberry Pi Camera Module 3 Wide**.

---

## Power Distribution Architecture

### LM317 Regulation Stage

An LM317 adjustable linear regulator is configured to generate a steady **5.0V output**:
*   **Voltage Divider:** $R_1 = 240\,\Omega$ (between VO and ADJ) and $R_2 = 720\,\Omega$ (between ADJ and GND) yield $V_{\text{out}} = 1.25\text{V} \times (1 + 720/240) = 5.0\text{V}$.
*   **Input Decoupling:** A $0.1\,\mu\text{F}$ ceramic capacitor placed close to the VI pin suppresses input noise.
*   **Output Decoupling:** A $10\,\mu\text{F}$ electrolytic capacitor placed across VO and GND stabilizes the regulated 5V output rail.

### Voltage Rails

| Rail Name | Voltage | Source | Consumers |
|---|---|---|---|
| **V_Raw** | 7.4V – 12V | Battery / DC Supply | LM317 VI (Input) pin |
| **Main +5V** | 5.0V | LM317 VO (Output) pin | Pi 4B Pin 2/4, ESP32 Vin, TB6612FNG VM |
| **+3.3V_Pi** | 3.3V | Pi 4B internal LDO | Pi Camera Module 3 Wide |
| **+3.3V_ESP** | 3.3V | ESP32 internal LDO | ESP32 core, ToF VCC, TB6612FNG VCC (Logic Power) |

---

## Detailed Component Interconnections

```mermaid
flowchart TD
    subgraph Power ["Power Distribution"]
        battery["Raw Battery / Power Source"]
        lm317["LM317 Regulator (5V Output)"]
    end

    subgraph Compute ["Compute & Control"]
        pi["Raspberry Pi 4B"]
        esp32["ESP32"]
    end

    subgraph Sensing ["Sensing"]
        camera["Pi Camera 3 Wide"]
        tof["Time of Flight Sensor"]
    end

    subgraph Actuation ["Actuation"]
        driver["TB6612FNG Motor Driver"]
        motorL["Left N20 Motor"]
        motorR["Right N20 Motor"]
    end

    battery --> lm317
    lm317 -->|5V Rail| pi
    lm317 -->|5V Rail| esp32
    lm317 -->|5V Rail| driver
    pi --> camera
    pi <-->|UART| esp32
    esp32 -->|I2C| tof
    esp32 -->|PWM / GPIO| driver
    driver --> motorL
    driver --> motorR