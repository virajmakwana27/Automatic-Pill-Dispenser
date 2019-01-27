# Automatic-Pill-Dispenser
A pill dispensing machine which works using an android app, raspberry Pi and firebase. The user sets the time and amount of pills through the app and the pill dispenser dispenses the medicines at the set time.

Components required:
1.	Raspberry Pi 2 Model B
2.	Stepper Motor
3.	Serial Enabled LCD (16x2)
4.	IR sensor
5.	RTC module
6.	Electric Buzzer
7.	IC uln2003A
8.	Wires and Breadboard

A simple android app takes input from user regarding what pills he wants to the dispenser to dispense, and at what time. I have written the code for 2 different types of pills, but it can be extended for more than 2 types.

There is a method for taking input from firebase and getting time and pill information from it. Another method is for rotating the relevant motor to dispense pills.

The time and the pill information are displayed on the lcd. An alarm will ring when the pills are dispensed. If the user fails to collect the pills or there are no pills remaining in the dispenser, an e-mail will be sent to the user.
