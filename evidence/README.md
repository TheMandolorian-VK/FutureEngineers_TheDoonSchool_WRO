<div align="center">

# Evidence Archive

**A dated trail of real progress, observations, and engineering review.**

[← Project home](../README.md) · [Testing records](../docs/testing/README.md) · [Photos](../images/README.md)

</div>

---

This folder holds dated evidence that does not belong with final media: design reviews, calibration records, test summaries, and change records.

For every record, state the date, what was observed, the configuration used, and the next action.

## Evidence log

Status legend: **Analysis** (conclusion from design calculation or bench observation, raw record to be attached), **Planned** (scheduled, not yet run), **Measured** (dated raw record archived).

| # | Date | Type | Summary | Status | Link |
| --- | --- | --- | --- | --- | --- |
| E1 | 2026-08-01 | Steering sweep | 31° vs 40° lock-angle comparison; 40° clears the 600 mm corridor with ~80 mm margin (design analysis from prototype notes; dated sweep log pending) | Analysis | journal 04, [steering geometry](../design/ackermann_geometry.md) |
| E2 | 2026-08-03 | Driver comparison | L298N dropout ~1.8 V vs TB6612FNG ~0.4 V at stall → driver changed | Analysis | journal 06 |
| E3 | 2026-08-05 | Power bench test | Brown-out observed on a single shared battery → power separation adopted (two-battery design, later superseded by the single-pack two-rail design) | Analysis | journal 07 (historical), journal 11 (current) |
| E4 | 2026-08-09 | Sensor bench | VL53L0X median filter expected to improve stability on a white mat at 15° mount (to be verified when the ToF is wired) | Planned | journal 08, testing T6 |
| E5 | 2026-08-11 | Software | ESP32 serial protocol + fail-safe (timeout → `MODE_FAULT`) | Planned | testing T5 |

> [!NOTE]
> The archive grows as the development cycle continues. Evidence is added when observed: simulated or predicted results are never recorded as physical-test evidence.

> [!IMPORTANT]
> No raw evidence files (photographs, data logs, or videos) are present in this archive yet. They will be archived here as the vehicle is built and tested, and only observed results will ever be recorded. Rows marked **Analysis** or **Planned** have no raw record attached yet.
