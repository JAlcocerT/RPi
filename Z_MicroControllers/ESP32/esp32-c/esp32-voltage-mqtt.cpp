// ESP32 supply/battery voltage → MQTT
// Reads voltage via a resistor voltage divider on GPIO35 (ADC1_CH7)
// GPIO35 is input-only and ADC1 — safe to use alongside WiFi
//
// ---- Wiring (voltage divider) ----
//
//   V_in ──┬── R1 (100kΩ) ──┬── R2 (100kΩ) ── GND
//           |                |
//           |              GPIO35
//           |           (ADC reading)
//
//   V_measured = ADC_voltage * (R1 + R2) / R2
//
//   With R1=R2=100kΩ: divides by 2 → safe for up to 6.6V input
//   Typical use: LiPo single cell (3.0V–4.2V) or USB 5V rail
//
// NOTE: The ESP32 ADC is not highly accurate (±5–10% typical).
//       For better accuracy, use esp_adc_cal calibration (see below).
//       ADC2 pins conflict with WiFi — always use ADC1 (GPIO32–GPIO39).
//
// Libraries needed:
//   - PubSubClient (knolleary/pubsubclient)

#include <WiFi.h>
#include <PubSubClient.h>
#include <esp_adc_cal.h>

// ---- Configuration ----
#define WIFI_SSID     "your-wifi"
#define WIFI_PASSWORD "your-password"
#define MQTT_BROKER   "192.168.1.2"
#define MQTT_PORT     1883
#define PUBLISH_MS    10000  // every 10s (voltage changes slowly)

// ---- ADC & Voltage Divider ----
#define ADC_PIN       35          // GPIO35 — ADC1, input-only, WiFi-safe
#define R1_KOHM       100.0f      // upper resistor (kΩ)
#define R2_KOHM       100.0f      // lower resistor (kΩ) — change if different
#define ADC_REF_MV    1100        // ESP32 internal reference (mV)
#define ADC_SAMPLES   16          // average multiple readings to reduce noise

// ---- MQTT Topic ----
const char* TOPIC_VOLTAGE = "esp32/voltage/supply";

WiFiClient espClient;
PubSubClient mqtt(espClient);
esp_adc_cal_characteristics_t adcChars;

unsigned long lastPublish = 0;

float readVoltage() {
    // Average multiple ADC samples to reduce noise
    uint32_t raw = 0;
    for (int i = 0; i < ADC_SAMPLES; i++) {
        raw += analogRead(ADC_PIN);
        delay(2);
    }
    raw /= ADC_SAMPLES;

    // Convert raw ADC to calibrated millivolts
    uint32_t mv = esp_adc_cal_raw_to_voltage(raw, &adcChars);

    // Scale back up through the voltage divider
    float voltage = mv / 1000.0f * (R1_KOHM + R2_KOHM) / R2_KOHM;
    return voltage;
}

void connectWifi() {
    Serial.printf("Connecting to %s", WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
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

    // Configure ADC: 12-bit, 0–3.3V range (attenuation 11dB → ~3.1V usable)
    analogReadResolution(12);
    analogSetAttenuation(ADC_11db);

    // Calibrate ADC using internal reference
    esp_adc_cal_characterize(ADC_UNIT_1, ADC_ATTEN_DB_11,
                             ADC_WIDTH_BIT_12, ADC_REF_MV, &adcChars);

    connectWifi();
    connectMqtt();
}

void loop() {
    if (!mqtt.connected()) connectMqtt();
    mqtt.loop();

    unsigned long now = millis();
    if (now - lastPublish >= PUBLISH_MS) {
        lastPublish = now;

        float voltage = readVoltage();
        char voltStr[8];
        snprintf(voltStr, sizeof(voltStr), "%.3f", voltage);

        mqtt.publish(TOPIC_VOLTAGE, voltStr);
        Serial.printf("Published supply voltage: %s V\n", voltStr);
    }
}
