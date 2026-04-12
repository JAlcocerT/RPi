# DHT Sensor Dashboard

Multi-sensor dashboard for Pico W (DHT22) and ESP32 (DHT11) data via MQTT → TimescaleDB → FastAPI → Browser.

---

## Files

| File | Purpose |
|------|---------|
| `mqtt_to_db.py` | MQTT subscriber — writes `pico/#` and `esp32/#` to TimescaleDB |
| `main.py` | FastAPI — REST `/history` endpoint + WebSocket live feed |
| `index.html` | Dashboard — sensor filter, time range picker, live charts |

---

## Deploy on server

```sh
# stop old sessions if running
tmux kill-session -t mqtt
tmux kill-session -t webapp

# install deps
cd ~/dht-webapp
uv pip install -r requirements.txt

# start MQTT subscriber
tmux new-session -d -s mqtt 'cd ~/dht-webapp && uv run mqtt_to_db.py'

# start web app (http://192.168.1.2:8077)
tmux new-session -d -s webapp 'cd ~/dht-webapp && uv run uvicorn main:app --host 0.0.0.0 --port 8077'
```

---

## TimescaleDB queries

### Average per hour for each metric (last 24h)

```sh
docker exec -it timescaledb psql -U pico -d sensors -c \
  "SELECT time_bucket('1 hour', ts) AS hour,
          topic,
          ROUND(AVG(value)::numeric, 2) AS avg_value
   FROM readings
   WHERE topic IN (
     'pico/temperature/dht22',
     'pico/humidity/dht22',
     'esp32/temperature/dht11',
     'esp32/humidity/dht11'
   )
   AND ts > NOW() - INTERVAL '24 hours'
   GROUP BY hour, topic
   ORDER BY topic, hour DESC;"
```

### Latest raw value for each metric

```sh
docker exec -it timescaledb psql -U pico -d sensors -c \
  "SELECT DISTINCT ON (topic)
          topic,
          ROUND(value::numeric, 2) AS value,
          ts
   FROM readings
   WHERE topic IN (
     'pico/temperature/dht22',
     'pico/humidity/dht22',
     'esp32/temperature/dht11',
     'esp32/humidity/dht11'
   )
   ORDER BY topic, ts DESC;"
```

---

## MQTT topics

| Topic | Sensor | Metric |
|-------|--------|--------|
| `pico/temperature/dht22` | Pico W | Temperature (°C) |
| `pico/humidity/dht22` | Pico W | Humidity (%) |
| `esp32/temperature/dht11` | ESP32 | Temperature (°C) |
| `esp32/humidity/dht11` | ESP32 | Humidity (%) |

Monitor live:
```sh
mosquitto_sub -h 192.168.1.2 -t "pico/#" -t "esp32/#" -v
```
