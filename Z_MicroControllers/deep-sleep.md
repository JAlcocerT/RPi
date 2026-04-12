# Deep Sleep & Scheduled Wake

Applies to: **Pico W (MicroPython)** and **ESP32 (Arduino C++)**

---

## How the internal clocks work

Neither chip has a battery-backed RTC. On power-up they have no idea what time it is.

| | Pico W | ESP32 |
|---|---|---|
| Has RTC | ✅ | ✅ |
| RTC survives power off | ❌ | ❌ |
| RTC survives deep sleep | ❌ | ✅ (low-power RTC domain) |
| Knows real wall time | ❌ not without NTP | ❌ not without NTP |
| Max deep sleep timer | ~hours (tested) | days (64-bit µs counter) |

**Conclusion:** always sync via NTP on wake. Don't rely on the chip knowing the time from a previous session.

---

## Strategy — wake only between 7am and 1pm

```
Wake up
  └─ connect WiFi
  └─ NTP sync → get current time
  └─ if 7:00–12:59 → read sensor → publish MQTT
  └─ calculate seconds until next 7am
  └─ deep sleep for that duration
```

Battery impact — publishing 6h/day instead of 24h/day:

| Board | Always on | 7am–1pm only |
|---|---|---|
| Pico W | ~3.7 days | ~14 days |
| ESP32 | ~1.8 days | ~7 days |

---

## Pico W — MicroPython

```python
# deep_sleep_scheduled.py
# Assumes boot.py has connected to WiFi

import ntptime
import utime
import machine
from umqtt.robust import MQTTClient
from machine import Pin
from DHT22 import DHT22

UTC_OFFSET   = 2        # adjust to your timezone (e.g. 1=CET, 2=CEST)
WAKE_HOUR    = 7        # start publishing at 7am
SLEEP_HOUR   = 13       # stop publishing at 1pm
PUBLISH_INTERVAL_MS = 30 * 1000  # publish every 30s while awake

MQTT_BROKER = "192.168.1.2"

def get_local_hour():
    ntptime.settime()  # sync RTC from NTP (UTC)
    return (utime.localtime()[3] + UTC_OFFSET) % 24

def seconds_until_hour(target_hour, current_hour, current_min, current_sec):
    hours_to_wait = (target_hour - current_hour - 1) % 24 + 1
    return hours_to_wait * 3600 - current_min * 60 - current_sec

def main():
    ntptime.settime()
    t = utime.localtime()
    hour = (t[3] + UTC_OFFSET) % 24
    minute, second = t[4], t[5]

    print(f"Local time: {hour:02d}:{minute:02d}:{second:02d}")

    if WAKE_HOUR <= hour < SLEEP_HOUR:
        # Active window — read and publish
        import ubinascii
        CLIENT_ID = ubinascii.hexlify(machine.unique_id())
        mqttClient = MQTTClient(CLIENT_ID, MQTT_BROKER, keepalive=60)
        mqttClient.connect()

        dht_sensor = DHT22(Pin(15, Pin.IN, Pin.PULL_UP))
        utime.sleep_ms(2000)  # DHT22 stabilise

        T, H = dht_sensor.read()
        if T is not None:
            mqttClient.publish(b"pico/temperature/dht22", "{:.1f}".format(T).encode())
            mqttClient.publish(b"pico/humidity/dht22",    "{:.1f}".format(H).encode())
            print(f"Published: {T:.1f}°C  {H:.1f}%")

        mqttClient.disconnect()

        # Sleep until next publish interval or until SLEEP_HOUR
        remaining_active_ms = (SLEEP_HOUR - hour - 1) * 3600000
        sleep_ms = min(PUBLISH_INTERVAL_MS, remaining_active_ms)
        print(f"Sleeping {sleep_ms // 1000}s before next publish")
        machine.deepsleep(sleep_ms)

    else:
        # Outside active window — sleep until 7am
        secs = seconds_until_hour(WAKE_HOUR, hour, minute, second)
        print(f"Outside active window. Sleeping {secs // 3600}h {(secs % 3600) // 60}m until {WAKE_HOUR}:00")
        machine.deepsleep(secs * 1000)

if __name__ == "__main__":
    main()
```

