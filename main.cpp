#include <Servo.h>

// Ultrasonic sensor pins
int trigPin = 7;
int echoPin = 6;

// RGB LED pins
int red = 11;
int blue = 10;
int green = 9;

// Servo motor for barrier gate
int servoPin = 3;
Servo barrierGate;

// Buzzer pin
int buzzerPin = 12;

// Variables
long duration;
int distance;
bool spotOccupied = false;
int parkingThreshold = 15; // Distance in cm to detect car

void setup() {
    // Initialize pins
    pinMode(trigPin, OUTPUT);
    pinMode(echoPin, INPUT);
    pinMode(red, OUTPUT);
    pinMode(blue, OUTPUT);
    pinMode(green, OUTPUT);
    pinMode(buzzerPin, OUTPUT);
    
    // Initialize servo
    barrierGate.attach(servoPin);
    barrierGate.write(0); // Gate closed initially
    
    // Initialize serial communication
    Serial.begin(9600);
    
    // Initial status - parking available
    setRGB(0, 255, 0); // Green LED
    
    Serial.println("Smart Parking System Initialized");
    Serial.print("Parking threshold set to: ");
    Serial.print(parkingThreshold);
    Serial.println(" cm");
}

void loop() {
    // Measure distance using ultrasonic sensor
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
    
    duration = pulseIn(echoPin, HIGH);
    distance = duration * 0.034 / 2;
    
    // Print distance information
    Serial.print("Distance: ");
    Serial.print(distance);
    Serial.println(" cm");
    
    // Check parking status
    if (distance < parkingThreshold) {
        // Car detected - spot occupied
        if (!spotOccupied) {
            spotOccupied = true;
            Serial.println("OCCUPIED");
            setRGB(255, 0, 0); // Red LED
            
            // Sound buzzer to indicate car parked
            for (int i = 0; i < 2; i++) {
                digitalWrite(buzzerPin, HIGH);
                delay(200);
                digitalWrite(buzzerPin, LOW);
                delay(200);
            }
        } else {
            Serial.println("OCCUPIED");
        }
    }
    else if (distance >= parkingThreshold && distance < 100) {
        // No car detected - spot available
        if (spotOccupied) {
            spotOccupied = false;
            Serial.println("AVAILABLE");
            setRGB(0, 255, 0); // Green LED
            
            // Single beep to indicate car left
            digitalWrite(buzzerPin, HIGH);
            delay(500);
            digitalWrite(buzzerPin, LOW);
        } else {
            Serial.println("AVAILABLE");
        }
    }
    else {
        // Invalid reading (too far or sensor error)
        Serial.println("NO READING");
        setRGB(0, 0, 255); // Blue LED for error
    }
    
    // Check for manual gate control commands
    char command;
    if (Serial.available()) {
        command = Serial.read();
        
        switch (command) {
            case 'o': // Open gate
                barrierGate.write(90);
                Serial.println("Gate OPENED");
                setRGB(255, 255, 0); // Yellow LED
                delay(1000);
                break;
                
            case 'c': // Close gate
                barrierGate.write(0);
                Serial.println("Gate CLOSED");
                if (spotOccupied) {
                    setRGB(255, 0, 0); // Red
                } else {
                    setRGB(0, 255, 0); // Green
                }
                delay(1000);
                break;
                
            case 's': // Status request
                if (spotOccupied) {
                    Serial.println("STATUS:OCCUPIED");
                } else {
                    Serial.println("STATUS:AVAILABLE");
                }
                break;
                
            case 'r': // Reset system
                spotOccupied = false;
                barrierGate.write(0);
                setRGB(0, 255, 0);
                Serial.println("SYSTEM RESET");
                break;
                
            default:
                Serial.println("INVALID COMMAND");
                break;
        }
    }
    
    delay(500); // Check every 0.5 seconds
}

// Function to set RGB LED color
void setRGB(int redValue, int greenValue, int blueValue) {
    redValue = constrain(redValue, 0, 255);
    greenValue = constrain(greenValue, 0, 255);
    blueValue = constrain(blueValue, 0, 255);
    
    analogWrite(red, redValue);
    analogWrite(green, greenValue);
    analogWrite(blue, blueValue);
}
