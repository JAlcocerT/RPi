#include <OneWire.h>
#include <DallasTemperature.h>


//both works but weird values
#define ONE_WIRE_BUS 13 // D13
// #define ONE_WIRE_BUS 14  // D5 is GPIO14


OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);



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
  Serial.begin(9600);
  sensors.begin();
}

void loop() {
  sensors.requestTemperatures(); 
  
  digitalWrite(ledPin, HIGH);

  Serial.print("Celsius temperature: ");
  Serial.print(sensors.getTempCByIndex(0));
  Serial.print(" - Fahrenheit temperature: ");
  Serial.println(sensors.getTempFByIndex(0));
  
  blink_led(5,200);

  delay(1000);
}