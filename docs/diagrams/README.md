<div align="center">

# Diagrams

**Architecture, wiring, and control-flow visualisations.**

[← Documentation](../README.md) · [Strategy](../../strategy/README.md) · [Hardware wiring](../../hardware/wiring-guide/README.md)

</div>

---

Each diagram is named by subject and version, and captioned **Planned** (to be produced) or **Verified** (matches the built vehicle). No diagram files are committed yet: the rows below are the production queue, and each becomes **Committed** when the file lands in this folder.

| Diagram | Type | Source | Status |
| --- | --- | --- | --- |
| Chassis cutting layout | LightBurn file (`.lbrn` + DXF) | Design records | Planned (`.lbrn` and full DXF deck patterns pending) |
| Chassis assembly / double-stack layout | LightBurn + annotated photo | Design records | Planned |
| Wiring flowchart | Mermaid + PDF export | [hardware/wiring-guide/](../../hardware/wiring-guide/README.md) | Planned |
| Power distribution flow | Mermaid | [hardware/wiring-guide/](../../hardware/wiring-guide/README.md) | Planned |
| System architecture (Pi ↔ ESP32 ↔ actuators) | Mermaid | [hardware/wiring-guide/](../../hardware/wiring-guide/README.md) | Planned |
| Software state machine | Mermaid | `strategy/` | Planned |
| Obstacle strategy flow (pillars, parking) | Mermaid | `strategy/` | Planned |

## Chassis cutting files (LightBurn)

The chassis is cut from **3 mm plywood** on the school's laser cutter using **LightBurn**.

- Source files: `.lbrn` project (editable) + exported DXF (portable) + PDF (print), stored with the design records. Only the DXF validation geometry is committed today ([cut file notes](../../design/dxf_notes.md)); the `.lbrn` master and full deck patterns are pending.
- Two decks: lower deck (electronics, battery) + upper deck (Pi + camera), spaced by brass standoff offsets.
- Every cut file lists: material, thickness, kerf setting, power/speed parameters used.

> [!NOTE]
> The LightBurn files are the planned primary mechanical source for Criterion 5 (Reproducibility). They are not in the repository yet; the [design](../../design/README.md) documentation tracks when they land.
