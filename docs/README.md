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
| [Diagrams](diagrams/README.md) | Architecture, wiring, and logic diagrams | 5 Mermaid diagrams committed; chassis/layout diagrams pending |
| [Engineering journal](engineering_journal/README.md) | Dated choices, iterations, and lessons (mapped to the WRO rubric) | Active |
| [Testing](testing/README.md) | Test plans and measured results | In progress |
| [Release notes](release_notes.md) | Repository-level milestones | Active |

## Documentation rule

Use one dated file per meaningful decision or test. Keep the source of each claim clear: **plan**, **calculation**, **simulation**, **observation**, or **measurement**.

## What the evaluators see (WRO 2026 rubric: max 30 points)

| Criterion | Max | Journal entries | Key files a judge should open |
| --- | --- | --- | --- |
| 1. Mobility and Mechanical Design | 6 | 01–05 | [engineering_journal](engineering_journal/README.md) entries 01–05, [design/](../design/README.md) (Ackermann geometry, assembly guide, rules checklist, mechanical BOM; `wooden_plate.dxf` is placeholder, `.lbrn` and full deck patterns pending) |
| 2. Power and Sensor Architecture | 6 | 06, 08, 11 | [engineering_journal](engineering_journal/README.md) entries 06/08/11, [electronics/](../electronics/README.md) (BOM + power architecture), [hardware/wiring-guide](../hardware/wiring-guide/README.md) |
| 3. Software Architecture and Obstacle Strategy | 6 | 08, 09, 10 | [strategy/](../strategy/README.md) (overview + [software_architecture.md](../strategy/software_architecture.md) deep-dive), [engineering_journal](engineering_journal/README.md) entries 08/09/10, [software/](../software/README.md) |
| 4. Systems Thinking and Engineering Decisions | 6 | 02–10 | [engineering_journal](engineering_journal/README.md) entries 02–10 (risk register in entry 10), [design/design_decisions.md](../design/design_decisions.md) |
| 5. Reproducibility and GitHub Quality | 6 | 01–11 + repo structure | Root [README.md](../README.md), [docs/README.md](README.md), [engineering_journal](engineering_journal/README.md) (all entries), [hardware/wiring-guide](../hardware/wiring-guide/README.md), [testing/procedures.md](testing/procedures.md), `design/wooden_plate.dxf` (placeholder); diagrams/STL/`.lbrn` pending |

## How this repository maps to the five documentation criteria

| Criterion | What judges look for | Key files to open first |
| --- | --- | --- |
| C1 Mobility & Mechanical Design | Torque/speed reasoning, tradeoffs, build evidence | docs/engineering_journal/README.md (entries 01-05), design/README.md, design/ackermann_geometry.md, design/assembly_guide.md |
| C2 Power & Sensor Architecture | Single-battery two-rail power, sensor choices, calibration | docs/engineering_journal/README.md (06, 08, 11), electronics/README.md, hardware/wiring-guide/README.md |
| C3 Software Architecture & Obstacle Strategy | State machine, PD steering, obstacle logic | strategy/README.md, strategy/software_architecture.md, docs/engineering_journal/README.md (08-10), software/ |
| C4 Systems Thinking & Engineering Decisions | "Chose X over Y because...", constraints, risks, iteration | docs/engineering_journal/README.md (02-10), design/design_decisions.md |
| C5 Reproducibility & GitHub Quality | Clear README, CAD, wiring, commits | README.md (root), docs/README.md, hardware/wiring-guide/README.md, docs/testing/procedures.md, design/wooden_plate.dxf (placeholder) |

> [!NOTE]
> STL models and the LightBurn `.lbrn` chassis source are not yet committed. The five Mermaid diagrams are committed. `design/wooden_plate.dxf` is a placeholder rectangle.
