// ESP32 + DHT11 -> EMQX (MQTT)
// Separate sketch with safer reconnect behavior for an EMQX broker in Docker.
// Board: ESP32 Dev Module
// Libraries needed (Arduino IDE):
//   - DHTesp
//   - PubSubClient

#include <WiFi.h>
#include <PubSubClient.h>
#include "DHTesp.h"

#ifndef LED_BUILTIN
#define LED_BUILTIN 2
#endif

// ---- WiFi ----
const char* WIFI_SSID     = "your-wifi";
const char* WIFI_PASSWORD = "your-password";

// ---- MQTT / EMQX ----
const char* MQTT_BROKER   = "192.168.1.106";
const int   MQTT_PORT     = 1883;
const char* MQTT_USERNAME = "";
const char* MQTT_PASSWORD = "";

// ---- Sensor ----
const int   DHT_PIN            = 4;
const int   PUBLISH_MS         = 5000;
const int   WIFI_RETRY_MS      = 10000;
const int   MQTT_RETRY_MS      = 5000;

// ---- MQTT Topics ----
const char* TOPIC_TEMP = "esp32/temperature/dht11";
const char* TOPIC_HUMI = "esp32/humidity/dht11";

DHTesp dht;
WiFiClient espClient;
PubSubClient mqtt(espClient);

unsigned long lastPublish = 0;
unsigned long lastWifiAttempt = 0;
unsigned long lastMqttAttempt = 0;
bool wifiLogged = false;

const char* mqttStateName(int state) {
  switch (state) {
    case MQTT_CONNECTION_TIMEOUT:     return "timeout";
    case MQTT_CONNECTION_LOST:        return "connection lost";
    case MQTT_CONNECT_FAILED:         return "connect failed";
    case MQTT_DISCONNECTED:           return "disconnected";
    case MQTT_CONNECTED:              return "connected";
    case MQTT_CONNECT_BAD_PROTOCOL:   return "bad protocol";
    case MQTT_CONNECT_BAD_CLIENT_ID:  return "bad client id";
    case MQTT_CONNECT_UNAVAILABLE:    return "server unavailable";
    case MQTT_CONNECT_BAD_CREDENTIALS:return "bad credentials";
    case MQTT_CONNECT_UNAUTHORIZED:   return "unauthorized";
    default:                          return "unknown";
  }
}

void beginWifi() {
  Serial.printf("Connecting to WiFi '%s'\n", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  lastWifiAttempt = millis();
}

void ensureWifi() {
  unsigned long now = millis();

  if (WiFi.status() == WL_CONNECTED) {
    if (!wifiLogged) {
      Serial.printf("WiFi connected, IP: %s\n", WiFi.localIP().toString().c_str());
      wifiLogged = true;
    }
    digitalWrite(LED_BUILTIN, HIGH);
    return;
  }

  wifiLogged = false;
  digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
  delay(150);

  if (now - lastWifiAttempt >= WIFI_RETRY_MS) {
    Serial.println("WiFi still down, retrying...");
    WiFi.disconnect();
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    lastWifiAttempt = now;
  }
}

void ensureMqtt() {
  if (WiFi.status() != WL_CONNECTED || mqtt.connected()) {
    return;
  }

  unsigned long now = millis();
  if (now - lastMqttAttempt < MQTT_RETRY_MS) {
    return;
  }
  lastMqttAttempt = now;

  String clientId = "esp32-dht11-" + WiFi.macAddress();
  bool connected;

  Serial.printf("Connecting to MQTT %s:%d ... ", MQTT_BROKER, MQTT_PORT);
  if (MQTT_USERNAME[0] != '\0') {
    connected = mqtt.connect(clientId.c_str(), MQTT_USERNAME, MQTT_PASSWORD);
  } else {
    connected = mqtt.connect(clientId.c_str());
  }

  if (connected) {
    Serial.println("connected.");
  } else {
    Serial.printf("failed, state=%d (%s)\n", mqtt.state(), mqttStateName(mqtt.state()));
  }
}

void publishReading() {
  TempAndHumidity data = dht.getTempAndHumidity();
  if (isnan(data.temperature) || isnan(data.humidity)) {
    Serial.println("DHT11 read error. Check wiring or sensor power.");
    return;
  }

  char tempStr[8];
  char humiStr[8];
  snprintf(tempStr, sizeof(tempStr), "%.2f", data.temperature);
  snprintf(humiStr, sizeof(humiStr), "%.1f", data.humidity);

  bool tempOk = mqtt.publish(TOPIC_TEMP, tempStr);
  bool humiOk = mqtt.publish(TOPIC_HUMI, humiStr);

  if (tempOk && humiOk) {
    Serial.printf("Published temp=%s C humi=%s %%\n", tempStr, humiStr);
  } else {
    Serial.println("Publish failed. MQTT connection may have dropped.");
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  dht.setup(DHT_PIN, DHTesp::DHT11);

  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
  mqtt.setKeepAlive(30);

  beginWifi();
}

void loop() {
  ensureWifi();
  ensureMqtt();

  if (!mqtt.connected()) {
    return;
  }

  mqtt.loop();

  unsigned long now = millis();
  if (now - lastPublish >= PUBLISH_MS) {
    lastPublish = now;
    publishReading();
  }
}
