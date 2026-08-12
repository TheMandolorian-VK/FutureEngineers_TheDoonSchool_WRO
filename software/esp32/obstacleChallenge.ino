/*
 * ============================================================
 * WRO FUTURE ENGINEERS 2026
 * THE DOON SCHOOL
 *
 * ESP32 LOW-LEVEL VEHICLE CONTROLLER
 * Version 2.0
 * ============================================================
 *
 * HARDWARE
 * --------
 * ESP32
 * MG996R steering servo
 * 1x N20 6V 600RPM drive motor
 * TB6612FNG motor driver
 *
 * COMMUNICATION
 * -------------
 * Raspberry Pi 4B <-> USB <-> ESP32
 * 115200 baud
 *
 * ARCHITECTURE
 * ------------
 * Raspberry Pi:
 *   - Camera perception
 *   - Orange/blue line detection
 *   - Red/green pillar detection
 *   - PD steering
 *   - IMU / ToF fusion
 *   - WRO navigation state
 *   - Lap counting
 *   - Parking
 *
 * ESP32:
 *   - Receive validated actuator commands
 *   - Control MG996R
 *   - Control single N20 through TB6612FNG
 *   - Communication watchdog
 *   - Emergency stop
 *
 * ============================================================
 */

#include <Arduino.h>
#include <ESP32Servo.h>

/* ============================================================
 * PINOUT
 * ============================================================
 */

// -------------------------
// MG996R steering
// -------------------------

const int SERVO_PIN = 13;

// -------------------------
// TB6612FNG Channel A
// -------------------------

const int MOTOR_PWM_PIN  = 25;
const int MOTOR_IN1_PIN  = 26;
const int MOTOR_IN2_PIN  = 27;
const int MOTOR_STBY_PIN = 32;

// -------------------------
// Status LEDs
// -------------------------

const int LED_GREEN_PIN = 2;
const int LED_RED_PIN   = 4;

/* ============================================================
 * SERIAL
 * ============================================================
 */

const unsigned long SERIAL_BAUD = 115200;

// Robot stops if the Pi disappears.
const unsigned long COMMAND_TIMEOUT_MS = 350;

// Debug output interval.
const unsigned long DEBUG_INTERVAL_MS = 1000;

/* ============================================================
 * STEERING
 * ============================================================
 */

Servo steeringServo;

const float STEERING_MIN_DEG = -45.0f;
const float STEERING_MAX_DEG =  45.0f;

const int SERVO_CENTER_DEG = 90;

// Conservative starting pulse range.
// Must be calibrated against the actual MG996R installation.
const int SERVO_MIN_US = 1000;
const int SERVO_MAX_US = 2000;

float currentSteeringDeg = 0.0f;

/*
 * Change to true if the physical steering direction is reversed.
 */
const bool STEERING_REVERSED = false;

/* ============================================================
 * DRIVE MOTOR
 * ============================================================
 */

const int MOTOR_MAX_PWM = 255;

/*
 * Change to true if the motor rotates opposite to the desired
 * forward direction.
 */
const bool MOTOR_REVERSED = false;

int currentMotorPWM = 0;

/* ============================================================
 * VEHICLE MODE
 * ============================================================
 */

enum VehicleMode
{
    MODE_STOP,
    MODE_DRIVE,
    MODE_PARK,
    MODE_FINISH,
    MODE_FAULT
};

VehicleMode currentMode = MODE_STOP;

/* ============================================================
 * COMMUNICATION WATCHDOG
 * ============================================================
 */

unsigned long lastValidCommandTime = 0;
unsigned long lastDebugTime = 0;

/* ============================================================
 * SERIAL INPUT BUFFER
 * ============================================================
 */

const size_t SERIAL_BUFFER_SIZE = 128;

char serialBuffer[SERIAL_BUFFER_SIZE];
size_t serialBufferIndex = 0;

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

bool parseDriveCommand(char *line);
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

    stopMotor();
    centerSteering();

    currentMode = MODE_STOP;

    lastValidCommandTime = millis();

    Serial.println();
    Serial.println("========================================");
    Serial.println("WRO FUTURE ENGINEERS 2026");
    Serial.println("THE DOON SCHOOL");
    Serial.println("ESP32 CONTROLLER V2.0");
    Serial.println("========================================");
    Serial.println("READY");
}

/* ============================================================
 * LOOP
 * ============================================================
 */

