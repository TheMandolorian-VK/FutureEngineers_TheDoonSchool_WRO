<div align="center">

# Diagrams

**Architecture, wiring, and control-flow visualisations.**

[← Documentation](../README.md) · [Strategy](../../strategy/README.md) · [Hardware wiring](../../hardware/wiring-guide/README.md)

</div>

---

Each diagram is named by subject and version, and captioned **Planned** (to be produced) or **Verified** (matches the built vehicle). No diagram files are committed yet: the rows below are the production queue, and each becomes **Committed** when the file lands in this folder.

| Diagram | Type | Source | Status |
| --- | --- | --- | --- |
| Chassis cutting layout | LightBurn file (`.lbrn` + DXF) | Design records | Pending (`.lbrn` and full DXF deck patterns not yet committed) |
| Chassis assembly / double-stack layout | LightBurn + annotated photo | Design records | Pending |
| Wiring flowchart | Mermaid | [hardware/wiring-guide/](../../hardware/wiring-guide/README.md) | Committed: `wiring_overview.mmd` |
| Power distribution flow | Mermaid | [hardware/wiring-guide/](../../hardware/wiring-guide/README.md) | Committed: `wiring_overview.mmd` |
| System architecture (Pi to ESP32 to actuators) | Mermaid | [hardware/wiring-guide/](../../hardware/wiring-guide/README.md) | Committed: `system_architecture.mmd` |
| Software state machine | Mermaid | `strategy/` | Committed: `state_machine.mmd` |
| Obstacle strategy flow (pillars, parking) | Mermaid | `strategy/` | Committed: `challenge_flow.mmd`, `obstacle_strategy.mmd` |

## Chassis cutting files (LightBurn)

The chassis is cut from **3 mm plywood** on the school's laser cutter using **LightBurn**.

- Source files: `.lbrn` project (editable) + exported DXF (portable) + PDF (print). Only the DXF placeholder is committed today ([cut file notes](../../design/dxf_notes.md)); the `.lbrn` master and full deck patterns are pending.
- Two decks: lower deck (electronics, battery) + upper deck (Pi + camera), spaced by brass standoff offsets.
- Every cut file lists: material, thickness, kerf setting, power/speed parameters used.

> [!NOTE]
> The LightBurn `.lbrn` file and full DXF deck patterns are not yet committed. The five Mermaid diagrams above are committed.
