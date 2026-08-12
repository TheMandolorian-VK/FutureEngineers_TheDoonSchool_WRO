# Release notes

## v0.3 (2026-08-12)

- Engineering journal completed and mapped to the WRO 2026 evaluation rubric (all 5 criteria).
- Design documentation expanded: Ackermann steering geometry (31°→40° iteration), 3 mm plywood LightBurn chassis, double-stack layout (wood + LEGO + brass offsets).
- Power and sensor architecture documented: two-rail/two-battery design, TB6612FNG driver (replacing L298N), VL53L0X + HC-SR04 + MPU6050 + Camera Module 3 Wide sensor suite.
- Bill of materials published in `electronics/`.
- Testing framework and test plan (T1–T10) published.
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
