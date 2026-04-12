# ESP32 + MH-Series IR Obstacle Sensor → MQTT

Detects objects using infrared reflection. The onboard LM393 comparator chip converts the IR signal to a clean digital HIGH/LOW — your code only needs a `digitalRead()`. No sensor library required.

---

## Wiring

```
MH Sensor    ESP32-WROOM-DA
─────────    ──────────────
VCC    →     3V3
GND    →     GND
OUT    →     GPIO14
```

| MH Pin | ESP32 Pin | Notes |
|--------|-----------|-------|
| VCC | 3V3 | Use 3.3V — keeps OUT signal at 3.3V logic, safe for ESP32 |
| GND | GND | |
| OUT | GPIO14 | Digital signal — safe pin, no special boot functions |

> **Do not use 5V on VCC.** If powered at 5V, the OUT pin may output 5V logic which can damage the ESP32 GPIO over time. The module works fine at 3.3V.

> Some MH modules have a 4th pin labelled **EN** or **AO** (analog out). Leave it unconnected for this digital use case.

---

## How the sensor works

The module emits IR light from a transmitter LED. When an object is in range, the light reflects back and hits the receiver. The LM393 comparator compares the received signal against a threshold set by the **onboard potentiometer** and outputs:

| OUT pin | Meaning |
|---------|---------|
| **LOW** | Object detected (IR reflected back) |
| **HIGH** | Path clear (no reflection) |

> LOW = detected is counterintuitive but standard for this type of sensor.

---

## Sensitivity adjustment

The blue module has a small **potentiometer** (adjustable with a screwdriver):

- Turn **clockwise** → increases sensitivity → detects objects at greater distance
- Turn **counter-clockwise** → decreases sensitivity → only detects at close range
- Typical useful range: **2–30 cm** depending on object reflectivity
- The onboard LED lights up when an object is detected — use it to calibrate before wiring to the ESP32

---

## Arduino IDE setup

1. Board: **ESP32 Dev Module** (`Tools → Board`)
2. Port: whichever COM port shows (`Tools → Port`)
3. Libraries (`Tools → Manage Libraries`):
   - `PubSubClient` by Nick O'Leary — only library needed
4. Edit credentials at top of file, then `Ctrl+U` to flash

---

## MQTT Topics

| Topic | Value | Trigger |
|-------|-------|---------|
| `esp32/ir/obstacle` | `"1"` detected / `"0"` clear | On state change + every 5s heartbeat (retained) |
| `esp32/ir/event` | `"detected"` / `"clear"` | On state change only |

The `obstacle` topic is published as **retained** — the broker remembers the last state, so any new subscriber immediately gets the current status without waiting for the next reading.

Verify on your server:

```sh
mosquitto_sub -h 192.168.1.2 -t "esp32/ir/#" -v
```

---

## Serial Monitor

Baud rate: **115200**

Expected output:
```
Connecting to 'your-wifi'
....
Connected — IP: 192.168.1.x
Connecting to MQTT broker... connected.
State change → clear
Heartbeat — obstacle: clear
State change → detected
State change → clear
Heartbeat — obstacle: clear
```

---

## Known limitation — sunlight interference

The sensor is **blind outdoors in direct sunlight**. Sunlight contains a large amount of IR radiation which saturates the receiver — the sensor will report "detected" constantly regardless of whether anything is in front of it.

| Environment | Works? |
|-------------|--------|
| Indoors | ✅ Yes |
| Outdoors, shaded | ✅ Usually |
| Outdoors, direct sun | ❌ No |

---

## Use cases

| Use case | Notes |
|----------|-------|
| Object / presence detection | Is something on the shelf, in the bin, at the door? |
| Proximity trigger | Start an action when something comes within range |
| Line following (robotics) | Point downward — detects dark line vs light floor |
| Liquid level (non-contact) | Point at translucent container side |
| Counting (conveyor belt) | Objects passing a fixed point |

---

## Safety note

The IR LED emits non-visible light. It is not harmful to eyes or skin at this power level (same as a TV remote). The only electrical risk is exposed solder pads on the back of the module — ensure the board does not rest on any metal surface or stray wires while powered.
