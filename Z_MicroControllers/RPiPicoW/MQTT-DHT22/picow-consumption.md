# Pico W Battery Life Estimation

Battery: **4000 mAh / 17.8 Wh / 5V 2A max**
Setup: **DHT22 sensor + WiFi + MQTT publishing every 5s**

---

## Pico W current draw

| Mode | Current |
|------|---------|
| Active WiFi TX (peak) | ~120 mA |
| Active WiFi connected, idle | ~40–50 mA |
| DHT22 reading (brief spike) | +1–2 mA |
| Light sleep (WiFi on) | ~20 mA |
| Dormant mode (WiFi off) | ~0.18 mA |
| DORMANT + disable regulator | ~0.025 mA (25 µA) |

> The Pico W draws significantly less than the ESP32 — single core, simpler WiFi chip (CYW43439).

---

## Estimation for each mode

### Current script (WiFi always on, publish every 5s)

```
4000 mAh / 45 mA = ~88 hours
```

> ~3.7 days on a 4000 mAh battery.

### Light sleep between DHT22 reads (WiFi stays on)

```
active ~0.5s @ 80 mA + sleep ~4.5s @ 20 mA
average = (80×0.5 + 20×4.5) / 5 = ~26 mA
4000 mAh / 26 mA = ~153 hours
```

> ~6.4 days.

### Dormant mode between publishes (WiFi reconnects every 60s)

```
active ~2s @ 120 mA + dormant ~58s @ 0.18 mA
average = (120×2 + 0.18×58) / 60 = ~4.2 mA
4000 mAh / 4.2 mA = ~952 hours
```

> ~39 days.

### Dormant mode, publish every 5 minutes

```
active ~2s @ 120 mA + dormant ~298s @ 0.18 mA
average = (120×2 + 0.18×298) / 300 = ~0.98 mA
4000 mAh / 0.98 mA = ~4081 hours
```

> ~170 days.

---

## Comparison vs ESP32-WROOM-DA (same battery, same setup)

| Strategy | Pico W | ESP32 |
|----------|--------|-------|
| WiFi always on | ~3.7 days | ~1.8 days |
| Sleep between publishes (60s) | ~39 days | ~25 days |
| Sleep between publishes (5 min) | ~170 days | ~111 days |

> Pico W lasts roughly **2× longer** than the ESP32 on the same battery due to lower idle current.

---

## Summary

| Strategy | Avg current | Battery life |
|----------|-------------|--------------|
| WiFi always on (current script) | ~45 mA | ~3.7 days |
| Light sleep, WiFi on | ~26 mA | ~6.4 days |
| Dormant, reconnect every 60s | ~4.2 mA | ~39 days |
| Dormant, reconnect every 5 min | ~0.98 mA | ~170 days |

---

## Caveats

- DHT22 adds negligible current — its contribution is under 2 mA and only during the brief read
- A boost converter from LiPo to 5V has ~85–90% efficiency — reduces effective capacity by ~10–15%
- WiFi reconnection after dormant takes ~2–3 seconds — the DHT22 needs ~1–2s to stabilise after power-up, so they overlap well
- The 5V 2A battery rating is the max output — the Pico W peaks at ~120 mA, well within limits
- MicroPython dormant mode requires calling `machine.lightsleep()` or `machine.deepsleep()` — the Pico W does not have a hardware deep sleep as aggressive as the ESP32, but `machine.deepsleep()` achieves ~0.18 mA

---

## Dormant mode code snippet

Replace the `utime.sleep_ms(500)` loop with deep sleep for maximum battery life:

```python
import machine
import utime
from umqtt.robust import MQTTClient
from machine import Pin
from DHT22 import DHT22

SLEEP_MS = 60 * 1000  # wake every 60 seconds

def main():
    # connect, read, publish once, then sleep
    mqttClient = MQTTClient(CLIENT_ID, MQTT_BROKER, keepalive=60)
    mqttClient.connect()

    dht_data = Pin(15, Pin.IN, Pin.PULL_UP)
    dht_sensor = DHT22(dht_data)
    utime.sleep_ms(2000)  # let DHT22 stabilise

    T, H = dht_sensor.read()
    if T is not None:
        mqttClient.publish(b"pico/temperature/dht22", "{:.1f}".format(T).encode())
        mqttClient.publish(b"pico/humidity/dht22",    "{:.1f}".format(H).encode())

    mqttClient.disconnect()
    machine.deepsleep(SLEEP_MS)
    # Pico W resets and runs boot.py + main.py again on wake
```
