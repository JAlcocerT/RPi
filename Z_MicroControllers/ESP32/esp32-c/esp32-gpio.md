# ESP32 GPIO Pin Reference

Which pins are safe to use for sensors (DHT11, DHT22, etc.) and which to avoid.

---

## Summary table

| Safety | GPIO Numbers | Reason |
|--------|-------------|--------|
| **Best** | 4, 14, 25, 26, 27, 32, 33 | No special boot functions — stable for data |
| **Okay** | 12, 13, 15 | Strapping pins — may cause boot/flash issues if pulled at power-on |
| **Bad** | 34, 35, 36, 39 | Input-only — no pull-up, cannot drive signal back to sensor |
| **Avoid** | 0, 1, 2, 3 | Critical for boot and USB/serial communication |

---

## Why each category

### Best — GPIO 4, 14, 25, 26, 27, 32, 33

No special duties at boot. Safe for any bidirectional sensor protocol (DHT11, DHT22, 1-wire, etc.).

### Okay — GPIO 12, 13, 15 (Strapping pins)

The ESP32 reads these pins at the moment of power-on to decide how to boot:

- **GPIO 15** — if pulled LOW at boot, suppresses boot log output. If pulled HIGH, no issue. DHT11/22 idle state is HIGH, so it usually works — but if the sensor pulls the line LOW during power-on you may get a failed boot or failed upload.
- **GPIO 12** — controls flash voltage. If pulled HIGH at boot on some modules, the flash runs at 1.8V instead of 3.3V and the ESP32 crashes.
- **GPIO 0** — see Avoid below.

> Our `esp32-dht11-mqtt.cpp` originally used GPIO15. Works in practice but GPIO14 is safer — updated accordingly.

### Bad — GPIO 34, 35, 36, 39 (Input-only)

These pins have **no internal pull-up and cannot output**. The DHT11/DHT22 protocol requires the ESP32 to pull the line LOW briefly to trigger a reading — input-only pins cannot do this. These pins are fine for analog readings (ADC1) but not for sensor data lines.

### Avoid — GPIO 0, 1, 2, 3

| Pin | Used for | Risk |
|-----|----------|------|
| GPIO 0 | BOOT button — LOW at power-on = flash mode | Sensor pulling LOW = ESP32 never runs your code |
| GPIO 1 | USB TX (Serial output) | Conflicts with Serial Monitor; upload issues |
| GPIO 2 | Onboard LED; reserved on WROOM-DA (antenna) | LED flicker; boot conflicts; reserved on DA variant |
| GPIO 3 | USB RX (Serial input) | Conflicts with Serial Monitor; upload issues |

---

## ADC pins — additional constraint for analog use

If reading **voltage/analog signals** (not digital sensor data), also avoid ADC2 pins when WiFi is active:

| ADC | Pins | WiFi safe? |
|-----|------|-----------|
| ADC1 | 32, 33, 34, 35, 36, 39 | ✅ Yes |
| ADC2 | 0, 2, 4, 12, 13, 14, 15, 25, 26, 27 | ❌ No — disabled when WiFi on |

> See `esp-voltage-verif.md` for full ADC detail.

---

## Recommended pins for this project

| Use | Pin | Notes |
|-----|-----|-------|
| DHT11 / DHT22 data | **GPIO14** | Safe, no special functions |
| Voltage divider (ADC) | **GPIO35** | ADC1, input-only, WiFi-safe |
| I2C SDA (MLX90614) | **GPIO21** | Default I2C SDA on ESP32 |
| I2C SCL (MLX90614) | **GPIO22** | Default I2C SCL on ESP32 |
| LED status | **GPIO4** | Safe; GPIO2 reserved on WROOM-DA |
