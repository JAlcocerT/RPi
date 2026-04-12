// ESP32 + DHT11 → MQTT
// Improved version of esp32-dht11.cpp — adds WiFi + MQTT publishing
// Board: ESP32 Dev Module  ← use this profile, not ESP32-WROOM-DA
// Libraries needed (Arduino IDE):
//   - DHTesp      (beegee-tokyo/DHT-sensor-library-for-ESPx)
//   - PubSubClient (knolleary/pubsubclient)

#include <WiFi.h>
#include <PubSubClient.h>
#include "DHTesp.h"

// ---- LED ----
#define LED_BUILTIN 4  // GPIO4 — GPIO2 reserved on ESP32-WROOM-DA

// ---- Configuration ----
const char* WIFI_SSID     = "your-wifi";
const char* WIFI_PASSWORD = "your-password";  // const char* handles special chars ($, @, etc.)
const char* MQTT_BROKER   = "192.168.1.2";
const int   MQTT_PORT     = 1883;
const int   DHT_PIN       = 15;
const int   PUBLISH_MS    = 5000;

// ---- MQTT Topics ----
const char* TOPIC_TEMP = "esp32/temperature/dht11";
const char* TOPIC_HUMI = "esp32/humidity/dht11";

DHTesp dht;
WiFiClient espClient;
PubSubClient mqtt(espClient);

unsigned long lastPublish = 0;

void connectWifi() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.printf("Connecting to '%s'\n", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));  // blink while connecting
    delay(500);
    Serial.print(".");
  }
  digitalWrite(LED_BUILTIN, HIGH);  // solid ON once connected
  Serial.printf("\nConnected — IP: %s\n", WiFi.localIP().toString().c_str());
}

void connectMqtt() {
  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
  while (!mqtt.connected()) {
    Serial.print("Connecting to MQTT broker...");
    String clientId = "esp32-" + String(WiFi.macAddress());
    if (mqtt.connect(clientId.c_str())) {
      Serial.println(" connected.");
    } else {
      Serial.printf(" failed (rc=%d), retrying in 5s\n", mqtt.state());
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  dht.setup(DHT_PIN, DHTesp::DHT11);
  connectWifi();
  connectMqtt();
}

void loop() {
  if (!mqtt.connected()) connectMqtt();
  mqtt.loop();

  unsigned long now = millis();
  if (now - lastPublish >= PUBLISH_MS) {
    lastPublish = now;

    TempAndHumidity data = dht.getTempAndHumidity();

    if (!isnan(data.temperature) && !isnan(data.humidity)) {
      char tempStr[8], humiStr[8];
      snprintf(tempStr, sizeof(tempStr), "%.2f", data.temperature);
      snprintf(humiStr, sizeof(humiStr), "%.1f", data.humidity);

      mqtt.publish(TOPIC_TEMP, tempStr);
      mqtt.publish(TOPIC_HUMI, humiStr);

      Serial.printf("Published — Temp: %s °C  Humi: %s %%\n", tempStr, humiStr);
    } else {
      Serial.println("DHT11 read error — check wiring.");
    }
  }
}
