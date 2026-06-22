/*

WRO FUTURE ENGINEERS 2026
OBSTACLE CHALLENGE
ESP32 CODE V0.3
==================

*/

// ==================================================
// LIBRARIES
// ==================================================

#include <ESP32Servo.h>

// ==================================================
// PINOUTS
// ==================================================

// Steering Servo
const int SERVO_PIN = 13;

// Left Rear Motor
const int LEFT_PWM_PIN  = 25;
const int LEFT_IN1_PIN  = 26;
const int LEFT_IN2_PIN  = 27;

// Right Rear Motor
const int RIGHT_PWM_PIN = 14;
const int RIGHT_IN1_PIN = 12;
const int RIGHT_IN2_PIN = 33;

const int LED_GREED_PIN = 2;
const int LED_RED_PIN   = 4;

// ==================================================
// HARDWARE OBJECTS
// ==================================================

Servo steeringServo;

// ==================================================
// STEERING CONSTANTS
// ==================================================

const int SERVO_CENTER = 90;

const float MAX_LEFT_STEERING  = -45.0f;
const float MAX_RIGHT_STEERING =  45.0f;

const int MAX_SPEED = 255;

// ==================================================
// PI INPUT VARIABLES
// ==================================================

// Main output from Pi
float steeringAngle = 0;

// Speed command
int driveSpeed = 0;

// ==================================================
// OBSTACLE VARIABLES FROM PI
// ==================================================

bool redPillarDetected   = false;
bool greenPillarDetected = false;

int redPillarX   = 0;
int greenPillarX = 0;

float redPillarDistance   = 0;
float greenPillarDistance = 0;

// ==================================================
// STATE MACHINE
// ==================================================

enum VehicleState
{
  DRIVING,
  RED_PILLAR,
  GREEN_PILLAR,
  PARKING,
  FINISHED
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
  Serial.begin(115200);
  initialiseSteering();
  initialiseMotors();
}

// ==================================================
// LOOP
// ==================================================

void loop()
{
  receivePiData();

  switch (currentState)
  {
    case DRIVING:      drivingState();      break;
    case RED_PILLAR:   redPillarState();    break;
    case GREEN_PILLAR: greenPillarState();  break;
    case PARKING:      parkingState();      break;
    case FINISHED:     finishedState();     break;
  } 

  printDebugData();
}

// ==================================================
// COMMUNICATION
// ==================================================

void receivePiData()
{
  // TODO: read from Serial2 and populate variables
}

void parsePacket()
{
  // TODO: parse incoming data from Pi
}

// ==================================================
// STEERING
// ==================================================

void initialiseSteering()
{
  steeringServo.attach(SERVO_PIN);
  centerSteering();
}

void setSteeringAngle(float angle)
{
  if (angle < MAX_LEFT_STEERING)  angle = MAX_LEFT_STEERING;
  if (angle > MAX_RIGHT_STEERING) angle = MAX_RIGHT_STEERING;

  steeringServo.write(SERVO_CENTER + (int)angle);
}

void centerSteering()
{
  steeringServo.write(SERVO_CENTER);
}

// ==================================================
// MOTOR CONTROL
// ==================================================

void initialiseMotors()
{
  pinMode(LEFT_IN1_PIN,  OUTPUT);
  pinMode(LEFT_IN2_PIN,  OUTPUT);
  pinMode(RIGHT_IN1_PIN, OUTPUT);
  pinMode(RIGHT_IN2_PIN, OUTPUT);

  // ESP32 PWM setup
  ledcSetup(0, 5000, 8);
  ledcSetup(1, 5000, 8);
  ledcAttachPin(LEFT_PWM_PIN,  0);
  ledcAttachPin(RIGHT_PWM_PIN, 1);

  stopVehicle();
}

void setMotorSpeed(int speed)
{
  speed = constrain(speed, -MAX_SPEED, MAX_SPEED);

  if (speed >= 0)
  {
    digitalWrite(LEFT_IN1_PIN,  HIGH);
    digitalWrite(LEFT_IN2_PIN,  LOW);
    digitalWrite(RIGHT_IN1_PIN, HIGH);
    digitalWrite(RIGHT_IN2_PIN, LOW);
  }
  else
  {
    digitalWrite(LEFT_IN1_PIN,  LOW);
    digitalWrite(LEFT_IN2_PIN,  HIGH);
    digitalWrite(RIGHT_IN1_PIN, LOW);
    digitalWrite(RIGHT_IN2_PIN, HIGH);
    speed = -speed;
  }

  ledcWrite(0, speed);
  ledcWrite(1, speed);
}

void stopVehicle()
{
  digitalWrite(LEFT_IN1_PIN,  LOW);
  digitalWrite(LEFT_IN2_PIN,  LOW);
  digitalWrite(RIGHT_IN1_PIN, LOW);
  digitalWrite(RIGHT_IN2_PIN, LOW);
  ledcWrite(0, 0);
  ledcWrite(1, 0);
}

// ==================================================
// OBSTACLE DETECTION
// ==================================================

void detectRedPillar()
{
  // TODO
}

void detectGreenPillar()
{
  // TODO
}

// ==================================================
// OBSTACLE AVOIDANCE
// ==================================================

void calculateRedAvoidance()
{
  setSteeringAngle(MAX_RIGHT_STEERING);
}

void calculateGreenAvoidance()
{
  setSteeringAngle(MAX_LEFT_STEERING);
}

void returnToCenter()
{
  setSteeringAngle(steeringAngle);
}

// ==================================================
// PARKING
// ==================================================

void detectParkingZone()
{
  // TODO
}

void executeParking()
{
  stopVehicle();
  centerSteering();
}

// ==================================================
// STATE HANDLERS
// ==================================================

void drivingState()
{
  setSteeringAngle(steeringAngle);
  setMotorSpeed(driveSpeed);

  if (redPillarDetected)   currentState = RED_PILLAR;
  if (greenPillarDetected) currentState = GREEN_PILLAR;
}

void redPillarState()
{
  calculateRedAvoidance();
  setMotorSpeed(driveSpeed);

  if (!redPillarDetected)
  {
    returnToCenter();
    currentState = DRIVING;
  }
}

void greenPillarState()
{
  calculateGreenAvoidance();
  setMotorSpeed(driveSpeed);

  if (!greenPillarDetected)
  {
    returnToCenter();
    currentState = DRIVING;
  }
}

void parkingState()
{
  setSteeringAngle(steeringAngle);
  setMotorSpeed(driveSpeed);

  if (driveSpeed == 0)
  {
    executeParking();
    currentState = FINISHED;
  }
}

void finishedState()
{
  stopVehicle();
  centerSteering();
}

// ==================================================
// DEBUGGING
// ==================================================

void printDebugData()
{
  // TODO
}