### NTP note — timezone

`ntptime.settime()` always returns **UTC**. Add your offset manually:

```python
UTC_OFFSET = 2   # CEST (Central European Summer Time)
UTC_OFFSET = 1   # CET  (Central European Time, winter)
UTC_OFFSET = 0   # UTC / GMT
```

---

## ESP32 — Arduino C++

```cpp
// deep_sleep_scheduled.cpp
#include <WiFi.h>
#include <time.h>
#include <PubSubClient.h>

const char* WIFI_SSID     = "your-wifi";
const char* WIFI_PASSWORD = "your-password";
const char* MQTT_BROKER   = "192.168.1.2";
const char* NTP_SERVER    = "pool.ntp.org";

const int UTC_OFFSET_SEC  = 2 * 3600;  // CEST
const int WAKE_HOUR       = 7;
const int SLEEP_HOUR      = 13;
const int PUBLISH_INTERVAL_SEC = 30;

WiFiClient espClient;
PubSubClient mqtt(espClient);

void connectWifi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) delay(500);
}

void syncNTP() {
  configTime(UTC_OFFSET_SEC, 0, NTP_SERVER);
  struct tm t;
  while (!getLocalTime(&t)) delay(500);
}

int getCurrentHour() {
  struct tm t;
  getLocalTime(&t);
  return t.tm_hour;
}

long secondsUntilHour(int target) {
  struct tm t;
  getLocalTime(&t);
  int hours = ((target - t.tm_hour - 1 + 24) % 24) + 1;
  return hours * 3600L - t.tm_min * 60 - t.tm_sec;
}

void setup() {
  Serial.begin(115200);
  connectWifi();
  syncNTP();

  int hour = getCurrentHour();
  Serial.printf("Local hour: %d\n", hour);

  if (hour >= WAKE_HOUR && hour < SLEEP_HOUR) {
    // Active window — publish
    mqtt.setServer(MQTT_BROKER, 1883);
    while (!mqtt.connected()) {
      mqtt.connect("esp32-scheduler");
      delay(500);
    }

    // read internal temp and publish
    float chipTemp = (temprature_sens_read() - 32) / 1.8f;
    char buf[8];
    snprintf(buf, sizeof(buf), "%.2f", chipTemp);
    mqtt.publish("esp32/temperature/internal", buf);
    mqtt.loop();
    delay(100);

    long remaining = (SLEEP_HOUR - hour - 1) * 3600L;
    long sleepSec = min((long)PUBLISH_INTERVAL_SEC, remaining);
    Serial.printf("Sleeping %lds\n", sleepSec);
    esp_sleep_enable_timer_wakeup(sleepSec * 1000000ULL);
  } else {
    long secs = secondsUntilHour(WAKE_HOUR);
    Serial.printf("Sleeping %ldh %ldm until %d:00\n",
                  secs / 3600, (secs % 3600) / 60, WAKE_HOUR);
    esp_sleep_enable_timer_wakeup(secs * 1000000ULL);
  }

  esp_deep_sleep_start();
}

void loop() {}  // never reached — board resets on wake
```

---

## Hardware RTC alternative (DS3231)

If WiFi is unavailable or you need accurate timekeeping without NTP:

| Feature | DS3231 |
|---|---|
| Interface | I2C |
| Accuracy | ±2 ppm (~1 min/year) |
| Backup battery | CR2032 coin cell |
| Price | ~€2 |
| Library (Arduino) | `RTClib` by Adafruit |
| Library (MicroPython) | `ds3231` via mip |

Wire it like the MLX90614 (SDA/SCL + 3.3V + GND) and it keeps perfect time even when the board is fully powered off.

---

## References

- Pico W deep sleep: `machine.deepsleep(ms)` — [MicroPython docs](https://docs.micropython.org/en/latest/library/machine.html#machine.deepsleep)
- ESP32 deep sleep: `esp_deep_sleep_start()` — [Espressif docs](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/system/sleep_modes.html)
- Battery estimates: see `MQTT-DHT22/picow-consumption.md` and `ESP32/esp32-c/esp32-consumption.md`
