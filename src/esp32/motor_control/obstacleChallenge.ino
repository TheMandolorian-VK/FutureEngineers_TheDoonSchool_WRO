/*
 * ============================================================
 * WRO FUTURE ENGINEERS 2026
 * THE DOON SCHOOL
 *
 * ESP32 LOW-LEVEL VEHICLE CONTROLLER
 * Version: 1.0
 * ============================================================
 *
 * HARDWARE
 * --------
 * MCU:
 *   ESP32
 *
 * STEERING:
 *   MG996R servo
 *
 * DRIVE:
 *   1x N20 geared DC motor
 *   6 V
 *   600 RPM
 *   Mechanically connected to both rear wheels
 *
 * MOTOR DRIVER:
 *   TB6612FNG
 *
 * COMMUNICATION:
 *   Raspberry Pi 4B <-> ESP32
 *   USB Serial
 *
 * ARCHITECTURE
 * ------------
 * Raspberry Pi:
 *   - Computer vision
 *   - Line detection
 *   - Pillar detection
 *   - IMU processing
 *   - ToF processing
 *   - PD steering
 *   - High-level navigation
 *
 * ESP32:
 *   - Receive command
 *   - Validate command
 *   - Set steering
 *   - Set motor speed
 *   - Communication timeout safety
 *
 * ============================================================
 */

/* ============================================================
 * LIBRARIES
 * ============================================================
 */

#include <Arduino.h>
#include <ESP32Servo.h>

/* ============================================================
 * PINOUT
 * ============================================================
 *
 * These retain the useful pins from the original prototype.
 *
 * TB6612FNG:
 *   PWMA -> GPIO 25
 *   AIN1 -> GPIO 26
 *   AIN2 -> GPIO 27
 *   STBY -> GPIO 32
 *
 * MG996R:
 *   Signal -> GPIO 13
 *
 * STATUS:
 *   Green LED -> GPIO 2
 *   Red LED   -> GPIO 4
 *
 * IMPORTANT:
 *   TB6612 motor power and MG996R servo power should not be
 *   taken directly from an ESP32 GPIO.
 *
 * ============================================================
 */

// ----------------------------
// Steering
// ----------------------------

const int SERVO_PIN = 13;

// ----------------------------
// TB6612FNG - Channel A
// ----------------------------

const int MOTOR_PWM_PIN  = 25;
const int MOTOR_IN1_PIN  = 26;
const int MOTOR_IN2_PIN  = 27;
const int MOTOR_STBY_PIN = 32;

// ----------------------------
// Status LEDs
// ----------------------------

const int LED_GREEN_PIN = 2;
const int LED_RED_PIN   = 4;


/* ============================================================
 * SERVO CONFIGURATION
 * ============================================================
 */

Servo steeringServo;

// Mechanical steering command limits.
// These are logical steering angles, not guaranteed physical
// Ackermann angles until calibration is completed.

const float STEERING_MIN_DEG = -45.0f;
const float STEERING_MAX_DEG =  45.0f;

// Servo position corresponding to straight ahead.
const int SERVO_CENTER_DEG = 90;

// Safe initial pulse range.
// These should be calibrated on the actual MG996R installation.
const int SERVO_MIN_US = 1000;
const int SERVO_MAX_US = 2000;

float currentSteeringDeg = 0.0f;


/* ============================================================
 * MOTOR CONFIGURATION
 * ============================================================
 */

const int MOTOR_MAX_PWM = 255;

// Change these during physical calibration if the motor runs
// backwards relative to the commanded direction.
const bool MOTOR_REVERSED = false;

int currentMotorPWM = 0;


/* ============================================================
 * SERIAL CONFIGURATION
 * ============================================================
 */

const unsigned long SERIAL_BAUD = 115200;

// Maximum allowed time without a valid command.
//
// The Pi will continuously send commands while the vehicle is
// running. If communication stops for this period, the ESP32
// stops the motor and centers the steering.

const unsigned long COMMAND_TIMEOUT_MS = 300;

unsigned long lastValidCommandTime = 0;


/* ============================================================
 * SERIAL INPUT BUFFER
 * ============================================================
 */

const size_t SERIAL_BUFFER_SIZE = 128;

char serialBuffer[SERIAL_BUFFER_SIZE];
size_t serialBufferIndex = 0;


