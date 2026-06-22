# Future Engineers 2026 – The Doon School

## Team Information

**Team Name:** The Doon School Future Engineers

**Competition:** World Robot Olympiad (WRO) 2026

**Category:** Future Engineers

**School:** The Doon School, Dehradun, India

---

# Project Overview

This repository contains the complete design, development, testing, and documentation of our autonomous vehicle for the WRO Future Engineers 2026 competition.

The objective of the Future Engineers challenge is to design, build, program, test, and document a fully autonomous vehicle capable of successfully completing both the Open Challenge and the Obstacle Challenge without human intervention.

Our approach focuses on modular engineering, reproducibility, robust software architecture, and iterative testing. Every major design decision is documented and justified through experimentation, calculations, and performance evaluation.

---

# Repository Structure

```text
FutureEngineers_TheDoonSchool_WRO
│
├── README.md
│
├── docs/
│   ├── engineering_journal/
│   ├── testing/
│   └── diagrams/
│
├── hardware/
│   ├── cad/
│   ├── wiring/
│   └── stl/
│
├── images/
│   ├── robot/
│   ├── testing/
│   └── competition/
│
├── software/
│   ├── esp32/
│   └── raspberry_pi/
│
└── videos/
```

---

# Team Introduction

## Team Members

| Name | Role                              |
| ---- | --------------------------------- |
| Dhrubo Mishra         | Mechanical Engineering            |
| Vivaan Kumbhat        | Software Engineering              |
| Yug Jain              | Electronics & Systems Integration |
| Mr. Ashutosh Tripathi | Head Mentor                       |

### School

The Doon School
Dehradun, Uttarakhand, India

---

# Engineering Philosophy

Our design philosophy is based on three core principles:

### 1. Reliability

Competition robots must consistently complete tasks under varying environmental conditions. Reliability is prioritized over unnecessary complexity.

### 2. Modularity

Mechanical, electrical, and software systems are developed as independent modules that can be tested and improved separately.

### 3. Reproducibility

All major design decisions, calculations, test results, and source code are documented to allow complete reproduction of the vehicle.

---

# Vehicle Architecture

## High-Level System Overview

```text
Camera
   ↓
Raspberry Pi
   ↓
Computer Vision
   ↓
Decision Making
   ↓
ESP32
   ↓
Steering Servo
Rear Drive Motors
```

The Raspberry Pi acts as the primary processing unit responsible for perception and decision-making.

The ESP32 functions as the actuator controller responsible for steering and motor control.

---

# Mechanical Design

## Chassis

The vehicle uses a four-wheeled chassis designed specifically for autonomous navigation.

### Design Objectives

* High stability
* Low center of gravity
* Easy maintenance
* Efficient weight distribution
* Compliance with WRO regulations

Future updates will include:

* CAD models
* Manufacturing drawings
* Mass analysis
* Center of gravity calculations

---

## Steering System

The vehicle utilizes Ackermann steering geometry.

### Objectives

* Accurate cornering
* Reduced tire scrub
* Improved path tracking
* Consistent turning radius

Documentation to be added:

* Steering calculations
* Servo selection rationale
* Turning radius measurements
* Steering assembly photographs

---

## Drive System

Rear-wheel drive is used to provide propulsion.

### Design Considerations

* Torque requirements
* Speed requirements
* Mechanical efficiency
* Reliability under competition conditions

Future documentation will include:

* Motor specifications
* Gear ratio calculations
* Mounting solutions
* Test data

---

# Electronics Architecture

## Main Controller

### Raspberry Pi

Responsibilities:

* Computer Vision
* Object Detection
* State Machine Logic
* Path Planning
* Steering Calculation

---

## Actuator Controller

### ESP32

Responsibilities:

* Steering Control
* Motor Control
* Communication Handling
* Safety Functions

---

## Sensor Suite

The final sensor configuration is under evaluation.

Potential sensors include:

* Camera Module
* Distance Sensors
* IMU
* Wheel Encoders

Future documentation will include:

* Sensor placement
* Calibration procedures
* Sensor performance analysis
* Wiring diagrams

---

# Software Architecture

## Overview

The software system follows a layered architecture.

```text
Perception Layer
        ↓
Decision Layer
        ↓
Control Layer
        ↓
Actuation Layer
```

---

## Perception Layer

Responsible for:

* Image acquisition
* Object detection
* Color classification
* Distance estimation

Technologies:

* C++
* OpenCV

---

## Decision Layer

Responsible for:

* Vehicle state management
* Obstacle avoidance strategy
* Path planning
* Parking logic

---

## Control Layer

Responsible for:

* Steering computation
* Speed regulation
* Motion planning

---

## Actuation Layer

Implemented on the ESP32.

Responsible for:

* Servo control
* Motor control
* Hardware safety

---

# Obstacle Challenge Strategy

## Pillar Detection

The system identifies:

* Red Pillars
* Green Pillars

using computer vision techniques.

---

## Avoidance Logic

### Red Pillar

The vehicle passes the obstacle while ensuring the pillar remains on the correct side according to WRO rules.

### Green Pillar

The vehicle performs the corresponding avoidance maneuver while maintaining lane integrity and stability.

---

## State Machine

The obstacle challenge software is organized using a state machine architecture.

### States

```text
DRIVING
↓
RED_PILLAR
↓
RETURN_TO_CENTER
↓
DRIVING

GREEN_PILLAR
↓
RETURN_TO_CENTER
↓
DRIVING

PARKING
↓
FINISHED
```

This architecture improves reliability, debugging, and maintainability.

---

# Open Challenge Strategy

Documentation will be added after completion of obstacle challenge development.

Planned topics:

* Direction determination
* Lap counting
* Corner detection
* Wall following
* Localization

---

# Testing Methodology

Every subsystem is validated independently before full integration.

## Mechanical Testing

* Steering accuracy
* Turning radius
* Chassis durability

## Electronics Testing

* Voltage stability
* Current consumption
* Communication reliability

## Software Testing

* Detection accuracy
* Control stability
* State transitions

---

# Engineering Journal

A complete engineering journal is maintained throughout development.

The journal records:

* Design decisions
* Failures
* Improvements
* Experimental results
* Competition preparation

Documentation can be found in:

```text
docs/engineering_journal/
```

---

# Future Development Roadmap

## Phase 1

* Repository setup
* Architecture planning
* Mechanical design

## Phase 2

* Electronics integration
* Steering implementation
* Motor control

## Phase 3

* Computer vision development
* Obstacle avoidance

## Phase 4

* Open challenge implementation
* Parking logic

## Phase 5

* Optimization
* Testing
* Competition preparation

---

# License

This project is published for educational purposes as part of the World Robot Olympiad Future Engineers program.

All documentation, software, and design files are maintained by the team and may be updated throughout the development cycle.

---

# Acknowledgements

* World Robot Olympiad Association
* The Doon School
* Mentors, teachers, supporters who contribute to the development of the project, and Mr. Ravi.
