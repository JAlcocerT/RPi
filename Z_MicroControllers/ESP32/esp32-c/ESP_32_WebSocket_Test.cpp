#include <WiFi.h>
#include <AsyncTCP.h>
#include <AsyncWebSocket.h>

const char* ssid = "YourWiFiSSID";
const char* password = "YourWiFiPassword";

AsyncWebSocket ws("/ws");

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  ws.onEvent([](AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type, void *arg, uint8_t *data, size_t len) {
    if (type == WS_EVT_CONNECT) {
      Serial.println("WebSocket client connected");
    }
  });

  ws.begin();
}

void loop() {
  // Send data to WebSocket server periodically
  ws.textAll("Hello from ESP32!");
  delay(5000);
}
