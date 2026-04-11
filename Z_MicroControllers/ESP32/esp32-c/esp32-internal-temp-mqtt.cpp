// ESP32 internal temperature sensor → MQTT
// No external sensor needed — reads the ESP32's built-in hall/temp sensor
// Board: ESP32 Dev Module (note: not available on ESP32-S2/S3/C3)
// Libraries needed:
//   - PubSubClient (knolleary/pubsubclient)
//
// NOTE: The internal sensor is not calibrated for absolute accuracy (~±5°C).
//       It reflects chip temperature, not room temperature.
//       Useful for monitoring if the board is overheating.

#include <WiFi.h>
#include <PubSubClient.h>

#ifdef __cplusplus
extern "C" {
#endif
uint8_t temprature_sens_read();  // built-in ROM function (yes, typo is intentional)
#ifdef __cplusplus
}
#endif

// ---- LED ----
#define LED_BUILTIN 4  // GPIO4 — GPIO2 reserved on ESP32-WROOM-DA

// ---- Configuration ----
const char* WIFI_SSID     = "your-wifi";
const char* WIFI_PASSWORD = "your-password";
const char* MQTT_BROKER   = "192.168.1.2";
const int   MQTT_PORT     = 1883;
const int   PUBLISH_MS    = 5000;

// ---- MQTT Topic ----
const char* TOPIC_CHIP_TEMP = "esp32/temperature/internal";

WiFiClient espClient;
PubSubClient mqtt(espClient);

unsigned long lastPublish = 0;

float getInternalTempC() {
  // ROM function returns Fahrenheit
  return (temprature_sens_read() - 32) / 1.8f;
}

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
  connectWifi();
  connectMqtt();
}

void loop() {
  if (!mqtt.connected()) connectMqtt();
  mqtt.loop();

  unsigned long now = millis();
  if (now - lastPublish >= PUBLISH_MS) {
    lastPublish = now;

    float chipTemp = getInternalTempC();
    char tempStr[8];
    snprintf(tempStr, sizeof(tempStr), "%.2f", chipTemp);

    mqtt.publish(TOPIC_CHIP_TEMP, tempStr);
    Serial.printf("Published internal temp: %s °C\n", tempStr);
  }
}
