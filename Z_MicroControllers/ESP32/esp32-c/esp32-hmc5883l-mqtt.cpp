// ESP32 + HMC5883L → MQTT
// Reads X/Y/Z magnetic field and calculates compass heading, publishes every 5s
// Board: ESP32 Dev Module  ← use this profile, not ESP32-WROOM-DA
//
// ⚠ IMPORTANT — many cheap modules labelled HMC5883L are actually QMC5883L clones.
//   Run the I2C scan in esp32-hmc5883l-mqtt.md to confirm your chip before flashing.
//   Genuine HMC5883L → address 0x1E → use this script + Adafruit library
//   QMC5883L clone   → address 0x0D → use QMC5883LCompass library instead (see .md)
//
// Libraries needed (Arduino IDE):
//   - Adafruit HMC5883 Unified  (Adafruit)
//   - Adafruit Unified Sensor   (Adafruit) — pulled in automatically
//   - Adafruit BusIO            (Adafruit) — pulled in automatically
//   - PubSubClient              (knolleary/pubsubclient)

#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_HMC5883_U.h>

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

// Magnetic declination for your location in radians.
// Find yours at: https://www.magnetic-declination.com
// Example: +2.5° → 0.0436   |   -3.1° → -0.0541
// Set to 0.0 if you only care about relative heading changes.
const float DECLINATION_RAD = 0.0;

// ---- MQTT Topics ----
const char* TOPIC_HEADING = "esp32/magnetometer/heading";  // compass bearing 0–360°
const char* TOPIC_X       = "esp32/magnetometer/x";        // µT
const char* TOPIC_Y       = "esp32/magnetometer/y";        // µT
const char* TOPIC_Z       = "esp32/magnetometer/z";        // µT

Adafruit_HMC5883_Unified mag(12345);  // ID is arbitrary, used internally by the library
WiFiClient espClient;
PubSubClient mqtt(espClient);

unsigned long lastPublish = 0;
bool isConnected = false;

void connectMqtt() {
  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
  while (!mqtt.connected()) {
    Serial.print("Connecting to MQTT broker...");
    String clientId = "esp32-mag-" + String(WiFi.macAddress());
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
  if (!mag.begin()) {
    Serial.println("HMC5883L not found — check wiring or chip (may be QMC5883L clone, see .md).");
    while (1) delay(500);  // halt
  }
  Serial.println("HMC5883L ready.");

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

  unsigned long now = millis();
  if (now - lastPublish >= PUBLISH_MS) {
    lastPublish = now;

    sensors_event_t event;
    mag.getEvent(&event);

    // Compass heading from X and Y axes
    float heading = atan2(event.magnetic.y, event.magnetic.x) + DECLINATION_RAD;
    if (heading < 0)       heading += 2 * PI;
    if (heading > 2 * PI)  heading -= 2 * PI;
    float headingDeg = heading * 180.0 / PI;

    char hStr[8], xStr[8], yStr[8], zStr[8];
    snprintf(hStr, sizeof(hStr), "%.1f", headingDeg);
    snprintf(xStr, sizeof(xStr), "%.2f", event.magnetic.x);
    snprintf(yStr, sizeof(yStr), "%.2f", event.magnetic.y);
    snprintf(zStr, sizeof(zStr), "%.2f", event.magnetic.z);

    mqtt.publish(TOPIC_HEADING, hStr);
    mqtt.publish(TOPIC_X, xStr);
    mqtt.publish(TOPIC_Y, yStr);
    mqtt.publish(TOPIC_Z, zStr);

    Serial.printf("Published — Heading: %s°  X: %s  Y: %s  Z: %s µT\n",
                  hStr, xStr, yStr, zStr);
  }
}
