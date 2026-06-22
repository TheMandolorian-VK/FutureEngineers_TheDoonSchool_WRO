# /*

WRO FUTURE ENGINEERS 2026
OBSTACLE CHALLENGE
==================

*/

// ==================================================
// LIBRARIES
// ==================================================

// #include <ESP32Servo.h>

// ==================================================
// PINOUTS
// ==================================================

// Steering Servo
const int SERVO_PIN = 13;

// Left Rear Motor
const int LEFT_PWM_PIN = 25;
const int LEFT_IN1_PIN = 26;
const int LEFT_IN2_PIN = 27;

// Right Rear Motor
const int RIGHT_PWM_PIN = 14;
const int RIGHT_IN1_PIN = 12;
const int RIGHT_IN2_PIN = 33;

// ==================================================
// HARDWARE OBJECTS
// ==================================================

// Servo steeringServo;

// ==================================================
// VEHICLE CONSTANTS
// ==================================================

const int SERVO_CENTER = 90;

const int MAX_LEFT_STEERING  = -30;
const int MAX_RIGHT_STEERING = 30;

const int MAX_SPEED = 255;

// ==================================================
// PI INPUT VARIABLES
// ==================================================

// Main output from Pi
float steeringAngle = 0;

// Speed command
int driveSpeed = 0;

// ==================================================
// OBSTACLE VARIABLES
// ==================================================

bool redPillarDetected = false;
bool greenPillarDetected = false;

int redPillarX = 0;
int greenPillarX = 0;

float redPillarDistance = 0;
float greenPillarDistance = 0;

// ==================================================
// STATE MACHINE
// ==================================================

enum VehicleState
{
DRIVING,

```
RED_PILLAR,

GREEN_PILLAR,

PARKING,

FINISHED
```

};

VehicleState currentState = DRIVING;

// ==================================================
// COMMUNICATION
// ==================================================

void receivePiData();

void parsePacket();

// ==================================================
// STEERING
// ==================================================

void initialiseSteering();

void setSteeringAngle(float angle);

void centerSteering();

// ==================================================
// MOTOR CONTROL
// ==================================================

void initialiseMotors();

void setMotorSpeed(int speed);

void stopVehicle();

// ==================================================
// OBSTACLE DETECTION
// ==================================================

void detectRedPillar();

void detectGreenPillar();

void estimatePillarPosition();

// ==================================================
// OBSTACLE AVOIDANCE
// ==================================================

void calculateRedAvoidance();

void calculateGreenAvoidance();

void returnToCenter();

// ==================================================
// PARKING
// ==================================================

void detectParkingZone();

void executeParking();

// ==================================================
// STATE HANDLERS
// ==================================================

void drivingState();

void redPillarState();

void greenPillarState();

void parkingState();

void finishedState();

// ==================================================
// DEBUGGING
// ==================================================

void printDebugData();

// ==================================================
// SETUP
// ==================================================

void setup()
{

}

// ==================================================
// LOOP
// ==================================================

void loop()
{

}
