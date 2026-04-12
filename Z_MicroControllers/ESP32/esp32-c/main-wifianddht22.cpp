
// WIFI and DHT11??




#include <Arduino.h>
#include <WiFiMulti.h>

#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>

#define DHTPIN 23

//#define DHTTYPE DHT11
#define DHTTYPE DHT22

DHT_Unified dht(DHTPIN, DHTTYPE);

uint32_t delayMS;

#define WIFI_SSID "GiBWifi_EXT"
#define WIFI_PASSWORD "abcdefg1234"

WiFiMulti wifiMulti;



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
  pinMode(LED_BUILTIN, OUTPUT);

  wifiMulti.addAP(WIFI_SSID, WIFI_PASSWORD);

  while (wifiMulti.run() != WL_CONNECTED) {
    delay(100);
  }

  Serial.println("Connected");
  blink_led(10,200);
  Serial.println("Connected!!");
}

void loop() {
  //digitalWrite(LED_BUILTIN, WiFi.status() == WL_CONNECTED);
    // Delay between measurements.
  digitalWrite(LED_BUILTIN, HIGH);
  //delay(delayMS);
  delay(3000);

  // Get temperature event and print its value.
  sensors_event_t event;

  dht.temperature().getEvent(&event);
  if (isnan(event.temperature)) {
    Serial.println(F("Error reading temperature!"));
  }
  else {
    Serial.print(F("Temperature: "));
    Serial.print(event.temperature);
    Serial.println(F("°C"));
  }
  delay(3000);
  // Get humidity event and print its value.
  dht.humidity().getEvent(&event);
  if (isnan(event.relative_humidity)) {
    Serial.println(F("Error reading humidity!"));
  }
  else {
    Serial.print(F("Humidity: "));
    Serial.print(event.relative_humidity);
    Serial.println(F("%"));
  }
  
  digitalWrite(LED_BUILTIN, LOW);
  delay(3000);
}