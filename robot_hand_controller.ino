/*
 * Robot Hand Controller for Arduino Uno
 * Receives serial data from Python MediaPipe controller
 * Controls 5 servos for basic hand movement
 * 
 * SERVO PIN CONNECTIONS (Arduino Uno):
 * ====================================
 * Servo 0 (Index Finger)    -> Pin 3
 * Servo 1 (Middle Finger)   -> Pin 5
 * Servo 2 (Ring Finger)     -> Pin 6
 * Servo 3 (Pinky Finger)    -> Pin 9
 * Servo 4 (Thumb)           -> Pin 10
 * 
 * Serial Protocol:
 * - Baud Rate: 115200
 * - Start bytes: 0xFE, 0xFE
 * - Data: 23 bytes (angle values 0-255)
 * - Checksum: 1 byte
 * - End bytes: 0xFD, 0xFD
 */

#include <Servo.h>

// Define number of servos
#define NUM_SERVOS 5

// Servo objects
Servo servos[NUM_SERVOS];

// Servo pin assignments
const int servoPins[NUM_SERVOS] = {3, 5, 6, 9, 10};

// Servo angle storage
int servoAngles[NUM_SERVOS] = {90, 90, 90, 90, 90}; // Initialize to middle position

// Serial communication variables
const byte START_BYTE = 0xFE;
const byte END_BYTE = 0xFD;
byte receivedData[23]; // All 23 joint angles from Python
int dataIndex = 0;
bool receivingData = false;
int startByteCount = 0;

// Map which angles from the 23 DOF array to use for our 5 servos
// You can customize this mapping based on which joints you want to control
const int servoMapping[NUM_SERVOS] = {
  0,  // Servo 0 -> Index finger knuckle flex (joint_angles[0])
  3,  // Servo 1 -> Middle finger knuckle flex (joint_angles[3])
  6,  // Servo 2 -> Ring finger knuckle flex (joint_angles[6])
  9,  // Servo 3 -> Pinky finger knuckle flex (joint_angles[9])
  12  // Servo 4 -> Thumb angle (joint_angles[12])
};

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  
  // Attach servos to pins
  for (int i = 0; i < NUM_SERVOS; i++) {
    servos[i].attach(servoPins[i]);
    servos[i].write(servoAngles[i]); // Set to initial position
  }
  
  // Wait for serial connection
  delay(1000);
  Serial.println("Robot Hand Controller Ready");
  Serial.print("Controlling ");
  Serial.print(NUM_SERVOS);
  Serial.println(" servos");
  Serial.println("Waiting for data...");
}

void loop() {
  if (Serial.available() > 0) {
    byte inByte = Serial.read();
    
    // Look for start sequence (two 0xFE bytes)
    if (inByte == START_BYTE) {
      startByteCount++;
      if (startByteCount >= 2) {
        receivingData = true;
        dataIndex = 0;
        startByteCount = 0;
      }
    } 
    // Receiving data
    else if (receivingData && dataIndex < 23) {
      receivedData[dataIndex] = inByte;
      dataIndex++;
      
      // If we've received all 23 bytes
      if (dataIndex >= 23) {
        receivingData = false;
        
        // Wait for checksum (1 byte) - we'll read it but not validate for simplicity
        while (Serial.available() < 1) {
          delay(1);
        }
        byte checksum = Serial.read();
        
        // Wait for end bytes (two 0xFD bytes)
        while (Serial.available() < 2) {
          delay(1);
        }
        byte end1 = Serial.read();
        byte end2 = Serial.read();
        
        // Verify end bytes
        if (end1 == END_BYTE && end2 == END_BYTE) {
          // Process the data and update servos
          updateServos();
        }
      }
    }
    // Reset if we get unexpected data
    else if (!receivingData && inByte != START_BYTE) {
      startByteCount = 0;
    }
  }
}

void updateServos() {
  // Map the received angles to our 5 servos
  for (int i = 0; i < NUM_SERVOS; i++) {
    int angleIndex = servoMapping[i];
    byte rawAngle = receivedData[angleIndex];
    
    // Convert 0-255 range to 0-180 degrees for servo
    int servoAngle = map(rawAngle, 0, 255, 0, 180);
    
    // Constrain to valid servo range
    servoAngle = constrain(servoAngle, 0, 180);
    
    // Update servo position
    servos[i].write(servoAngle);
    servoAngles[i] = servoAngle;
  }
  
  // Debug output (optional - comment out for better performance)
  /*
  Serial.print("Servos: ");
  for (int i = 0; i < NUM_SERVOS; i++) {
    Serial.print(servoAngles[i]);
    Serial.print(" ");
  }
  Serial.println();
  */
}