/* ============================================================
 * VEHICLE MODES
 * ============================================================
 *
 * The Pi decides what the robot should be doing.
 *
 * DRIVE:
 *   Normal autonomous driving.
 *
 * PARK:
 *   Parking manoeuvre commanded by Pi.
 *
 * STOP:
 *   Immediate stop.
 *
 * FINISH:
 *   Run completed; remain stopped.
 *
 * FAULT:
 *   Internal communication timeout / invalid operating state.
 *
 * ============================================================
 */

enum VehicleMode
{
    MODE_DRIVE,
    MODE_PARK,
    MODE_STOP,
    MODE_FINISH,
    MODE_FAULT
};

VehicleMode currentMode = MODE_STOP;


/* ============================================================
 * FUNCTION DECLARATIONS
 * ============================================================
 */

// Hardware
void initialiseServo();
void initialiseMotorDriver();

void setSteeringAngle(float angleDeg);
void centerSteering();

void setMotorPWM(int pwm);
void stopMotor();

// Communication
void receiveSerial();
void processSerialLine(char *line);

bool parseCommand(char *line);
void processStopCommand();
void processPingCommand();

// Safety
void updateFailsafe();
void enterFaultState();

// Status
void updateStatusLEDs();
void printStatus();


/* ============================================================
 * SETUP
 * ============================================================
 */

void setup()
{
    Serial.begin(SERIAL_BAUD);

    pinMode(LED_GREEN_PIN, OUTPUT);
    pinMode(LED_RED_PIN, OUTPUT);

    digitalWrite(LED_GREEN_PIN, LOW);
    digitalWrite(LED_RED_PIN, HIGH);

    initialiseServo();
    initialiseMotorDriver();

    currentMode = MODE_STOP;

    stopMotor();
    centerSteering();

    lastValidCommandTime = millis();

    Serial.println();
    Serial.println("========================================");
    Serial.println("WRO FUTURE ENGINEERS 2026");
    Serial.println("THE DOON SCHOOL");
    Serial.println("ESP32 LOW-LEVEL CONTROLLER V1.0");
    Serial.println("========================================");
    Serial.println("READY");
}


/* ============================================================
 * MAIN LOOP
 * ============================================================
 */

void loop()
{
    receiveSerial();

    updateFailsafe();

    updateStatusLEDs();

    // Keep status output slow enough that it does not flood
    // the same serial interface used for commands.
    static unsigned long lastStatusTime = 0;

    if (millis() - lastStatusTime >= 1000)
    {
        lastStatusTime = millis();
        printStatus();
    }
}


/* ============================================================
 * SERVO INITIALISATION
 * ============================================================
 */

void initialiseServo()
{
    steeringServo.setPeriodHertz(50);

    steeringServo.attach(
        SERVO_PIN,
        SERVO_MIN_US,
        SERVO_MAX_US
    );

    centerSteering();
}


/* ============================================================
 * SERVO CONTROL
 * ============================================================
 */

void setSteeringAngle(float angleDeg)
{
    // Clamp logical command.
    angleDeg = constrain(
        angleDeg,
        STEERING_MIN_DEG,
        STEERING_MAX_DEG
    );

    currentSteeringDeg = angleDeg;

    /*
     * Convert:
     *
     * -45 deg -> 45 servo degrees
     *   0 deg -> 90 servo degrees
     * +45 deg -> 135 servo degrees
     */

    float servoAngle =
        SERVO_CENTER_DEG + angleDeg;

    servoAngle = constrain(
        servoAngle,
        45.0f,
        135.0f
    );

    steeringServo.write(
        (int)round(servoAngle)
    );
}


void centerSteering()
{
    currentSteeringDeg = 0.0f;

    steeringServo.write(
        SERVO_CENTER_DEG
    );
}


/* ============================================================
 * TB6612FNG INITIALISATION
 * ============================================================
 */

void initialiseMotorDriver()
{
    pinMode(MOTOR_PWM_PIN, OUTPUT);
    pinMode(MOTOR_IN1_PIN, OUTPUT);
    pinMode(MOTOR_IN2_PIN, OUTPUT);
    pinMode(MOTOR_STBY_PIN, OUTPUT);

    // Keep driver disabled during startup.
    digitalWrite(MOTOR_STBY_PIN, LOW);

    digitalWrite(MOTOR_IN1_PIN, LOW);
    digitalWrite(MOTOR_IN2_PIN, LOW);

    analogWrite(MOTOR_PWM_PIN, 0);
}


