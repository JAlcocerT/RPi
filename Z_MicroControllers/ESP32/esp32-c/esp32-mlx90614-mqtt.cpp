// ESP32 + MLX90614 (GY-906) → MQTT
// Reads object (IR) and ambient temperature via I2C, publishes every 5s
// Board: ESP32 Dev Module  ← use this profile, not ESP32-WROOM-DA
// Libraries needed (Arduino IDE):
//   - Adafruit MLX90614  (Adafruit)
//   - Adafruit BusIO     (Adafruit) — pulled in automatically
//   - PubSubClient       (knolleary/pubsubclient)

#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <Adafruit_MLX90614.h>

#ifndef LED_BUILTIN
#define LED_BUILTIN 2  // GPIO2 — onboard LED on ESP32 Dev Module
#endif

// ---- Configuration ----
const char* WIFI_SSID     = "your-wifi";
const char* WIFI_PASSWORD = "your-password";  // const char* handles special chars ($, @, etc.)
const char* MQTT_BROKER   = "192.168.1.2";
const int   MQTT_PORT     = 1883;
const int   PUBLISH_MS    = 5000;

// I2C pins — ESP32 defaults (no need to change)
// SDA = GPIO21, SCL = GPIO22

// ---- MQTT Topics ----
const char* TOPIC_OBJ = "esp32/temperature/mlx/object";    // IR / non-contact
const char* TOPIC_AMB = "esp32/temperature/mlx/ambient";   // sensor board temp

Adafruit_MLX90614 mlx;
WiFiClient espClient;
PubSubClient mqtt(espClient);

unsigned long lastPublish = 0;
bool isConnected = false;

void connectMqtt() {
  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
  while (!mqtt.connected()) {
    Serial.print("Connecting to MQTT broker...");
    String clientId = "esp32-mlx-" + String(WiFi.macAddress());
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

  Wire.begin();  // SDA=21, SCL=22 by default
  if (!mlx.begin()) {
    Serial.println("MLX90614 not found — check wiring and I2C address (0x5A).");
    while (1) delay(500);  // halt
  }
  Serial.println("MLX90614 ready.");

  Serial.printf("Connecting to '%s'\n", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

void loop() {
  // ---- LED + WiFi state ----
  if (WiFi.status() == WL_CONNECTED && !isConnected) {
    Serial.printf("\nConnected — IP: %s\n", WiFi.localIP().toString().c_str());
    digitalWrite(LED_BUILTIN, HIGH);  // solid ON
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

  unsigned long now = millis();
  if (now - lastPublish >= PUBLISH_MS) {
    lastPublish = now;

    double objTemp = mlx.readObjectTempC();
    double ambTemp = mlx.readAmbientTempC();

    if (!isnan(objTemp) && !isnan(ambTemp)) {
      char objStr[8], ambStr[8];
      snprintf(objStr, sizeof(objStr), "%.2f", objTemp);
      snprintf(ambStr, sizeof(ambStr), "%.2f", ambTemp);

      mqtt.publish(TOPIC_OBJ, objStr);
      mqtt.publish(TOPIC_AMB, ambStr);

      Serial.printf("Published — Object: %s °C  Ambient: %s °C\n", objStr, ambStr);
    } else {
      Serial.println("MLX90614 read error — check wiring.");
    }
  }
}
