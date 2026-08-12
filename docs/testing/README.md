<div align="center">

# Testing Records

**Plans, procedures, observations, and measured results.**

![WRO](https://img.shields.io/badge/WRO-2026-0057B8?style=for-the-badge&logo=robotframework&logoColor=white)
![Category](https://img.shields.io/badge/Category-Future%20Engineers-7A2E8E?style=for-the-badge)
![Tests](https://img.shields.io/badge/Tests-Planned-F59E0B?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Development%20Phase-F59E0B?style=for-the-badge)
![Updated](https://img.shields.io/badge/Updated-2026--08--13-555555?style=for-the-badge)

[← Documentation](../README.md) · [Evidence archive](../../evidence/README.md) · [Tuning log](../README.md)

</div>

---

Add a dated Markdown record for every physical or software test. State the objective, setup, hardware/software version, procedure, raw measurements or observations, outcome, and next action.

**Suggested filename:** `YYYY-MM-DD-short-test-name.md`

## Test plan summary

| # | Date | Test | Status | Result link |
| --- | --- | --- | --- | --- |
| T1 | 2026-08-01 | Servo sweep + steering range (31° vs 40°) | ✅ Done | steering sweep log |
| T2 | 2026-08-03 | Motor driver comparison: L298N vs TB6612FNG dropout | ✅ Done | journal entry 06 |
| T3 | 2026-08-06 | PD steering tuning on straight + corner | 🟡 In progress | `other/pid_tuning_log.md` |
| T4 | 2026-08-08 | Camera HSV detection under two lighting setups | 🟡 In progress | vision test log |
| T5 | 2026-08-10 | Serial protocol fail-safe (timeout → MODE_FAULT) | ⚪ Planned | N/A |
| T6 | 2026-08-12 | Wall-follow with VL53L0X in 600 mm corridor | ⚪ Planned | N/A |
| T7 | 2026-08-14 | Pillar pass logic (red right / green left) | ⚪ Planned | N/A |
| T8 | 2026-08-16 | Parallel parking sequence (camera + IMU + ToF) | ⚪ Planned | N/A |
| T9 | 2026-08-18 | Full Open Challenge: 3 laps + finish stop | ⚪ Planned | N/A |
| T10 | 2026-08-20 | Full Obstacle Challenge: 3 laps + pillars + parking | ⚪ Planned | N/A |

## Standard test procedure

1. Record date, software version (git hash), battery state, lighting.
2. Define pass/fail metric before running.
3. Run ≥5 repetitions; log all outcomes (pass/fail/partial).
4. Keep failing runs: they document the iteration cycle.
5. Link every result to a photo or video in `v-photos/` / `videos/`.

> [!IMPORTANT]
> Until a test is actually run, use a test plan and label it **Planned**. Do not add predicted values as results.

> [!NOTE]
> The vehicle is in the development and integration phase; results are added as tests are completed at the Doon School lab. Test evidence is recorded when measured, never assumed.