/* ============================================================
 * MOTOR CONTROL
 * ============================================================
 */

void setMotorPWM(int pwm)
{
    pwm = constrain(
        pwm,
        -MOTOR_MAX_PWM,
        MOTOR_MAX_PWM
    );

    if (MOTOR_REVERSED)
    {
        pwm = -pwm;
    }

    currentMotorPWM = pwm;

    // Enable TB6612.
    digitalWrite(MOTOR_STBY_PIN, HIGH);

    if (pwm > 0)
    {
        // Forward
        digitalWrite(MOTOR_IN1_PIN, HIGH);
        digitalWrite(MOTOR_IN2_PIN, LOW);

        analogWrite(
            MOTOR_PWM_PIN,
            pwm
        );
    }
    else if (pwm < 0)
    {
        // Reverse
        digitalWrite(MOTOR_IN1_PIN, LOW);
        digitalWrite(MOTOR_IN2_PIN, HIGH);

        analogWrite(
            MOTOR_PWM_PIN,
            -pwm
        );
    }
    else
    {
        stopMotor();
    }
}


/* ============================================================
 * MOTOR STOP
 * ============================================================
 */

void stopMotor()
{
    currentMotorPWM = 0;

    analogWrite(
        MOTOR_PWM_PIN,
        0
    );

    digitalWrite(MOTOR_IN1_PIN, LOW);
    digitalWrite(MOTOR_IN2_PIN, LOW);

    // Standby disables the H-bridge.
    digitalWrite(MOTOR_STBY_PIN, LOW);
}


/* ============================================================
 * SERIAL RECEIVE
 * ============================================================
 *
 * USB serial protocol:
 *
 * CMD,<steering_deg>,<motor_pwm>,<mode>
 *
 * Example:
 *
 * CMD,-12.5,180,DRIVE
 *
 * Meaning:
 *
 * steering = -12.5 degrees
 * motor    = PWM 180
 * mode     = DRIVE
 *
 * Additional commands:
 *
 * STOP
 * PING
 *
 * ============================================================
 */

void receiveSerial()
{
    while (Serial.available() > 0)
    {
        char incoming = (char)Serial.read();

        // Ignore CR from Windows-style line endings.
        if (incoming == '\r')
        {
            continue;
        }

        // End of packet.
        if (incoming == '\n')
        {
            serialBuffer[serialBufferIndex] = '\0';

            if (serialBufferIndex > 0)
            {
                processSerialLine(serialBuffer);
            }

            serialBufferIndex = 0;

            continue;
        }

        // Add character if there is room.
        if (serialBufferIndex < SERIAL_BUFFER_SIZE - 1)
        {
            serialBuffer[serialBufferIndex++] = incoming;
        }
        else
        {
            // Packet too large.
            serialBufferIndex = 0;

            Serial.println("ERR,BUFFER_OVERFLOW");
        }
    }
}


/* ============================================================
 * SERIAL COMMAND PROCESSING
 * ============================================================
 */

void processSerialLine(char *line)
{
    if (strncmp(line, "CMD,", 4) == 0)
    {
        if (parseCommand(line))
        {
            lastValidCommandTime = millis();

            Serial.println("ACK,CMD");
        }

        return;
    }

    if (strcmp(line, "STOP") == 0)
    {
        processStopCommand();
        return;
    }

    if (strcmp(line, "PING") == 0)
    {
        processPingCommand();
        return;
    }

    Serial.println("ERR,UNKNOWN_COMMAND");
}


/* ============================================================
 * COMMAND PARSER
 * ============================================================
 *
 * CMD,<steering_deg>,<motor_pwm>,<mode>
 *
 * Examples:
 *
 * CMD,0,150,DRIVE
 * CMD,-20,180,DRIVE
 * CMD,15,100,PARK
 * CMD,0,0,STOP
 *
 * ============================================================
 */

