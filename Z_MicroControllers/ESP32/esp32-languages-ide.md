# ESP32 — Languages & IDEs

---

## Install Arduino IDE

```powershell
# via Chocolatey (Arduino 1.x)
choco install arduino

# via Chocolatey (Arduino 2.x)
choco install arduino-ide-2

# via winget (recommended — built into Windows 11)
winget install ArduinoSA.IDE.stable
```

Or download directly from: https://www.arduino.cc/en/software

### Add ESP32 board support (first time only)

1. `File` → `Preferences` → **Additional Board Manager URLs**, add:
```
https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
```
2. `Tools` → `Board` → `Boards Manager` → search **esp32** → install **esp32 by Espressif**
3. `Tools` → `Board` → **ESP32 Dev Module**
4. `Tools` → `Port` → **COM4**

### Required libraries for this project

Install via `Tools` → `Manage Libraries`:

| Library | Author | Used by |
|---------|--------|---------|
| `DHT sensor library for ESPx` | beegee-tokyo | `esp32-dht11.cpp`, `esp32-dht11-mqtt.cpp` |
| `PubSubClient` | Nick O'Leary | all MQTT scripts |

### Serial Monitor baud rates

| Script | Baud rate |
|--------|-----------|
| `esp32-dht11.cpp` | 115200 |
| `esp32-dht11-mqtt.cpp` | 115200 |
| `esp32-internal-temp-mqtt.cpp` | 115200 |
| `esp32-voltage-mqtt.cpp` | 115200 |
| `wifi-blink.cpp` | **921600** |

---

## Connecting to a running ESP32

### Identify the port first (Windows)

```powershell
pnputil /enum-devices /class Ports
```

| USB chip | Typical board | Port shows as |
|----------|--------------|---------------|
| CH9102 / CH340 (`VID_1A86`) | ESP32 dev boards | COM4 (or similar) |
| CP2102 (`VID_10C4`) | ESP32 dev boards | COM port |
| USB-CDC (`VID_2E8A`) | Raspberry Pi Pico W | COM3 (or similar) |

> Only one program can hold a COM port at a time — close Arduino IDE Serial Monitor before opening Thonny, and vice versa.

### If the device is busy / not responding

The ESP32 may be running a script. Try in order:

1. `Ctrl+C` in Thonny Shell — interrupts a running MicroPython script
2. Press the **EN/Reset** button on the board
3. Use `mpremote` (see MicroPython section below)

### LED always ON = WiFi connected (wifi-blink.cpp)

`wifi-blink.cpp` blinks while connecting, then sets `LED_BUILTIN HIGH` permanently once connected. A solid ON LED likely means Arduino firmware with WiFi connected — not MicroPython.

---

## Language & IDE comparison

| Language | IDE / Toolchain | Thonny? | Best for |
|----------|----------------|---------|----------|
| **Arduino C++** | Arduino IDE, PlatformIO | ❌ | Most library support, largest community, all scripts in `esp32-c/` |
| **MicroPython** | Thonny, `mpremote` | ✅ | Familiar from Pico W, fast iteration, no compile step |
| **ESPHome (YAML)** | Docker dashboard | ❌ | Zero-code sensor → MQTT pipelines, see `Z_SelfHosting/esphome/` |
| **Rust** | `esp-idf-hal`, `esp-hal` | ❌ | Bare-metal, memory safety, production firmware — overkill for sensor reading |
| **C (esp-idf)** | ESP-IDF toolchain | ❌ | Full Espressif native SDK — rarely needed over Arduino |

---

## MicroPython on ESP32

Thonny works with ESP32 **only if MicroPython firmware is flashed**.

### Flash MicroPython (replaces any existing firmware)

```powershell
pip install esptool

# Erase existing firmware
esptool.py --port COM4 erase_flash

# Download .bin from https://micropython.org/download/esp32/
# Then flash it
esptool.py --port COM4 write_flash -z 0x1000 esp32-XXXXXX.bin
```

### Connect with Thonny

- Interpreter: **MicroPython (ESP32)**
- Port: **COM4**
- Hit Stop — Shell should show `MicroPython vX.XX on ...; ESP32 module`

### Connect with mpremote (more robust than Thonny for stubborn connections)

```powershell
pip install mpremote

mpremote connect COM4        # open REPL
mpremote connect COM4 ls     # list files on device
mpremote connect COM4 run script.py  # run a script without flashing
```

---

## Internal temperature sensor — module compatibility

| Module | Core | Has `temprature_sens_read()`? |
|---|---|---|
| ESP-WROOM-32 / ESP32-D0WDQ6 | Xtensa LX6 | ✅ Yes |
| ESP32-WROOM-32U | Xtensa LX6 | ✅ Yes |
| ESP32-S2 | Xtensa LX7 | ❌ No |
| ESP32-S3 | Xtensa LX7 | ❌ No |
| ESP32-C3 | RISC-V | ❌ No |
| ESP32-H2 | RISC-V | ❌ No |

If the function returns `128` (converts to ~53°C cold), the sensor is not present on that chip.

---

## ADC / voltage reading — quick rules

- Always use **ADC1 pins (GPIO32–GPIO39)** — ADC2 is disabled when WiFi is active
- Use **GPIO35** for voltage reading (input-only, no pull-up/down, WiFi-safe)
- Use a **voltage divider** (R1=R2=100kΩ) to scale V_in to 0–3.3V range
- Use `esp_adc_cal` + average 16 samples to reduce noise and non-linearity
- Max safe V_in with ÷2 divider: **6.6V**

See `esp-voltage-verif.md` for full detail.
