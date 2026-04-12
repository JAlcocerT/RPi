// print??

#include <Arduino.h>



#define ledPin 2

void blink_led(unsigned int times, unsigned int duration){
  for (int i = 0; i < times; i++) {
    digitalWrite(ledPin, HIGH);
    delay(duration);
    digitalWrite(ledPin, LOW); 
    delay(200);
  }
}

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
}

void loop() {
  blink_led(3,200);
  // Print a message to the serial monitor
  Serial.print(F("Humidity: "));
  Serial.println(50); // Replace 50 with your humidity value

  delay(1000); // Delay for 1 second
}