# The Doon School — WRO Future Engineers 2026

> Designing a self-driving vehicle for the World Robot Olympiad Future Engineers category.

## Overview

This repository is the public engineering record for **The Doon School Future Engineers** team. It will document how we design, build, program, test, and refine our autonomous vehicle for WRO 2026.

We are currently in the **design and planning phase**. The physical vehicle is not yet assembled, and no integrated performance claims are made here. As development progresses, every completed stage will be supported by dated documentation, source files, photographs, or measured test results.

## Team

| Team member | Focus area |
| --- | --- |
| Dhrubo Mishra | Mechanical design |
| Vivaan Kumbhat | Software development |
| Yug Jain | Electronics, systems, and repository integration |
| Mr. Ashutosh Tripathi | Head mentor |

**School:** The Doon School, Dehradun, India
**Category:** WRO 2026 — Future Engineers

## Our intended system

```text
Camera → Raspberry Pi → perception and decision logic → ESP32 → steering and drive actuators
```

The intended architecture separates high-level perception and decision-making from low-level actuator control. Final components, wiring, and software behaviour will be recorded only after they are selected, assembled, and verified.

## Explore the project

| Area | What it will contain | Status |
| --- | --- | --- |
| [`design/`](design/) | Vehicle layout, mechanical decisions, dimensions | Planned |
| [`electronics/`](electronics/) | Components, power plan, wiring, pin assignments | Planned |
| [`strategy/`](strategy/) | Open/Obstacle Challenge logic and flow diagrams | Planned |
| [`software/`](software/) | Raspberry Pi and ESP32 source code | Under development |
| [`docs/`](docs/) | Engineering journal, diagrams, testing records | In preparation |
| [`images/`](images/) | Team, vehicle, and test visuals | In preparation |
| [`videos/`](videos/) | Dated run and presentation videos | Reserved |
| [`evidence/`](evidence/) | Dated reviews, calibration, and test summaries | Reserved |
| [`resources/`](resources/) | Rules, datasheets, and permitted references | Reserved |

## Robot visualizations

Until physical assembly is complete, any visuals in [`images/robot/`](images/robot/) are **AI-generated concept renders** based on the team's current design direction. They represent an intended configuration, not photographs of a completed robot.

## Documentation standard

We keep a clear distinction between **planned work**, **conceptual material**, **implemented work**, and **measured results**.

- Each test record will state its date, setup, method, observations, and next action.
- Plans and proposals are labelled clearly until verified.
- Concept renders, simulations, and code are not presented as evidence of physical performance.
- Iterations and unsuccessful outcomes will be retained as part of the engineering process.

## Development roadmap

1. Define vehicle architecture and component choices.
2. Assemble and document the first prototype.
3. Implement perception, control, and communication software.
4. Test subsystems and record results.
5. Integrate the vehicle and publish challenge evidence.

## Repository history

This repository uses GitHub to track our engineering progress. Updates are committed as the team's work evolves.

## License

Published for educational use as part of WRO Future Engineers. Team materials may be updated during development.
