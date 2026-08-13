# WRO 2026 Rule Compliance Checklist

Vehicle rule compliance for the WRO Future Engineers 2026 season. This checklist maps every mechanical requirement to the design decision that satisfies it and to the evidence that confirms it.

Status legend:

- **Designed:** satisfied by the current design intent, not yet physically verified.
- **To verify:** check needed at the build or on the day.
- **Verified:** confirmed on the physical vehicle and logged in the [engineering journal](../docs/engineering_journal/README.md).

## Vehicle construction rules

| Rule | Requirement | Design answer | Status |
| --- | --- | --- | --- |
| 11.1-11.2 | Envelope ≤ 300x200x300 mm | Double-stack plywood layout keeps the 300x200 mm footprint; deck spacing ~35 mm keeps height low | To verify with the envelope gauge at the build |
| 11.1-11.2 | Mass ≤ 1.5 kg | [Mass budget](mass_budget.md) framework ready; to be measured with a scale | To verify with a scale |
| 11.3 / 11.5 | Exactly **one driving axle** | Single N20 6 V motor drives the rear axle; both rear wheels driven through one mechanically coupled axle | To verify both rear wheels receive torque |
| 11.3 / 11.5 | No differential drive, no one-motor-per-side | No independent side motors, no differential fitted | Designed |
| 11.13 | Exactly **one steering actuator** | Single TowerPro MG996R servo drives the front Ackermann linkage | Designed |
| - | Four wheels in contact | Two front (steered) + two rear (driven) wheels | Designed |
| - | No wireless control | All control and power on board; no radio link to an external controller | Designed |

## Competition behaviour rules

| Rule | Requirement | Design answer | Status |
| --- | --- | --- | --- |
| - | Complete the obstacle course autonomously | On-board vision (Pi 4B + Camera Module 3 Wide) + ToF/ultrasonic/IMU + ESP32 state machine | To verify in test runs |
| - | Park correctly after the course | Camera + ToF parking-gap detection, dynamic speed control, PD softening near lock | To verify in test runs |

## Notes

- The steering and drive definitions follow the interpretation used across the [design overview](README.md) and [engineering journal](../docs/engineering_journal/README.md).
- Any rule clarification from the national or international organisers that affects the design is recorded in the [engineering journal](../docs/engineering_journal/README.md) as a new entry.
- Rule numbers refer to the WRO 2026 Future Engineers rules; confirm against the latest published version before the event.
