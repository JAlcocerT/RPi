# ESP32 Battery Life Estimation

Battery: **4000 mAh / 17.8 Wh / 5V 2A max**

---

## ESP32-WROOM-DA current draw

| Mode | Current |
|------|---------|
| Active WiFi TX (peak) | ~240 mA |
| Active WiFi connected, idle | ~80–100 mA |
| Light sleep (WiFi off) | ~0.8 mA |
| Deep sleep | ~0.01 mA (10 µA) |

For the current script (`esp32-internal-temp-mqtt.cpp`) — WiFi always on, publishing every 5s:

**~80–100 mA continuous**

---

## Estimation for each mode

### Current script (WiFi always on)

```
4000 mAh / 90 mA = ~44 hours
```

> ~1.8 days on a 4000 mAh battery at 5V.

### With light sleep between publishes (WiFi reconnects every 5s)

```
active ~1s @ 200 mA + sleep ~4s @ 0.8 mA
average = (200×1 + 0.8×4) / 5 = ~41 mA
4000 mAh / 41 mA = ~97 hours
```

> ~4 days.

### With deep sleep between publishes (WiFi reconnects every 60s)

```
active ~2s @ 200 mA + sleep ~58s @ 0.01 mA
average = (200×2 + 0.01×58) / 60 = ~6.7 mA
4000 mAh / 6.7 mA = ~597 hours
```

> ~25 days.

---

## Summary

| Strategy | Avg current | Battery life |
|----------|-------------|--------------|
| WiFi always on (current script) | ~90 mA | ~44 hours |
| Light sleep between publishes | ~41 mA | ~4 days |
| Deep sleep, publish every 60s | ~6.7 mA | ~25 days |
| Deep sleep, publish every 5min | ~1.5 mA | ~111 days |

---

## Caveats

- These are estimates — actual draw varies by WiFi signal strength, broker distance, and power supply efficiency (a boost converter from LiPo to 5V typically has ~85–90% efficiency, reducing effective capacity by ~10–15%)
- The 5V 2A rating is the **maximum output** of the battery — well above what the ESP32 needs, so no bottleneck there
- A LiPo battery's usable voltage range is 3.0V–4.2V. If powering the ESP32 directly (3.3V via LDO), you skip the 5V conversion loss but the battery cuts out earlier
- WiFi reconnection time after deep sleep is typically 1–3 seconds and draws the most current — minimising reconnects is the biggest lever for battery life

---

## Deep sleep code snippet

To maximise battery life, replace the `loop()` publish interval with deep sleep:

```cpp
#include "esp_sleep.h"

#define SLEEP_SECONDS 60

void loop() {
  // connect, read, publish once
  connectWifi();
  connectMqtt();

  float chipTemp = getInternalTempC();
  char tempStr[8];
  snprintf(tempStr, sizeof(tempStr), "%.2f", chipTemp);
  mqtt.publish(TOPIC_CHIP_TEMP, tempStr);
  mqtt.loop();
  delay(100);  // let publish complete

  // then sleep
  esp_sleep_enable_timer_wakeup(SLEEP_SECONDS * 1000000ULL);
  esp_deep_sleep_start();
  // execution resumes from setup() after wakeup
}
```
