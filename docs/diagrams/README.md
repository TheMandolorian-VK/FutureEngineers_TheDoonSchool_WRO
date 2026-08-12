<div align="center">

# Diagrams

**Architecture, wiring, and control-flow visualisations.**

[← Documentation](../README.md) · [Strategy](../../strategy/README.md) · [Hardware wiring](../../hardware/wiring-guide/README.md)

</div>

---

Each diagram is named by subject and version, and captioned **Proposed** (planned) or **Verified** (matches the built vehicle).

| Diagram | Type | Source | Status |
| --- | --- | --- | --- |
| Chassis cutting layout | LightBurn file (`.lbrn` + DXF) | Design records | Proposed |
| Chassis assembly / double-stack layout | LightBurn + annotated photo | Design records | In progress |
| Wiring flowchart | Mermaid + PDF export | [hardware/wiring-guide/](../../hardware/wiring-guide/README.md) | Verified |
| Power distribution flow | Mermaid | [hardware/wiring-guide/](../../hardware/wiring-guide/README.md) | Verified |
| System architecture (Pi ↔ ESP32 ↔ actuators) | Mermaid | [hardware/wiring-guide/](../../hardware/wiring-guide/README.md) | Verified |
| Software state machine | Mermaid | `strategy/` | Verified |
| Obstacle strategy flow (pillars, parking) | Mermaid | `strategy/` | Verified |

## Chassis cutting files (LightBurn)

The chassis is cut from **3 mm plywood** on the school's laser cutter using **LightBurn**.

- Source files: `.lbrn` project (editable) + exported DXF (portable) + PDF (print), stored with the design records.
- Two decks: lower deck (electronics, batteries) + upper deck (Pi + camera), spaced by brass standoff offsets.
- Every cut file lists: material, thickness, kerf setting, power/speed parameters used.

> [!NOTE]
> The LightBurn files are the primary mechanical source — they let another team reproduce the chassis exactly, which is what Criterion 5 (Reproducibility) requires.
