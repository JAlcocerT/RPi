# ESP32

Collection of ESP32 projects. 

The ESP32 is a step up from the Pico W — dual-core, more RAM, Bluetooth, and a larger ecosystem of Arduino libraries.

## Existing scripts

| File | Description |
|------|-------------|
| `esp32-c/esp32-dht11.cpp` | Read DHT11 sensor, print to serial. Original version. |
| `esp32-c/esp32-dht11-mqtt.cpp` | **Improved** — reads DHT11 and publishes to MQTT broker every 5s. Drop-in for the same stack as `MQTT-DHT22`. |
| `esp32-c/wifi-blink.cpp` | Connect to WiFi, blink LED until connected. |
| `esp32-c/ESP_32_WebSocket_Test.cpp` | Minimal AsyncWebSocket server on the ESP32 itself. |
| `esp32-c/dht11-arduino-cloud.cpp` | DHT11 → Arduino IoT Cloud (requires Arduino Cloud account). |

## Does the DHT11 script work?

Yes — `esp32-dht11.cpp` works as-is with the `DHTesp` library on GPIO 15. It just prints to serial. The improved `esp32-dht11-mqtt.cpp` adds WiFi + MQTT publishing to match the rest of the stack (`192.168.1.2` broker, same topics pattern as the Pico W).

## Does Thonny work with the ESP32?

**For MicroPython — yes.** Flash MicroPython firmware for ESP32 first:

```sh
# Install esptool
pip install esptool

# Erase flash
esptool.py --port COM3 erase_flash

# Flash MicroPython (download .bin from https://micropython.org/download/esp32/)
esptool.py --port COM3 write_flash -z 0x1000 esp32-XXXXXX.bin
```

Then set Thonny interpreter to **MicroPython (ESP32)** — works exactly like the Pico W workflow.

**For C/Arduino — no.** Use **Arduino IDE** or **PlatformIO** (VS Code extension) instead.

## Which language to use?

| Language | Toolchain | Best for | Verdict |
|----------|-----------|----------|---------|
| **Arduino C++** | Arduino IDE / PlatformIO | Sensor reading, MQTT, WiFi — huge library ecosystem | Best choice for this project |
| **MicroPython** | Thonny | Familiar from Pico W work, fast iteration | Good if you want to reuse Pico W code patterns |
| **ESPHome (YAML)** | Docker dashboard | Zero-code sensor → MQTT pipelines | Best if you just want data flowing, no coding |
| **Rust** | `esp-idf-hal` / `esp-hal` | Production firmware, memory safety, bare-metal control | Overkill for sensor reading — steep setup |
| **C (esp-idf)** | ESP-IDF toolchain | Full control, Espressif native SDK | More complex than Arduino, rarely needed here |

### Recommendation for this project

- **Arduino C++** if you want the most library support and examples (DHT, MQTT, WebSocket all have mature libs)
- **MicroPython** if you want to reuse the same patterns as the Pico W `MQTT-DHT22` scripts
- **ESPHome** if you want the cleanest setup with zero boilerplate — see `Z_SelfHosting/esphome/`

## MQTT Topics (improved script)

| Topic | Value |
|-------|-------|
| `esp32/temperature/dht11` | Temperature (°C) |
| `esp32/humidity/dht11` | Humidity (%) |

Subscribe to verify:

```sh
mosquitto_sub -h 192.168.1.2 -t "esp32/#" -v
```

## Arduino IDE — required libraries

Install via **Tools → Manage Libraries**:

- `DHT sensor library for ESPx` by beegee-tokyo
- `PubSubClient` by Nick O'Leary

## Rust

See `esp32-rust/` — references in `readme.md` for getting started with `esp-idf-hal`.
