# Competition Day Checklist

Team must complete before WRO 2026 (Aug 26-28). Items marked "Required" must be done to reach 25+ documentation score.

## Physical Evidence (Required)

- [ ] Real robot photos (minimum 5 angles: front, rear, left, right, top)
- [ ] Test run video - Open Challenge (3 laps)
- [ ] Test run video - Obstacle Challenge (3 laps + parking)
- [ ] Measured mass on digital scale
- [ ] Measured current draw per rail (multimeter)
- [ ] Actual turning radius (measured on mat)
- [ ] Wheel diameter (calipers)
- [ ] Steering angle at full lock (protractor)

## Code Integration (Required)

- [ ] IMU wired and `available=True` in code
- [ ] VL53L0X ToF wired and returning real distance
- [ ] Start-zone detector working
- [ ] Parking manoeuvre functional
- [ ] All placeholder interfaces replaced with real code

## Documentation (Required)

- [ ] `.lbrn` LightBurn master committed
- [ ] Full DXF deck patterns committed (replacing placeholder)
- [ ] Steering knuckle STL files committed
- [ ] Camera mount STL committed
- [ ] Real robot photos in `images/robot/`
- [ ] Test videos in `videos/`
- [ ] Test results logged in `docs/testing/README.md`
- [ ] Mass budget filled in `design/mass_budget.md`
- [ ] Power budget filled in `electronics/README.md`

## Competition Day

- [ ] Robot fits in 300x200x300mm envelope gauge
- [ ] Robot weighs under 1.5kg on official scale
- [ ] Both rear wheels receive torque (lifted test)
- [ ] Steering symmetric left/right
- [ ] No wireless communication active
- [ ] Battery fully charged
- [ ] Spare parts packed (spare N20, spare MG996R)
- [ ] USB cable for last-minute code upload
