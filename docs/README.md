<div align="center">

# Documentation Hub

**The team's design record, engineering decisions, diagrams, and test evidence.**

[← Project home](../README.md) · [Design](../design/README.md) · [Strategy](../strategy/README.md)

</div>

---

> [!IMPORTANT]
> This directory separates **planned work** from **verified work**. A document is not evidence of a physical result unless it records a date, setup, method, and observed outcome.

| Section | Purpose | Current status |
| --- | --- | --- |
| [Diagrams](diagrams/README.md) | Architecture, wiring, and logic diagrams | Pending (no diagrams committed yet) |
| [Engineering journal](engineering_journal/README.md) | Dated choices, iterations, and lessons (mapped to the WRO rubric) | Active |
| [Testing](testing/README.md) | Test plans and measured results | In progress |
| [Release notes](release_notes.md) | Repository-level milestones | Active |

## Documentation rule

Use one dated file per meaningful decision or test. Keep the source of each claim clear: **plan**, **calculation**, **simulation**, **observation**, or **measurement**.

## What the evaluators see (WRO 2026 rubric: max 30 points)

| Criterion | Max | Journal entries | Key files a judge should open |
| --- | --- | --- | --- |
| 1. Mobility and Mechanical Design | 6 | 01–05 | [engineering_journal](engineering_journal/README.md) entries 01–05, [design/](../design/README.md) (committed: `wooden_plate.dxf`; LightBurn `.lbrn` and STL models pending) |
| 2. Power and Sensor Architecture | 6 | 06, 08, 11 | [engineering_journal](engineering_journal/README.md) entries 06/08/11, [electronics/](../electronics/README.md), [hardware/wiring-guide](../hardware/wiring-guide/README.md) |
| 3. Software Architecture and Obstacle Strategy | 6 | 08, 09, 10 | [engineering_journal](engineering_journal/README.md) entries 08/09/10, [strategy/](../strategy/README.md), [software/](../software/README.md) |
| 4. Systems Thinking and Engineering Decisions | 6 | 02–10 | [engineering_journal](engineering_journal/README.md) entries 02–10 (risk register in entry 10) |
| 5. Reproducibility and GitHub Quality | 6 | 01–11 + repo structure | Root [README.md](../README.md), [engineering_journal](engineering_journal/README.md) (all entries), [hardware/wiring-guide](../hardware/wiring-guide/README.md), committed `design/wooden_plate.dxf`; diagrams/STL/`.lbrn` pending |

## How this repository maps to the five documentation criteria

| Criterion | What judges look for | Key files to open first |
| --- | --- | --- |
| C1 Mobility & Mechanical Design | Torque/speed reasoning, tradeoffs, build evidence | docs/engineering_journal/README.md (entries 01–05), design/README.md |
| C2 Power & Sensor Architecture | Single-battery two-rail power, sensor choices, calibration | docs/engineering_journal/README.md (06, 08, 11), electronics/README.md, hardware/wiring-guide/README.md |
| C3 Software Architecture & Obstacle Strategy | State machine, PD steering, obstacle logic | strategy/README.md, docs/engineering_journal/README.md (08–10), software/ |
| C4 Systems Thinking & Engineering Decisions | "Chose X over Y because…", constraints, risks, iteration | docs/engineering_journal/README.md (02–10), the risk register (entry 10) |
| C5 Reproducibility & GitHub Quality | Clear README, reproducible CAD, wiring, commits | README.md (root), docs/README.md, hardware/wiring-guide/README.md, design/wooden_plate.dxf |

> [!NOTE]
> Diagrams, STL models, and the LightBurn `.lbrn` chassis source are not committed yet. Currently only `design/wooden_plate.dxf` is in the repository; the rest are pending and will be added as the build is finalised.
