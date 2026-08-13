# Release notes


## v0.6 (2026-08-13)

- Cleaned up overclaiming across all docs: removed "authoritative" DXF claims, softened rule-compliance language, marked all placeholders honestly.
- Added 5 Mermaid diagrams: system_architecture, state_machine, challenge_flow, wiring_overview, obstacle_strategy.
- Added CI link-check workflow (`.github/workflows/link-check.yml`).
- Added competition day checklist (`docs/competition_day_checklist.md`).
- Updated diagrams README to reflect committed Mermaid files.

## v0.5 (2026-08-13)

- Full cross-file consistency audit and fix: corrected every verifiable overclaim against the actual source code (`wromain.py`, `obstacleChallenge.ino`).
- Removed all invented mass, power, and torque estimates from design docs and journal; replaced with honest TBD measurement frameworks.
- Fixed challenge-flow description in root README: ToF/IMU/parking/start-zone are now clearly marked as planned, not implemented.
- Fixed strategy README: corrected wire-token statements, marked ToF/IMU-dependent behaviours as planned.
- Fixed evidence archive: added status column (Analysis/Planned/Measured); corrected E3 journal reference, E5 status.
- Fixed testing records: corrected T1/T4 result links, fixed `v-photos/` path.
- Fixed diagrams README: marked all non-existent diagrams as Planned (not Verified).
- Fixed wiring guide: marked LM317 as dropped (replaced by single-pack two-rail buck).
- Fixed journal entries 02, 03, 04, 07, 08, 09, 10, 11 for overclaims.
- Added mechanical BOM (`design/bom_mechanical.md`), Ackermann geometry spec, assembly guide, laser cutter setup, camera mount design, steering tuning plan, WRO rules checklist, design decision log, DXF notes, and mass budget framework.
- Added detailed test procedures (`docs/testing/procedures.md`) for T1-T10.
- Added software architecture deep-dive (`strategy/software_architecture.md`) grounded in actual code.
- Linked BOMs from root README.

## v0.4 (2026-08-13)

- Documentation consistency cleanup across all docs: removed decorative badges and emoji, aligned the serial protocol and power architecture descriptions, corrected broken links, and added an explicit rubric-to-criteria mapping.
- Power architecture restated consistently: single 11 V 3S LiPo driving two buck-regulated rails (motor/servo rail ~6 V, logic rail 5 V). The previously documented two-battery design (journal entry 07) is retained only as a historical record and is superseded by journal entry 11.
- Serial protocol restated consistently: the Pi sends wire tokens `DRIVE`, `PARK`, `FINISH`, `STOP`, and `PING`; the `MODE_*` names are internal ESP32 firmware states and are never sent on the wire.
- Added `docs/other/pid_tuning_log.md` as an honest, empty tuning template.

## v0.3 (2026-08-12)

- Engineering journal completed and mapped to the WRO 2026 evaluation rubric (all 5 criteria).
- Design documentation expanded: Ackermann steering geometry (31°→40° iteration), 3 mm plywood LightBurn chassis, double-stack layout (wood + LEGO + brass offsets).
- Power and sensor architecture documented: single 11 V 3S LiPo with two buck-regulated rails (motor/servo rail ~6 V, logic rail 5 V), TB6612FNG driver (replacing L298N), VL53L0X + HC-SR04 + MPU6050 + Camera Module 3 Wide sensor suite.
- Bill of materials published in `electronics/`.
- Testing framework and test plan (T1â€“T10) published.
- Robot visualizations labelled as AI-generated concept renders showing the intended competition-day look.
- Videos note: recordings are for competition day only; none made yet (vehicle in development stage): WRO India Team informed via calls/emails.

## v0.2 (2026-08-05)

- Wiring guide completed: power architecture, LM317 regulation stage, component interconnections, star grounding rules.
- Pi source reconstructed as `wromain.py` (vision + PD steering + ESP32 serial communication).
- ESP32 low-level controller reworked: serial protocol, `MODE_DRIVE/PARK/STOP/FINISH/FAULT` state machine.

## v0.1 (2026-07-15)

- Repository structure established for WRO Future Engineers documentation.
- Added evidence and documentation templates for design decisions, testing, diagrams, wiring, images, and videos.
- Robot visualizations are labelled as AI-generated concept renders, not physical-robot photographs.
