# Design Decision Log

A dated record of the significant mechanical and system decisions, with the alternatives that were rejected and the reason. This is the evidence for Criterion 4 (engineering decisions) in the [docs hub](../docs/README.md). Decisions that were reversed are kept in the log with their supersession noted, because a decision log that hides reversals is not an honest engineering record.

Status legend: **adopted** (current), **superseded** (a later decision replaced it), **pending** (not yet executed).

| Date | Decision | Options considered | Chosen | Reason | Status |
| --- | --- | --- | --- | --- | --- |
| 12-08-26 | Chassis material | Plywood, acrylic, 3D-printed PLA/PETG, aluminium | 3 mm plywood | Lightest per stiffness on the school laser, damps motor vibration, does not crack at screw points | Adopted |
| 12-08-26 | Steering geometry | Parallel vs Ackermann | Ackermann | Inner wheel turns tighter, no tyre scrub, stable through 90° corners | Adopted |
| 12-08-26 | Steering actuator | One MG996R vs two motors | One MG996R | One steering actuator is the rule; servo torque suits the LEGO linkage | Adopted |
| 12-08-26 | Drive layout | Two motors (one per side) vs one N20 rear axle | One N20 rear axle | Simpler, fewer parts, single axle drives both wheels | Adopted |
| 12-08-26 | Rear wheel size | Equal wheels vs smaller rear wheels | ~30 mm rear, ~40 mm front | Rear bias lightens the drive end and gives a rearward tilt for cornering stability | Adopted |
| 12-08-26 | Mounting system | Dedicated drilled holes vs LEGO grid + brass standoffs | LEGO 8 mm grid + standoffs | Iterative by construction: move sensors/brackets in 8 mm steps without re-cutting the chassis | Adopted |
| 13-08-26 | Deck stack | Single deck vs double stack | Double stack | Uses the height envelope; battery low for CG, Pi/camera up for horizon | Adopted |
| 13-08-26 | Power architecture | Two batteries vs one 11 V 3S two-rail | One 11 V 3S two-rail | Single source, two rails (~6 V motor/servo, 5 V logic); see [electronics](../electronics/README.md) | Adopted (supersedes the earlier two-battery idea) |
| 13-08-26 | Steer angle | 31° vs 40° | 40° | Reaches the 600 mm corridor corners; PD softens the servo near lock | Adopted |
| 13-08-26 | Cadence | N/A | 31° then 40° | Prototype 1 at 31° was too wide for the sharp corners; prototype 2 set to 40° | Superseded by 40° |

## Notes

- Reversals are logged: the two-battery idea (13-08-26) was replaced by the single-pack two-rail design on the same day.
- New decisions are appended here with the current date, never edited into an older row, so the log stays chronological.

## Related documents

- [Design overview](README.md)
- [Engineering journal](../docs/engineering_journal/README.md)
- [Release notes](../docs/release_notes.md)
