<div align="center">

# Evidence Archive

**A dated trail of real progress, observations, and engineering review.**

[← Project home](../README.md) · [Testing records](../docs/testing/README.md) · [Photos](../images/README.md)

</div>

---

This folder holds dated evidence that does not belong with final media: design reviews, calibration records, test summaries, and change records.

For every record, state the date, what was observed, the configuration used, and the next action.

## Evidence log

| # | Date | Type | Summary | Link |
| --- | --- | --- | --- | --- |
| E1 | 2026-08-01 | Steering sweep | 31° vs 40° lock-angle comparison; 40° clears the 600 mm corridor with ~80 mm margin | journal 04 |
| E2 | 2026-08-03 | Driver comparison | L298N dropout ~1.8 V vs TB6612FNG ~0.4 V at stall → driver changed | journal 06 |
| E3 | 2026-08-05 | Power bench test | Single-shared-battery brown-out observed → two-rail design adopted | journal 07 |
| E4 | 2026-08-09 | Sensor bench | VL53L0X median filter improves stability on white mat at 15° mount | journal 08 |
| E5 | 2026-08-11 | Software | ESP32 serial protocol + fail-safe verified on bench (MODE_FAULT on timeout) | testing T5 |

> [!NOTE]
> The archive grows as the development cycle continues. Evidence is added when observed: simulated or predicted results are never recorded as physical-test evidence.

> [!IMPORTANT]
> No raw evidence files (photographs, data logs, or videos) are present in this archive yet. They will be archived here as the vehicle is built and tested, and only observed results will ever be recorded.
