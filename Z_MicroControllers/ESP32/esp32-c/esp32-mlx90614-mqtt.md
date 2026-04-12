# ESP32 + MLX90614 (GY-906) → MQTT

Reads object (IR non-contact) and ambient temperature via I2C, publishes to MQTT every 5 seconds.

---

## Wiring — GY-906 (4-pin module)

```
GY-906       ESP32-WROOM-DA
──────       ──────────────
VCC    →     3.3V
GND    →     GND
SDA    →     GPIO21  (default I2C SDA)
SCL    →     GPIO22  (default I2C SCL)
```

| GY-906 Pin | ESP32 Pin | Notes |
|------------|-----------|-------|
| VCC | 3.3V | Do not use 5V — damages sensor |
| GND | GND | |
| SDA | GPIO21 | Default I2C SDA on ESP32 |
| SCL | GPIO22 | Default I2C SCL on ESP32 |

> The MLX90614 I2C address is **0x5A** (factory default, not configurable on GY-906).

> No pull-up resistors needed — the GY-906 module has 4.7kΩ pull-ups built in on SDA and SCL.

---

## MLX90614 — Object vs Ambient

| Reading | Method | Meaning |
|---------|--------|---------|
| Object temp | `mlx.readObjectTempC()` | Temperature of what the sensor is pointed at (IR, non-contact) |
| Ambient temp | `mlx.readAmbientTempC()` | Temperature of the sensor board itself |

- Measurement range: **-70°C to +380°C** (object), **-40°C to +125°C** (ambient)
- Accuracy: **±0.5°C** in the 0–50°C range
- Field of view: **90°** (GY-906 standard lens)

---

## Arduino IDE setup

1. Board: **ESP32 Dev Module** (`Tools → Board`)
   > Do NOT use "ESP32-WROOM-DA Module" — causes WiFi issues
2. Port: **COM4** (or whichever port shows in `Tools → Port`)
3. Libraries (`Tools → Manage Libraries`):
   - `Adafruit MLX90614 Library` by Adafruit
   - `Adafruit BusIO` by Adafruit (installed automatically as dependency)
   - `PubSubClient` by Nick O'Leary
4. Edit credentials at top of file, then `Ctrl+U` to flash
5. Hold **BOOT** button during `Connecting......` if upload fails

---

## MQTT Topics

| Topic | Value |
|-------|-------|
| `esp32/temperature/mlx/object` | IR object temperature (°C, 2 decimal places) |
| `esp32/temperature/mlx/ambient` | Ambient board temperature (°C, 2 decimal places) |

Verify on your server:

```sh
mosquitto_sub -h 192.168.1.2 -t "esp32/temperature/mlx/#" -v
```

---

## LED behaviour

| State | LED (GPIO2) |
|-------|-------------|
| Connecting to WiFi | Blinking |
| Connected | Solid ON |

---

## Serial Monitor

Baud rate: **115200**

Expected output:

```
MLX90614 ready.
Connecting to 'your-wifi'
....
Connected — IP: 192.168.1.x
Connecting to MQTT broker... connected.
Published — Object: 24.50 °C  Ambient: 23.12 °C
Published — Object: 24.52 °C  Ambient: 23.13 °C
```

If sensor not found at boot:

```
MLX90614 not found — check wiring and I2C address (0x5A).
```
> The script halts here — it will not attempt WiFi or MQTT until the sensor is detected.

---

## I2C scan (optional debug)

If you suspect a wiring issue, flash this one-liner sketch to confirm the sensor is visible on the bus:

```cpp
#include <Wire.h>
void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.beginTransmission(0x5A);
  Serial.println(Wire.endTransmission() == 0 ? "MLX90614 found at 0x5A" : "Not found");
}
void loop() {}
```
 