void loop()
{
    receiveSerial();

    updateFailsafe();

    updateStatusLEDs();

    if (
        millis() - lastDebugTime
        >= DEBUG_INTERVAL_MS
    )
    {
        lastDebugTime = millis();
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
    angleDeg = constrain(
        angleDeg,
        STEERING_MIN_DEG,
        STEERING_MAX_DEG
    );

    if (STEERING_REVERSED)
    {
        angleDeg = -angleDeg;
    }

    currentSteeringDeg = angleDeg;

    float servoPosition =
        SERVO_CENTER_DEG + angleDeg;

    servoPosition = constrain(
        servoPosition,
        45.0f,
        135.0f
    );

    steeringServo.write(
        (int)round(servoPosition)
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
 * TB6612 INITIALISATION
 * ============================================================
 */

void initialiseMotorDriver()
{
    pinMode(MOTOR_PWM_PIN, OUTPUT);
    pinMode(MOTOR_IN1_PIN, OUTPUT);
    pinMode(MOTOR_IN2_PIN, OUTPUT);
    pinMode(MOTOR_STBY_PIN, OUTPUT);

    digitalWrite(
        MOTOR_STBY_PIN,
        LOW
    );

    digitalWrite(
        MOTOR_IN1_PIN,
        LOW
    );

    digitalWrite(
        MOTOR_IN2_PIN,
        LOW
    );

    analogWrite(
        MOTOR_PWM_PIN,
        0
    );
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

    if (pwm == 0)
    {
        stopMotor();
        return;
    }

    digitalWrite(
        MOTOR_STBY_PIN,
        HIGH
    );

    if (pwm > 0)
    {
        digitalWrite(
            MOTOR_IN1_PIN,
            HIGH
        );

        digitalWrite(
            MOTOR_IN2_PIN,
            LOW
        );

        analogWrite(
            MOTOR_PWM_PIN,
            pwm
        );
    }
    else
    {
        digitalWrite(
            MOTOR_IN1_PIN,
            LOW
        );

        digitalWrite(
            MOTOR_IN2_PIN,
            HIGH
        );

        analogWrite(
            MOTOR_PWM_PIN,
            -pwm
        );
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

    digitalWrite(
        MOTOR_IN1_PIN,
        LOW
    );

    digitalWrite(
        MOTOR_IN2_PIN,
        LOW
    );

    digitalWrite(
        MOTOR_STBY_PIN,
        LOW
    );
}

/* ============================================================
 * USB SERIAL RECEIVE
 * ============================================================
 *
 * COMMAND:
 *
 * CMD,<steering_deg>,<motor_pwm>,<mode>
 *
 * Examples:
 *
 * CMD,0,150,DRIVE
 * CMD,-17.5,140,DRIVE
 * CMD,20,90,PARK
 * CMD,0,0,FINISH
 *
 * Emergency:
 *
 * STOP
 *
 * Test:
 *
 * PING
 *
 * ============================================================
 */

void receiveSerial()
{
    while (Serial.available() > 0)
    {
        char incoming =
            (char)Serial.read();

        if (incoming == '\r')
        {
            continue;
        }

        if (incoming == '\n')
        {
            serialBuffer[
                serialBufferIndex
            ] = '\0';

            if (serialBufferIndex > 0)
            {
                processSerialLine(
                    serialBuffer
                );
            }

            serialBufferIndex = 0;

            continue;
        }

        if (
            serialBufferIndex
            < SERIAL_BUFFER_SIZE - 1
        )
        {
            serialBuffer[
                serialBufferIndex++
            ] = incoming;
        }
        else
        {
            serialBufferIndex = 0;

            Serial.println(
                "ERR,BUFFER_OVERFLOW"
            );
        }
    }
}

/* ============================================================
 * PROCESS COMMAND
 * ============================================================
 */

void processSerialLine(char *line)
{
    if (
        strncmp(
            line,
            "CMD,",
            4
        ) == 0
    )
    {
        if (
            parseDriveCommand(line)
        )
        {
            lastValidCommandTime =
                millis();

            Serial.println(
                "ACK,CMD"
            );
        }

        return;
    }

    if (
        strcmp(
            line,
            "STOP"
        ) == 0
    )
    {
        processStopCommand();
        return;
    }

    if (
        strcmp(
            line,
            "PING"
        ) == 0
    )
    {
        processPingCommand();
        return;
    }

    Serial.println(
        "ERR,UNKNOWN_COMMAND"
    );
}

/* ============================================================
 * PARSE DRIVE COMMAND
 * ============================================================
 */

bool parseDriveCommand(
    char *line
)
{
    char *token;

    // CMD
    token = strtok(
        line,
        ","
    );

    if (
        token == nullptr
        ||
        strcmp(token, "CMD") != 0
    )
    {
        Serial.println(
            "ERR,BAD_PREFIX"
        );

        return false;
    }

    // Steering
    token = strtok(
        nullptr,
        ","
    );

    if (token == nullptr)
    {
        Serial.println(
            "ERR,MISSING_STEERING"
        );

        return false;
    }

    float newSteering =
        atof(token);

    if (!isfinite(newSteering))
    {
        Serial.println(
            "ERR,BAD_STEERING"
        );

        return false;
    }

    // Motor
    token = strtok(
        nullptr,
        ","
    );

    if (token == nullptr)
    {
        Serial.println(
            "ERR,MISSING_MOTOR"
        );

        return false;
    }

    int newMotorPWM =
        atoi(token);

    if (
        newMotorPWM
        < -MOTOR_MAX_PWM
        ||
        newMotorPWM
        > MOTOR_MAX_PWM
    )
    {
        Serial.println(
            "ERR,BAD_MOTOR"
        );

        return false;
    }

    // Mode
    token = strtok(
        nullptr,
        ","
    );

    if (token == nullptr)
    {
        Serial.println(
            "ERR,MISSING_MODE"
        );

        return false;
    }

    VehicleMode newMode;

    if (
        strcmp(
            token,
            "DRIVE"
        ) == 0
    )
    {
        newMode = MODE_DRIVE;
    }
    else if (
        strcmp(
            token,
            "PARK"
        ) == 0
    )
    {
        newMode = MODE_PARK;
    }
    else if (
        strcmp(
            token,
            "FINISH"
        ) == 0
    )
    {
        newMode = MODE_FINISH;
    }
    else if (
        strcmp(
            token,
            "STOP"
        ) == 0
    )
    {
        newMode = MODE_STOP;
    }
    else
    {
        Serial.println(
            "ERR,BAD_MODE"
        );

        return false;
    }

    currentMode = newMode;

    lastValidCommandTime =
        millis();

    if (
        currentMode == MODE_STOP
        ||
        currentMode == MODE_FINISH
    )
    {
        stopMotor();
        centerSteering();

        return true;
    }

    setSteeringAngle(
        newSteering
    );

    setMotorPWM(
        newMotorPWM
    );

    return true;
}

/* ============================================================
 * STOP
 * ============================================================
 */

void processStopCommand()
{
    currentMode = MODE_STOP;

    stopMotor();
    centerSteering();

    lastValidCommandTime =
        millis();

    Serial.println(
        "ACK,STOP"
    );
}

/* ============================================================
 * PING
 * ============================================================
 */

void processPingCommand()
{
    Serial.println(
        "PONG"
    );
}

/* ============================================================
 * FAILSAFE
 * ============================================================
 */

void updateFailsafe()
{
    if (
        millis()
        - lastValidCommandTime
        > COMMAND_TIMEOUT_MS
    )
    {
        if (
            currentMode
            != MODE_FAULT
        )
        {
            enterFaultState();
        }
    }
}

/* ============================================================
 * FAULT STATE
 * ============================================================
 */

void enterFaultState()
{
    currentMode =
        MODE_FAULT;

    stopMotor();
    centerSteering();
}

/* ============================================================
 * STATUS LED
 * ============================================================
 */

void updateStatusLEDs()
{
    bool healthy =
        (
            millis()
            - lastValidCommandTime
            <= COMMAND_TIMEOUT_MS
        );

    if (
        healthy
        &&
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
    Serial.print(
        "STATUS,mode="
    );

    switch (currentMode)
    {
        case MODE_STOP:
            Serial.print("STOP");
            break;

        case MODE_DRIVE:
            Serial.print("DRIVE");
            break;

        case MODE_PARK:
            Serial.print("PARK");
            break;

        case MODE_FINISH:
            Serial.print("FINISH");
            break;

        case MODE_FAULT:
            Serial.print("FAULT");
            break;
    }

    Serial.print(
        ",steering="
    );

    Serial.print(
        currentSteeringDeg,
        1
    );

    Serial.print(
        ",motor="
    );

    Serial.print(
        currentMotorPWM
    );

    Serial.print(
        ",command_age_ms="
    );

    Serial.println(
        millis()
        - lastValidCommandTime
    );
}