bool parseCommand(char *line)
{
    char *token;

    // ---------------------------------------------------------
    // Token 0: CMD
    // ---------------------------------------------------------

    token = strtok(line, ",");

    if (token == nullptr)
    {
        return false;
    }

    if (strcmp(token, "CMD") != 0)
    {
        return false;
    }

    // ---------------------------------------------------------
    // Token 1: steering angle
    // ---------------------------------------------------------

    token = strtok(nullptr, ",");

    if (token == nullptr)
    {
        Serial.println("ERR,MISSING_STEERING");
        return false;
    }

    float newSteering = atof(token);

    if (!isfinite(newSteering))
    {
        Serial.println("ERR,BAD_STEERING");
        return false;
    }

    // ---------------------------------------------------------
    // Token 2: motor PWM
    // ---------------------------------------------------------

    token = strtok(nullptr, ",");

    if (token == nullptr)
    {
        Serial.println("ERR,MISSING_SPEED");
        return false;
    }

    int newMotorPWM = atoi(token);

    if (
        newMotorPWM < -MOTOR_MAX_PWM ||
        newMotorPWM > MOTOR_MAX_PWM
    )
    {
        Serial.println("ERR,BAD_SPEED");
        return false;
    }

    // ---------------------------------------------------------
    // Token 3: mode
    // ---------------------------------------------------------

    token = strtok(nullptr, ",");

    if (token == nullptr)
    {
        Serial.println("ERR,MISSING_MODE");
        return false;
    }

    VehicleMode newMode;

    if (strcmp(token, "DRIVE") == 0)
    {
        newMode = MODE_DRIVE;
    }
    else if (strcmp(token, "PARK") == 0)
    {
        newMode = MODE_PARK;
    }
    else if (strcmp(token, "STOP") == 0)
    {
        newMode = MODE_STOP;
    }
    else if (strcmp(token, "FINISH") == 0)
    {
        newMode = MODE_FINISH;
    }
    else
    {
        Serial.println("ERR,BAD_MODE");
        return false;
    }

    // ---------------------------------------------------------
    // Apply command
    // ---------------------------------------------------------

    currentMode = newMode;

    // FINISH and STOP always override movement.
    if (
        currentMode == MODE_STOP ||
        currentMode == MODE_FINISH
    )
    {
        stopMotor();
        centerSteering();

        return true;
    }

    // Normal movement command.
    setSteeringAngle(newSteering);
    setMotorPWM(newMotorPWM);

    return true;
}


/* ============================================================
 * STOP COMMAND
 * ============================================================
 */

void processStopCommand()
{
    currentMode = MODE_STOP;

    stopMotor();
    centerSteering();

    lastValidCommandTime = millis();

    Serial.println("ACK,STOP");
}


/* ============================================================
 * PING
 * ============================================================
 */

void processPingCommand()
{
    Serial.println("PONG");
}


/* ============================================================
 * COMMUNICATION FAILSAFE
 * ============================================================
 */

void updateFailsafe()
{
    if (
        millis() - lastValidCommandTime
        > COMMAND_TIMEOUT_MS
    )
    {
        // Do not continuously modify the state if already stopped.
        if (currentMode != MODE_FAULT)
        {
            enterFaultState();
        }
    }
}


/* ============================================================
 * ENTER FAULT
 * ============================================================
 */

void enterFaultState()
{
    currentMode = MODE_FAULT;

    stopMotor();
    centerSteering();
}


/* ============================================================
 * STATUS LEDs
 * ============================================================
 */

void updateStatusLEDs()
{
    bool communicationOK =
        (
            millis() - lastValidCommandTime
            <= COMMAND_TIMEOUT_MS
        );

    if (
        communicationOK &&
        currentMode != MODE_FAULT
    )
    {
        digitalWrite(
            LED_GREEN_PIN,
            HIGH
        );

        digitalWrite(
            LED_RED_PIN,
            LOW
        );
    }
    else
    {
        digitalWrite(
            LED_GREEN_PIN,
            LOW
        );

        digitalWrite(
            LED_RED_PIN,
            HIGH
        );
    }
}


/* ============================================================
 * DEBUG STATUS
 * ============================================================
 */

void printStatus()
{
    Serial.print("STATUS,");

    Serial.print("mode=");

    switch (currentMode)
    {
        case MODE_DRIVE:
            Serial.print("DRIVE");
            break;

        case MODE_PARK:
            Serial.print("PARK");
            break;

        case MODE_STOP:
            Serial.print("STOP");
            break;

        case MODE_FINISH:
            Serial.print("FINISH");
            break;

        case MODE_FAULT:
            Serial.print("FAULT");
            break;
    }

    Serial.print(",");

    Serial.print("steering=");
    Serial.print(
        currentSteeringDeg,
        1
    );

    Serial.print(",");

    Serial.print("motor=");
    Serial.print(
        currentMotorPWM
    );

    Serial.print(",");

    Serial.print("age_ms=");
    Serial.println(
        millis() - lastValidCommandTime
    );
}