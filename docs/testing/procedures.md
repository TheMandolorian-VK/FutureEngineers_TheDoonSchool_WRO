# Test Procedures

Detailed methodology for each planned test (T1-T10). Every procedure defines the objective, setup, steps, pass criteria, and data to record. Tests are run at the Doon School lab; results land in the corresponding dated test file in this folder.

## T1: Servo sweep + steering range

- **Objective:** confirm the MG996R produces symmetric 40° outer lock and that the Ackermann inner/outer angle difference matches the design.
- **Setup:** vehicle on the bench (wheels off the ground), servo powered, Pi connected via USB serial.
- **Steps:**
  1. Send `CMD,-40,0,DRIVE` and photograph the steering linkage; measure outer-wheel angle with a protractor.
  2. Send `CMD,40,0,DRIVE` and repeat for the other side.
  3. At full lock, measure the inner-wheel angle and compute the Ackermann difference.
  4. Repeat 5 times and log all angles.
- **Pass criteria:** both sides reach 40° ± 2°; inner angle > outer angle (Ackermann condition met); symmetry within 3°.
- **Data to record:** protractor photos, measured angles, pass/fail per side, any binding or jitter.

## T2: Motor driver comparison

- **Objective:** measure voltage dropout of L298N vs TB6612FNG under the N20 motor load.
- **Setup:** bench power supply at 6 V, N20 motor, both drivers tested sequentially, multimeter across motor terminals.
- **Steps:**
  1. Wire the N20 to the L298N; run at full PWM; measure the voltage across the motor at stall and at free-run.
  2. Repeat with the TB6612FNG.
  3. Record dropout = supply voltage minus measured motor voltage.
- **Pass criteria:** TB6612FNG dropout < 0.5 V; L298N dropout > 1 V (confirming the design choice).
- **Data to record:** supply voltage, motor voltage at stall and free-run, dropout for each driver.

## T3: PD steering tuning

- **Objective:** tune KP and KD to minimise lateral oscillation on a straight and through a 90° corner.
- **Setup:** vehicle on the mat, camera on, corridor walls in place, serial log running.
- **Steps:**
  1. Start with KP=32, KD=10 (current values). Drive straight for 2 m. Log lateral offset and intervention count.
  2. Adjust KP in increments of 4; repeat. Find the KP that centres the vehicle with minimal oscillation.
  3. With optimal KP, adjust KD in increments of 2; repeat through a 90° corner. Find the KD that damps overshoot without adding jitter.
  4. Log all runs in the [PID tuning log](../other/pid_tuning_log.md).
- **Pass criteria:** straight-line drift < 50 mm over 2 m; corner entry/exit without wall contact.
- **Data to record:** KP/KD values, lateral offset, intervention count, pass/fail per run.

## T4: Camera HSV detection

- **Objective:** verify the camera detects red, green, purple (magenta), orange, and blue objects under fluorescent and spot lighting.
- **Setup:** each colour block placed at 0.5 m, 1.0 m, 1.5 m from the camera; two lighting conditions (fluorescent overhead, desk spot lamp).
- **Steps:**
  1. Place each colour block in turn; capture a frame; adjust the tolerance trackbar until detection is stable.
  2. Log the tolerance value and detection status (detected / not detected / intermittent) for each colour at each distance.
  3. Switch lighting and repeat.
- **Pass criteria:** all five colours detected at all three distances under both lighting conditions, with tolerance in the range 20-60.
- **Data to record:** colour, distance, lighting, tolerance, detection status, photos of the debug window.

## T5: Serial fail-safe

- **Objective:** confirm the ESP32 enters `MODE_FAULT` (motor stop + centred steering) within 350 ms of the last valid command.
- **Setup:** ESP32 powered, serial connected, motor and servo wired, green/red LEDs visible.
- **Steps:**
  1. Send `CMD,0,150,DRIVE` to start the motor running.
  2. Stop sending commands. Time the delay from the last command to the motor stopping (use a stopwatch or serial timestamp).
  3. Repeat 5 times.
