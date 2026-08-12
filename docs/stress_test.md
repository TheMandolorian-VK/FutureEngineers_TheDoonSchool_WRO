<div align="center">

# Robot Stress-Test (Pre-Competition Engineering Assessment)

**Cold, real-world failure analysis of the WRO 2026 Future Engineers vehicle. No romanticised assumptions. Analytical only: contains no measured test results.**

[← Documentation](../README.md) · [Design](../design/README.md) · [Engineering journal](engineering_journal/README.md)

</div>

---

## Most Critical Vulnerability

The navigation stack depends on a single Raspberry Pi camera with **no encoder odometry**, so any glare, occlusion, or Pi hang blinds the car with zero fallback and forces a full-stop fault that loses the run.

## Friction Filter (worst-case deployment realities)

- Venue lighting differs from the lab; the white mat reflects; pillars cast shadows.
- One 11 V 3S LiPo cell imbalance kills the entire robot.
- LEGO joints flex under MG996R load, so steering drifts mid-run.
- Small rear wheels plus the rearward tilt shift mass forward, cutting rear traction, causing wheelspin and an inability to hold the parking pose.
- A Raspberry Pi 4B running OpenCV can hang over a three-minute run due to memory or thermal limits.

## System Deconstruction (SPOF table)

| # | SPOF | Worst-case failure | Hidden dependency |
| --- | --- | --- | --- |
| 1 | Vision-only localisation | Glare or washout misses the line or pillar, causing wrong steer or fault | No encoder; no second position source |
| 2 | LEGO Ackermann compliance | Servo deflects plastic joints, causing toe drift and an unheld 40 degree lock | Steering accuracy is a function of flex |
| 3 | Rear traction / single-motor axle | Weight-forward plus small wheels causes wheelspin and no parking hold | May drive only one rear wheel (rule risk) |
| 4 | Single 11 V 3S LiPo | Cell sag causes motor over or undervoltage; pack death is total loss | No redundant source; buck failure cascades |
| 5 | Pi to ESP32 USB serial | Pi hang drives ESP32 `MODE_FAULT` and stops the car | No heartbeat redundancy |
| 6 | VL53L0X on white mat | Reflective error at shallow angle gives bad parking depth | Parking depends on it |
| 7 | One driving axle rule | Only one rear wheel powered may be flagged non-compliant | WRO Rule 11.3 / 11.13 interpretation |

## Divergent Hard Re-Engineering

### SPOF 1: Vision with no odometry

- **Case A (tactical patch):** Lock exposure. Temporally average three frames. If colour confidence drops below threshold, hold the last good line and creep straight instead of faulting. Re-tune HSV at the venue on arrival.
- **Case B (structural override):** Mount a rear-wheel encoder for dead reckoning. Fuse encoder plus IMU plus vision. Camera loss no longer equals a stop.

### SPOF 2: LEGO steering compliance

- **Case A:** Replace LEGO at the servo horn with a rigid 3D-printed steering arm. Keep LEGO only as non-load mount rails. Tighten with friction pins.
- **Case B:** Replace the entire LEGO linkage with printed rigid Ackermann arms and metal ball joints. Use LEGO only for sensor positioning.

### SPOF 3: Rear traction and axle

- **Case A:** Bias battery weight rearward. Fit higher-traction rear tyres. Verify both rear wheels receive torque.
- **Case B:** Drive both rear wheels through a small differential or dual output. Document compliance. Add an encoder on the axle.

### SPOF 4: Single battery

- **Case A:** ESP32 reads pack voltage. Fit a LiPo alarm. Controlled stop below threshold. Balance-charge before every run.
- **Case B:** Split into motor and logic packs with automatic switchover, or add a supercapacitor buffer for logic during sag.

### SPOF 7: Rule compliance (highest priority, cheapest to verify)

- **Case A:** Physically confirm the gearbox drives both rear wheels. Photograph the axle.
- **Case B:** Add a visible mechanical link to both rear wheels if ambiguous. Document in `design/` and `evidence/`.

## Blind Spots (experts miss these)

- No measured lap time, mass, or centre of gravity yet, so all consistency claims are unverified.
- EMC: USB serial and motor PWM on one pack can inject noise into the IMU and camera.
- Mat friction coefficient is unknown, so torque and speed math is theoretical.
- Multi-robot ToF crosstalk if two cars run close together.
- Servo deadband and Ackermann are not the same angle per wheel; an uncalibrated link causes asymmetric cornering.
- Camera height vibration on a tilted wooden deck blurs the image at speed.

## Master Priority List (maximum return on effort, ordered)

1. **Confirm both rear wheels are driven** (rule plus traction). Cost: zero. Impact: existential.
2. **Add rear-wheel encoder odometry** (kills SPOF 1 and 3). Highest return.
3. **Rigidify steering** (kill LEGO compliance, SPOF 2).
4. **Venue-lighting fallback** in `wromain.py` (hold line, not fault).
5. **Battery voltage monitor and balance charge** (SPOF 4).
6. **Document all of the above truthfully** in the repository (`design/`, `evidence/`, journal).

## Next Immediate Friction Point

The build may currently drive only one rear wheel, and there may be no space for an encoder inside the 300 by 200 by 300 mm envelope.

**Follow-up question:** Does the N20 gearbox output currently drive both rear wheels, and is there physical clearance on the rear axle to mount a magnetic or optical encoder without breaching the envelope?

> This document is an analytical assessment. It states no measured results. Physical verification belongs in `docs/testing/README.md` and `evidence/README.md` as on-mat testing proceeds.
