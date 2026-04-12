# ESP32 + HMC5883L → MQTT

Reads 3-axis magnetic field and compass heading via I2C, publishes to MQTT every 5 seconds.

---

## ⚠ HMC5883L vs QMC5883L — check your chip first

Most cheap 4-pin modules **labelled HMC5883L** are actually **QMC5883L clones**. 

They look identical but have different I2C addresses and require a different library.

| | HMC5883L (genuine) | QMC5883L (clone) |
|---|---|---|
| I2C address | **0x1E** | **0x0D** |
| Library | `Adafruit HMC5883 Unified` | `QMC5883LCompass` by MPrograms |
| Manufacturer | Honeywell | QST Corporation |

**Run this I2C scan first** to find out which you have:

```cpp
#include <Wire.h>
void setup() {
  Serial.begin(115200);
  Wire.begin();
  for (byte addr = 8; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0)
      Serial.printf("Device found at 0x%02X\n", addr);
  }
}
void loop() {}
```

- `0x1E` → genuine HMC5883L → use `esp32-hmc5883l-mqtt.cpp` as-is
- `0x0D` → QMC5883L clone → see **QMC5883L section** below

---

## Wiring (same for both chips)

```
HMC5883L     ESP32-WROOM-DA
────────     ──────────────
VCC    →     3.3V
GND    →     GND
SDA    →     GPIO21  (default I2C SDA)
SCL    →     GPIO22  (default I2C SCL)
```

| Module Pin | ESP32 Pin | Notes |
|------------|-----------|-------|
| VCC | 3.3V | Do not use 5V — check your module; some GY-273 boards have a 3.3V regulator and accept 5V on VCC |
| GND | GND | |
| SDA | GPIO21 | Default I2C SDA on ESP32 |
| SCL | GPIO22 | Default I2C SCL on ESP32 |

> No external pull-up resistors needed — the module has them built in.

---

## Arduino IDE setup

1. Board: **ESP32 Dev Module** (`Tools → Board`)
2. Port: whichever COM port shows (`Tools → Port`)
3. Libraries (`Tools → Manage Libraries`):
   - `Adafruit HMC5883 Unified` by Adafruit
   - `Adafruit Unified Sensor` by Adafruit (auto-installed as dependency)
   - `Adafruit BusIO` by Adafruit (auto-installed as dependency)
   - `PubSubClient` by Nick O'Leary
4. Edit credentials at top of file, set `DECLINATION_RAD` for your location
5. `Ctrl+U` to flash — hold **BOOT** if upload fails

---

## Magnetic declination

The sensor measures magnetic north, which differs from true geographic north by a location-specific angle called **declination**.

- Find your declination at [magnetic-declination.com](https://www.magnetic-declination.com)
- Convert degrees to radians: `degrees × π / 180`
- Enter as `DECLINATION_RAD` in the script

| Location example | Declination | DECLINATION_RAD |
|-----------------|-------------|-----------------|
| Madrid, Spain | +0.6° | 0.0105 |
| London, UK | -0.3° | -0.0052 |
| New York, USA | -13.0° | -0.2269 |
| Set to 0 | — | 0.0 (relative heading only) |

---

## MQTT Topics

| Topic | Value | Unit |
|-------|-------|------|
| `esp32/magnetometer/heading` | Compass bearing | degrees (0–360°) |
| `esp32/magnetometer/x` | X-axis field | µT (microtesla) |
| `esp32/magnetometer/y` | Y-axis field | µT |
| `esp32/magnetometer/z` | Z-axis field | µT |

Verify on your server:
```sh
mosquitto_sub -h 192.168.1.2 -t "esp32/magnetometer/#" -v
```

---

## Serial Monitor

Baud rate: **115200**

Expected output:
```
HMC5883L ready.
Connecting to 'your-wifi'
....
Connected — IP: 192.168.1.x
Connecting to MQTT broker... connected.
Published — Heading: 247.3°  X: -12.45  Y: 8.20  Z: -34.10 µT
Published — Heading: 248.1°  X: -12.51  Y: 8.18  Z: -34.05 µT
```

If sensor not found at boot:
```
HMC5883L not found — check wiring or chip (may be QMC5883L clone, see .md).
```

---

## For QMC5883L clones (address 0x0D)

Install `QMC5883LCompass` by MPrograms from the library manager, then replace the relevant parts:

```cpp
#include <QMC5883LCompass.h>
QMC5883LCompass compass;

// in setup():
compass.init();

// in loop():
compass.read();
int x   = compass.getX();
int y   = compass.getY();
int z   = compass.getZ();
int hdg = compass.getAzimuth();  // 0–360°
```

Everything else (WiFi, MQTT, LED pattern) stays identical.

---

## What the readings mean

**Heading (0–360°)**
Compass bearing relative to magnetic north (or true north if declination is set).

| Heading | Direction |
|---------|-----------|
| 0° / 360° | North |
| 90° | East |
| 180° | South |
| 270° | West |

**X / Y / Z axes (µT)**
Raw magnetic field strength on each axis. Useful for:
- Detecting nearby ferrous metal (field distortion)
- Orientation tracking
- Tilt-compensated compass (needs accelerometer for full tilt compensation)

**Keep the sensor away from:**
- Motors, speakers, magnets — will saturate the readings
- Steel chassis / bolts — cause hard-iron distortion (fixed offset in X/Y)
- Other I2C devices sharing long cable runs without shielding

---

## Calibration (hard-iron offset)

All magnetometers need calibration to remove the constant magnetic bias from nearby metal. Without it, the heading can be off by 10–30°.

Simple calibration method:
1. Rotate the sensor slowly through 360° on a flat surface
2. Note the min and max values on X and Y
3. Add offsets to the heading calculation:

```cpp
float x_offset = (x_max + x_min) / 2.0;
float y_offset = (y_max + y_min) / 2.0;
float heading = atan2(event.magnetic.y - y_offset,
                      event.magnetic.x - x_offset) + DECLINATION_RAD;
```
