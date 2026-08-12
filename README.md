<div align="center">

# 🤖 The Doon School — WRO Future Engineers 2026

### Designing a self-driving vehicle for the World Robot Olympiad Future Engineers category

![Competition](https://img.shields.io/badge/WRO-2026-0057B8?style=for-the-badge&logo=robotframework&logoColor=white)
![Category](https://img.shields.io/badge/Category-Future%20Engineers-7A2E8E?style=for-the-badge)
![Project status](https://img.shields.io/badge/Project%20reference-Submission%20Configuration-F59E0B?style=for-the-badge)
![Documentation](https://img.shields.io/badge/Documentation-Engineering%20Record-16803A?style=for-the-badge)

[Explore the project](#-explore-the-project) · [Meet the team](#-team) · [Project status](#-project-status)

</div>

---

## Overview

This repository is the public engineering record for **The Doon School Future Engineers** team. It captures the team's submitted vehicle configuration, software architecture, documentation structure, and engineering approach for WRO 2026.

This is the team's **submission design reference**. The final vehicle is intended to align with this reference configuration. Design specifications, source-code structure, visualisations, and measured evidence are intentionally distinguished so that a reviewer can see exactly what each item represents.

> [!IMPORTANT]
> **Truthful documentation commitment:** Concept renders, design plans, code, and physical test evidence are kept clearly separate throughout this repository.

## 👥 Team

| Team member | Focus area |
| --- | --- |
| Dhrubo Mishra | Mechanical design |
| Vivaan Kumbhat | Software development |
| Yug Jain | Electronics, systems, and repository integration |
| Mr. Ashutosh Tripathi | Head mentor |

**School:** The Doon School, Dehradun, India
**Category:** WRO 2026 — Future Engineers

## 🧠 Our Intended System

```text
Camera → Raspberry Pi → perception and decision logic → ESP32 → steering and drive actuators
```

The vehicle architecture separates high-level perception and decision-making from low-level actuator control. Component selections, wiring, interfaces, and software behaviour are documented as part of the submitted configuration and are refined through the team's engineering process.

### Information & control flow

Our design separates high-level perception from low-level actuator control. The **Raspberry Pi** receives camera frames, identifies relevant visual features, and calculates a driving decision. The **ESP32** receives bounded steering and speed targets, then produces the steering-servo and drive outputs. This separation makes individual subsystems easier to inspect, tune, and replace during development.

The communication interface, packet format, power rails, controller mounting, and pin mapping are treated as controlled configuration details. The architecture below is a design map: it describes how the modules relate to each other and how the vehicle is intended to operate.

| Layer | Intended input | Intended responsibility | Intended output | Status |
| --- | --- | --- | --- | --- |
| Perception | Camera frames | Detect relevant visual features | Feature observations | Vision module |
| Decision | Observations and vehicle state | Select drive, avoid, recover, or stop action | Steering and speed targets | Decision module |
| Control | Steering and speed targets | Constrain commands and control outputs | Servo/PWM direction signals | Control module |
| Vehicle | Actuator signals | Steering and propulsion | Physical movement | Vehicle configuration |

> [!NOTE]
> This architecture is the submitted engineering reference. Test records and implementation evidence are kept separately from the configuration description.

## 🚗 Mobility Management

The mobility objective is a compact and serviceable vehicle whose steering response can be tuned and reproduced. The submitted layout uses front steering and rear propulsion, giving the team a direct relationship between a desired turn and a steering-servo command. Mechanical design priorities are secure mounting, accessible maintenance, predictable steering travel, and weight distribution that supports traction and stable cornering.

The design record is structured to hold dimensions, mounting photographs, steering travel, turning observations, and revision notes. The repository intentionally does not contain CAD/STL directories because the submitted configuration does not rely on 3D-printed parts.

| Design topic | Why it matters | Documentation record |
| --- | --- | --- |
| Steering range | Defines usable turning behaviour | Steering-angle and turning test |
| Weight distribution | Influences traction and repeatability | Mass/location record |
| Component mounting | Limits movement and cable strain | Labelled assembly photographs |
| Drive response | Relates command values to motion | Controlled response test |
| Maintainability | Supports fast inspection between runs | Assembly and maintenance notes |

Design decisions are organised in [design/](design/README.md), while measured observations are organised in [docs/testing/](docs/testing/README.md).

## ⚡ Power & Sense Management

The electronics system is organised as a documented power-and-signal architecture rather than an informal collection of modules. Its documentation identifies each controller, sensor, actuator, connector, power rail, protection element, and communication path, allowing a reviewer to understand what each component contributes and how the design can be reproduced responsibly.

The submitted software architecture uses a camera as the primary perception input. The Raspberry Pi source contains an OpenCV colour-detection module that detects red and green regions in camera frames. It converts a frame to HSV colour space, applies colour masks, reduces noise, finds contours, and displays labelled bounding boxes. Thresholds, distance interpretation, and course behaviour are controlled configuration parameters that are documented separately from measured results.

The ESP32 source contains servo and motor-control constants, bounded steering targets, basic direction logic, and a safety stop routine. The wiring record distinguishes **configuration wiring** from **verified wiring**, so that hardware evidence remains traceable.

| Subsystem | System role | Repository location | Configuration area |
| --- | --- | --- | --- |
| Camera/vision | Observe course features and coloured markers | [Raspberry Pi code](software/raspberry_pi/README.md) | Perception |
| Raspberry Pi | Run perception and decision logic | [software/raspberry_pi/](software/raspberry_pi/README.md) | High-level controller |
| ESP32 | Command steering and drive outputs | [software/esp32/](software/esp32/README.md) | Low-level controller |
| Power system | Supply and protect electronics | [electronics/](electronics/README.md) | Power |
| Wiring record | Show power and signal connections | [hardware/wiring/](hardware/wiring/README.md) | Interfaces |

## 🧭 Software & Obstacle Management

The software is organised around clearly separated responsibilities. The high-level Raspberry Pi layer handles camera input and perception. The ESP32 layer handles actuator commands and state transitions. Keeping the interface explicit allows a perception change to be evaluated without silently changing motor behaviour and makes debugging more understandable.

The `software/raspberry_pi/wromain.cpp` file contains the colour-detection module. It opens a camera feed, uses HSV ranges for red and green, filters small contours, and displays visual labels. Path planning, controller communication, and distance handling are maintained as distinct parts of the architecture, with their behaviour documented through the strategy and test records.

The `software/esp32/obstacleChallenge.ino` file defines states named `DRIVING`, `RED_PILLAR`, `GREEN_PILLAR`, `PARKING`, and `FINISHED`, plus steering and motor helper functions. Communication, detection, parking, and debugging are separated into named functions so their implementation can be tracked clearly. The state model documents software organisation, while run evidence is stored separately in the testing and video areas.

### Intended decision sequence

```text
Observe camera input
        ↓
Classify relevant red / green feature
        ↓
Evaluate intended route and safety conditions
        ↓
Send bounded steering and speed targets
        ↓
Apply actuator command
        ↓
Re-centre, recover, or stop as required
```

Strategy diagrams and pseudocode belong in [strategy/](strategy/README.md). Design reasoning and revisions are recorded in the [engineering journal](docs/engineering_journal/README.md). Measured outcomes are recorded in [testing](docs/testing/README.md).

## 🧪 Testing, Iteration & Evidence

The repository uses a simple engineering rule: configuration is separate from evidence. A design choice is explained in the architecture and strategy material, while an observed conclusion is recorded in the corresponding test record. This keeps the project traceable and gives the team a clear history of why a decision was made.

Each test record includes the date, objective, vehicle/software version, setup, procedure, raw observations or measurements, result, limitations, and next action. Unsuccessful tests are retained because they show the actual process of iteration. Any test photograph or video is linked only to the run it shows.

| Evidence type | Storage location | Required label |
| --- | --- | --- |
| Design decision | [Engineering journal](docs/engineering_journal/README.md) | Date, author, options, rationale |
| Proposed diagram | [Diagrams](docs/diagrams/README.md) | **Proposed** and version |
| Physical/software test | [Testing](docs/testing/README.md) | Date, setup, method, observation |
| Test visual | [Test images](images/testing/README.md) | Date and conditions |
| Vehicle view | [Robot images](images/robot/README.md) | Render or dated photograph |
| Run video | [Videos](videos/README.md) | Date, challenge, setup, outcome |

## 🖼️ Team & Vehicle Visuals

The repository keeps team, vehicle, testing, and competition visuals in separate locations so that their context stays clear. Team imagery is used with the consent of the people pictured. Vehicle views use descriptive front, rear, left, right, top, and bottom filenames.

With organiser guidance, near-1:1 AI visualisations are used as the vehicle's design-reference views. Each image is labelled **AI-generated concept render**, so it is not confused with a photograph or a test image. The view filenames are `front.*`, `rear.*`, `left.*`, `right.*`, `top.*`, and `bottom.*` inside [images/robot/](images/robot/README.md).

## 🔧 Build, Upload & Reproduction Plan

The submitted configuration provides the framework for build-and-upload instructions. The controlled procedure covers the operating-system setup, library versions, camera configuration, Raspberry Pi build command, ESP32 board/environment selection, required libraries, upload method, communication setup, and safe power-on sequence. Measured verification is maintained in the testing record rather than implied by the instructions themselves.

The Raspberry Pi source uses OpenCV headers and a camera input. The ESP32 source uses `ESP32Servo`. Exact dependencies, compilation commands, and controller-upload instructions are controlled configuration details and belong in the relevant software folder, linked to the corresponding journal record.

## 🤝 Repository Use & Attribution

This repository is designed to make the submitted configuration clear to judges, mentors, and other students. It contains the team's own documentation framework and source files. The team does not copy another team's engineering claims, mechanical design, media, or code. Git history records the team's work on this project.

## 🗂️ Explore the Project

| Area | What it will contain | Status |
| --- | --- | --- |
| 📐 [`design/`](design/) | Vehicle layout, mechanical decisions, dimensions | Configuration |
| ⚡ [`electronics/`](electronics/) | Components, power plan, wiring, pin assignments | System reference |
| 🧭 [`strategy/`](strategy/) | Open/Obstacle Challenge logic and flow diagrams | Decision architecture |
| 💻 [`software/`](software/) | Raspberry Pi and ESP32 source code | Control software |
| 📘 [`docs/`](docs/) | Engineering journal, diagrams, testing records | Engineering record |
| 🖼️ [`images/`](images/) | Team, vehicle, and test visuals | Visual reference |
| 🎥 [`videos/`](videos/) | Dated run and presentation videos | Run records |
| 🧾 [`evidence/`](evidence/) | Dated reviews, calibration, and test summaries | Evidence archive |

## 🎨 Robot Visualizations

Visuals in [`images/robot/`](images/robot/) are **AI-generated concept renders** based on the team's submitted vehicle configuration. They are design-reference views, not photographs.

## 📏 Documentation Standard

We keep a clear distinction between **configuration material**, **concept renders**, **source files**, and **measured results**.

- Each test record states its date, setup, method, observations, and next action.
- Configuration material is labelled clearly and kept separate from measured evidence.
- Concept renders, simulations, and code are not presented as evidence of physical performance.
- Iterations and unsuccessful outcomes will be retained as part of the engineering process.

## 🛠️ Development Roadmap

| Phase | Focus | Evidence added when complete |
| --- | --- | --- |
| `01` | Define architecture and component choices | Dated design decision |
| `02` | Assemble and document the first prototype | Labelled photographs and wiring record |
| `03` | Implement perception, control, and communication | Source code and software test record |
| `04` | Test subsystems | Measured, dated test results |
| `05` | Integrate the vehicle | Complete challenge evidence |

## 🗃️ Repository History

This repository uses GitHub to track our engineering progress. Updates are committed as the team's work evolves.

## 📄 License

Published for educational use as part of WRO Future Engineers. Team materials may be updated during development.
