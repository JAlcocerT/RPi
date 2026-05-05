# Data Lineage — Pico W → VPD POC

What is flowing today, and how to extend it to the ESP32.

## Current pipeline

```
Pico W (MicroPython)
   │  publishes
   ▼
EMQX broker  (192.168.1.2:1883)
   │  pico/#  (wildcard subscribe)
   ▼
server.js  ──INSERT──▶  TimescaleDB.readings(ts, topic, value)
                                    │ NOTIFY new_reading
                                    ▼
                          server.js LISTEN  ──WS──▶  Browser (app.js)
                                                       │ filter on TOPIC map
                                                       ▼
                                                 Cards / Charts / VPD
```

Two filter stages — they are **not** the same:

| Stage | Where | Rule today | Effect |
|------|------|-----------|--------|
| Ingest | `server.js` + `MQTT_TOPIC` env | `pico/#` wildcard | **All** Pico topics land in DB |
| Display | `public/app.js` `TOPIC` map | exact match on 3 strings | Only 3 fields rendered |

Anything ingested but not in the display map is silently dropped by the browser.
Still queryable in TimescaleDB.

## What flows right now

### Air temperature (DHT22) — drives VPD

| | |
|---|---|
| **MQTT topic** | `pico/temperature/dht22` |
| **Publisher** | `RPiPicoW/MQTT-DHT22/main.py` (`PUBLISH_TOPIC_DHT22_TEMP`) |
| **Sensor** | DHT22 on Pico W GPIO |
| **Units** | °C, 1 decimal |
| **Used by UI** | `card--temp`, `chart-th` (left axis), VPD calc |

### Relative humidity (DHT22) — drives VPD

| | |
|---|---|
| **MQTT topic** | `pico/humidity/dht22` |
| **Publisher** | `RPiPicoW/MQTT-DHT22/main.py` (`PUBLISH_TOPIC_DHT22_HUMI`) |
| **Sensor** | DHT22 on Pico W GPIO |
| **Units** | %RH, 1 decimal |
| **Used by UI** | `card--humi`, `chart-th` (right axis), VPD calc |

### Chip temperature (RP2040 internal) — info only

| | |
|---|---|
| **MQTT topic** | `pico/temperature/internal` |
| **Publisher** | `RPiPicoW/MQTT-DHT22/main.py` (`PUBLISH_TOPIC_PICO_TEMP`) — also `MQTT-MLX90614/main.py`, `MQTT-InternalTemp/main.py` |
| **Sensor** | RP2040 on-die ADC channel 4 |
| **Units** | °C, 2 decimals |
| **Used by UI** | `card--chip` only (not in VPD math, not in chart) |

### Other Pico topics that LAND IN DB but UI ignores

If you ever flash `MQTT-MLX90614/main.py`, these also land in `readings`:

- `pico/temperature/object`  — IR object temp (would be the **leaf** temp for true VPD)
- `pico/temperature/ambient` — IR sensor ambient

They're written to TimescaleDB but the dashboard does not render them.
Useful for queries like:

```sql
SELECT topic, COUNT(*), MAX(ts) FROM readings GROUP BY topic;
```

## VPD math today

```js
SVP(T) = 0.6108 · exp( 17.27·T / (T + 237.3) )
VPD    = SVP(T) · (1 − RH/100)
```

Inputs: `last.temp` ← `pico/temperature/dht22`, `last.humi` ← `pico/humidity/dht22`.
**Air-VPD approximation** — assumes leaf temp = air temp. True leaf-VPD needs an
IR sensor (MLX90614 on the leaf surface).

## Adding the ESP32

The ESP32 (`Z_MicroControllers/ESP32/esp32-c/esp32-dht11-mqtt.cpp`) publishes:

- `esp32/temperature/dht11`  — air T (°C)
- `esp32/humidity/dht11`     — RH (%)
- (`esp32/magnetometer/heading` from `esp32-hmc5883l-mqtt.cpp` — irrelevant for VPD)

Two changes are required — one for ingest, one for display.

### 1. Ingest — broaden the MQTT subscribe

`server.js` currently subscribes a single string. Easiest path: switch to an
array driven by a comma-separated env var.

**`docker-compose.yml`** — replace `MQTT_TOPIC` with the broader value, or use a
list:

```yaml
environment:
  # option A — wildcard for both devices
  MQTT_TOPIC: "pico/#,esp32/#"
  # option B — explicit allowlist (safer, no surprise topics)
  # MQTT_TOPIC: "pico/temperature/dht22,pico/humidity/dht22,pico/temperature/internal,esp32/temperature/dht11,esp32/humidity/dht11"
```

**`server.js`** — split + subscribe array:

```js
const MQTT_TOPIC = process.env.MQTT_TOPIC || 'pico/#';
const topics = MQTT_TOPIC.split(',').map(s => s.trim()).filter(Boolean);

mqttClient.on('connect', () => {
  mqttClient.subscribe(topics, (err) => {
    if (err) console.error('MQTT subscribe err', err.message);
    else console.log(`Subscribed: ${topics.join(', ')}`);
  });
});
```

After this, all matching topics land in `readings` next to the Pico ones.
Disambiguate in SQL via the `topic` column prefix:

```sql
SELECT
  CASE WHEN topic LIKE 'pico/%' THEN 'pico'
       WHEN topic LIKE 'esp32/%' THEN 'esp32'
  END AS device,
  topic, value, ts
FROM readings
ORDER BY ts DESC
LIMIT 50;
```

### 2. Display — render ESP32 values

The current dashboard is **single-device**. There are two reasonable patterns —
pick one based on goal:

#### Pattern A — Add a 2nd device, show two VPD readouts

Best if both rooms/devices matter. Duplicate the cards + charts and add a
second topic group:

```js
// public/app.js
const DEVICES = {
  pico:  { TEMP: 'pico/temperature/dht22',  HUMI: 'pico/humidity/dht22' },
  esp32: { TEMP: 'esp32/temperature/dht11', HUMI: 'esp32/humidity/dht11' },
};
```

Track `last.{pico,esp32}.{temp,humi}` separately, compute VPD per device,
render side-by-side cards + a 2-line VPD chart.

This is a real refactor of `app.js` and `index.html` — not a one-liner.

#### Pattern B — Same UI, switch which device feeds it

Simplest: keep the dashboard exactly as is, just point the `TOPIC` map at the
ESP32:

```js
const TOPIC = {
  TEMP: 'esp32/temperature/dht11',
  HUMI: 'esp32/humidity/dht11',
  CHIP: 'pico/temperature/internal',  // ESP32 has no equivalent — leave or remove
};
```

Same VPD math, same charts, just different sensor source. Good for an A/B
sanity check (same room, two sensors, do they agree).

### 3. Optional — leaf VPD via MLX90614

If you put an MLX90614 on a Pico W pointing at a leaf, you already publish
`pico/temperature/object` (= leaf temp).

Switch the formula in `app.js` to leaf-VPD:

```js
function vpdLeafKPa(tLeaf, tAir, rh) {
  return svp(tLeaf) - svp(tAir) * (rh / 100);
}
```

Add `last.leaf` from `pico/temperature/object` and call `vpdLeafKPa(last.leaf,
last.temp, last.humi)`. That gives biologically meaningful VPD instead of the
air-VPD approximation.

## TL;DR

- DB sees **everything** under `pico/#` already (wildcard ingest).
- UI shows only `dht22 temp`, `dht22 humi`, `internal chip temp`. VPD = f(dht22 temp, dht22 humi).
- ESP32 = expand `MQTT_TOPIC` (one env var) + minor `server.js` array tweak; UI work is a separate, larger change.