- **Pass criteria:** motor stops and steering centres within 350 ms ± 50 ms on all 5 runs; red LED illuminates.
- **Data to record:** measured timeout per run, LED state, pass/fail.

## T6: VL53L0X wall-follow

- **Objective:** verify the VL53L0X provides stable distance readings in the 600 mm corridor and that the vehicle can maintain a consistent wall distance.
- **Setup:** 600 mm corridor walls, VL53L0X wired and mounted at ~15° downward, serial log running.
- **Steps:**
  1. Place the vehicle at the corridor entrance. Log the raw VL53L0X readings for 10 s while stationary.
  2. Drive through the corridor at 0.3 m/s. Log distance readings vs time.
  3. Compute mean distance, standard deviation, and any outlier readings.
- **Pass criteria:** standard deviation < 20 mm on a straight; no reading > 2 m (false positive check); 5-sample median filter reduces noise compared to raw.
- **Data to record:** raw and filtered distance logs, mean/std, pass/fail.

## T7: Pillar pass logic

- **Objective:** confirm the vehicle passes red pillars on the right and green pillars on the left using the +12° bias.
- **Setup:** corridor with one red and one green pillar placed at 1.0 m from the centre line, serial log + camera debug window running.
- **Steps:**
  1. Drive toward the red pillar. Log the steering angle and bias applied.
  2. Repeat with the green pillar.
  3. Place both pillars in view simultaneously; confirm the higher-scored pillar is selected.
- **Pass criteria:** red pillar → steering biased right (positive); green pillar → biased left (negative); no pillar contact.
- **Data to record:** pillar colour, steering angle, bias value, pass side, pass/fail.

## T8: Parallel parking

- **Objective:** confirm the vehicle enters the 20 cm parking lot parallel within the 2 cm tolerance, using camera + IMU + ToF (all integrated at this point).
- **Setup:** parking lot marked on the mat, IMU zeroed, ToF mounted, serial log running.
- **Steps:**
  1. Approach the lot at low speed. Send `CMD,0,75,PARK`.
  2. Log the final position and heading angle relative to the lot boundary.
  3. Repeat 5 times.
- **Pass criteria:** vehicle fully inside the lot, parallel within 2°, no contact with the purple blocks, on all 5 runs.
- **Data to record:** final heading angle, distance from lot boundary, block contact (yes/no), pass/fail per run.

## T9: Full Open Challenge

- **Objective:** complete 3 laps of the Open Challenge course and stop autonomously in the finish section.
- **Setup:** full course with walls, start/finish markers, serial log running, lap counter active.
- **Steps:**
  1. Start the vehicle at the start line. Let it run for 3 laps.
  2. Log lap times, intervention count (manual steering override needed?), and final stop position.
- **Pass criteria:** 3 laps completed within 3 minutes; autonomous stop in the finish section; no wall contact.
- **Data to record:** lap times, total time, intervention count, stop position, pass/fail.

## T10: Full Obstacle Challenge

- **Objective:** complete 3 laps with correct pillar passing (red right, green left) and park inside the lot.
- **Setup:** full course with walls, red and green pillars, parking lot, serial log running.
- **Steps:**
  1. Start the vehicle. Let it run for 3 laps + parking.
  2. Log lap times, pillar pass correctness, parking accuracy, intervention count.
- **Pass criteria:** 3 laps within 3 minutes; correct pillar passing on all laps; vehicle parked inside the lot parallel within 2°.
- **Data to record:** lap times, pillar pass results, parking accuracy, intervention count, pass/fail.

## Data recording standard

Every test produces one dated Markdown file (`YYYY-MM-DD-short-test-name.md`) using the template in the [testing README](README.md). Raw data (serial logs, photos, distance logs) are stored in [`images/testing/`](../../images/testing/README.md) and linked from the test file.
