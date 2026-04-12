// ESP32 + MH-Series IR Obstacle Sensor → MQTT
// Detects objects via infrared reflection — digital HIGH/LOW output
// Board: ESP32 Dev Module  ← use this profile, not ESP32-WROOM-DA
//
// No external library needed for the sensor — it's a plain digital read.
// The onboard LM393 comparator handles all signal processing.
//
// Libraries needed (Arduino IDE):
//   - PubSubClient (knolleary/pubsubclient)

#include <WiFi.h>
#include <PubSubClient.h>

#ifndef LED_BUILTIN
#define LED_BUILTIN 2  // GPIO2 — onboard LED on ESP32 Dev Module
#endif

// ---- Configuration ----
const char* WIFI_SSID     = "your-wifi";
const char* WIFI_PASSWORD = "your-password";  // const char* handles special chars ($, @, etc.)
const char* MQTT_BROKER   = "192.168.1.2";
const int   MQTT_PORT     = 1883;
const int   SENSOR_PIN    = 14;  // GPIO14 — safe pin, no boot functions
const int   PUBLISH_MS    = 5000;  // heartbeat: publish current state every 5s

// ---- MQTT Topics ----
// Value: "1" = object detected, "0" = path clear
const char* TOPIC_STATE = "esp32/ir/obstacle";
// Publishes a timestamp-equivalent event only when state changes
const char* TOPIC_EVENT = "esp32/ir/event";

WiFiClient espClient;
PubSubClient mqtt(espClient);

unsigned long lastPublish = 0;
bool isConnected  = false;
int  lastState    = -1;  // -1 = unknown, forces first publish on boot

void connectMqtt() {
  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
  while (!mqtt.connected()) {
    Serial.print("Connecting to MQTT broker...");
    String clientId = "esp32-ir-" + String(WiFi.macAddress());
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
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(SENSOR_PIN, INPUT);

  Serial.printf("Connecting to '%s'\n", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

void loop() {
  // ---- LED + WiFi state ----
  if (WiFi.status() == WL_CONNECTED && !isConnected) {
    Serial.printf("\nConnected — IP: %s\n", WiFi.localIP().toString().c_str());
    digitalWrite(LED_BUILTIN, HIGH);
    isConnected = true;
    connectMqtt();
  }

  if (WiFi.status() != WL_CONNECTED) {
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));  // blink while disconnected
    delay(500);
    isConnected = false;
    return;
  }

  // ---- MQTT + sensor (only runs when WiFi connected) ----
  if (!mqtt.connected()) connectMqtt();
  mqtt.loop();

  // LOW = object detected (sensor pulls output LOW when IR reflects back)
  int raw   = digitalRead(SENSOR_PIN);
  int state = (raw == LOW) ? 1 : 0;  // 1 = detected, 0 = clear

  // Publish immediately on state change (event-driven)
  if (state != lastState) {
    const char* stateStr = state ? "1" : "0";
    const char* eventStr = state ? "detected" : "clear";
    mqtt.publish(TOPIC_STATE, stateStr, true);  // retained — broker remembers last state
    mqtt.publish(TOPIC_EVENT, eventStr);
    Serial.printf("State change → %s\n", eventStr);
    lastState = state;
  }

  // Heartbeat: publish current state every PUBLISH_MS even if no change
  unsigned long now = millis();
  if (now - lastPublish >= PUBLISH_MS) {
    lastPublish = now;
    mqtt.publish(TOPIC_STATE, lastState ? "1" : "0", true);
    Serial.printf("Heartbeat — obstacle: %s\n", lastState ? "detected" : "clear");
  }
}
