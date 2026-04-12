# ESP32 + DHT11 → MQTT

Reads temperature and humidity from a DHT11 sensor and publishes to MQTT every 5 seconds.

---

## Wiring

```
DHT11        ESP32-WROOM-DA
─────        ──────────────
VCC    →     3.3V
DATA   →     GPIO15
NC     →     (not connected)
GND    →     GND
```

| DHT11 Pin | ESP32 Pin | Notes |
|-----------|-----------|-------|
| VCC (pin 1) | 3.3V | Do not use 5V — damages sensor |
| DATA (pin 2) | GPIO15 | No pull-up resistor needed — DHTesp handles it internally |
| NC (pin 3) | — | Not connected |
| GND (pin 4) | GND | |

> DHT11 pin order left to right (flat side facing you): VCC · DATA · NC · GND

---

## DHT11 vs DHT22

| | DHT11 | DHT22 |
|---|---|---|
| Temperature range | 0–50°C | -40–80°C |
| Humidity range | 20–80% | 0–100% |
| Accuracy (temp) | ±2°C | ±0.5°C |
| Accuracy (humi) | ±5% | ±2–5% |
| Sample rate | 1s | 2s |
| Price | cheaper | slightly more |

For most indoor use cases DHT11 is sufficient. Switch to DHT22 by changing one line:
```cpp
dht.setup(DHT_PIN, DHTesp::DHT22);  // was DHT11
```

---

## Arduino IDE setup

1. Board: **ESP32 Dev Module** (`Tools` → `Board`)
   > Do NOT use "ESP32-WROOM-DA Module" — GPIO2 gets reserved and blocks WiFi
2. Port: **COM4** (`Tools` → `Port`)
3. Libraries (`Tools` → `Manage Libraries`):
   - `DHT sensor library for ESPx` by beegee-tokyo
   - `PubSubClient` by Nick O'Leary
4. Edit credentials at top of file, then `Ctrl+U` to flash
5. Hold **BOOT** button when `Connecting......` appears if upload fails

---

## MQTT Topics

| Topic | Value |
|-------|-------|
| `esp32/temperature/dht11` | Temperature (°C, 2 decimal places) |
| `esp32/humidity/dht11` | Humidity (%, 1 decimal place) |

Verify on your server:
```sh
mosquitto_sub -h 192.168.1.2 -t "esp32/#" -v
```

---

## LED behaviour

| State | LED (GPIO4) |
|-------|-------------|
| Connecting to WiFi | Blinking |
| Connected | Solid ON |

> GPIO4 has no physical LED on the WROOM-DA board — behaviour only visible if you wire an external LED (+ resistor) between GPIO4 and GND.

---

## Serial Monitor

Baud rate: **115200**

Expected output:
```
Connecting to 'your-wifi'
....
Connected — IP: 192.168.1.x
Connecting to MQTT broker... connected.
Published — Temp: 23.00 °C  Humi: 45.0 %
Published — Temp: 23.00 °C  Humi: 45.0 %
```

Error output if sensor not wired:
```
DHT11 read error — check wiring.
```
