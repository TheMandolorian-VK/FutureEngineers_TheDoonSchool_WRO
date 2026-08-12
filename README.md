# Future Engineers 2026 – The Doon School

## Team information

| Item | Details |
| --- | --- |
| Team | The Doon School Future Engineers |
| Competition | World Robot Olympiad (WRO) 2026, Future Engineers |
| School | The Doon School, Dehradun, India |

| Member | Responsibility |
| --- | --- |
| Dhrubo Mishra | Mechanical engineering |
| Vivaan Kumbhat | Software engineering |
| Yug Jain | Electronics, systems, and GitHub integration |
| Mr. Ashutosh Tripathi | Head mentor |

## Project status

This is a design-stage repository for the team's proposed autonomous vehicle. Physical assembly and integrated testing are still in progress. Statements, images, and documents are labelled to distinguish plans, concept renders, implementation, and measured results. This repository does not claim that the vehicle has been built or tested unless dated evidence is added.

## Robot visualizations

The images in [`images/robot/`](images/robot/) are AI-generated concept renders based on the team's current mechanical design and specifications. They show the intended vehicle configuration and are not photographs of a completed physical robot.

## Intended system architecture

```text
Camera → Raspberry Pi → perception and decision logic → ESP32 → steering and drive actuators
```

The Raspberry Pi is intended to run perception and decision logic. The ESP32 is intended to control steering, drive, communication, and safety functions. Hardware selections and final sensor configuration are still under evaluation.

## Current software

- [`software/raspberry_pi/wromain.cpp`](software/raspberry_pi/wromain.cpp): Raspberry Pi program under development.
- [`software/esp32/obstacleChallenge.ino`](software/esp32/obstacleChallenge.ino): ESP32 program under development.

Code presence alone is not evidence of completed robot integration or successful runs. Add dated test records when tests are performed.

## Repository structure

```text
FutureEngineers_TheDoonSchool_WRO/
├── README.md
├── docs/
│   ├── diagrams/                 # system, wiring, and logic diagrams
│   ├── engineering_journal/      # dated design decisions and iterations
│   ├── testing/                  # dated test plans and results
│   └── release_notes.md
├── hardware/
│   └── wiring/                   # verified wiring diagram and pin table
├── images/
│   ├── competition/              # future competition evidence
│   ├── robot/                    # labelled concept renders / future robot views
│   ├── team/
│   └── testing/                  # future test evidence
├── software/
│   ├── esp32/
│   └── raspberry_pi/
└── videos/                       # future run videos
```

## Evidence policy

- Put a date, conditions, method, and measured outcome in each test record.
- Label planned work as **Planned** and unverified work as **Unverified**.
- Do not present simulations, concept renders, or code as physical-run evidence.
- Retain unsuccessful results and describe the next change instead of removing them.

See each folder's README for its documentation guidance.

## License

Published for educational use as part of WRO Future Engineers. Team materials may be updated during development.
