# Release notes


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
