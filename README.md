# SMART PARKING DETCETION
A simple project using Ardunio. Here, we will be using cpp for the coding part and python for the controlling.


#FEATURES

Ultrasonic sensor measures the distance in front of it.

If the distance is less than 15 cm, a car is detected → parking spot is OCCUPIED.

If the distance is more than 15 cm (but less than 100 cm), the spot is AVAILABLE.

If the distance is too far or invalid, it shows NO READING.

RGB LED colors show the parking status:

🟢 Green → Parking available

🔴 Red → Parking occupied

🔵 Blue → Sensor error

🟡 Yellow → Gate is open

Buzzer sounds:

Two short beeps when a car parks.

One long beep when a car leaves.

Barrier gate (servo motor):

Controlled manually through serial commands.

'o' → Open gate

'c' → Close gate

's' → Show current status (occupied/available)

'r' → Reset system

Serial Monitor messages:

Continuously shows distance readings.

Displays status updates like "OCCUPIED", "AVAILABLE", "Gate OPENED", etc.


#COMPONENTS
- Arduino board
- Ultrasonic sensor (HC-SR04)
- RGB LED
- Servo motor
- Buzzer
- Jumper wires & breadboard


