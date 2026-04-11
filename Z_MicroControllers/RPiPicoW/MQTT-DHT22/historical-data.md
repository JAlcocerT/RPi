# Saving Historical DHT22 Data

MQTT is fire-and-forget — if nothing is consuming and storing messages when they arrive, they are lost. Below are the main strategies to persist the data coming from the Pico W.

---

## Strategy 1 — InfluxDB + Telegraf (recommended)

The simplest path to full time-series storage with no custom code.

```
Pico W → EMQX → Telegraf → InfluxDB → Grafana
```

**Telegraf** is a collector agent that subscribes to MQTT and writes directly to InfluxDB.

```yaml
# telegraf.conf (relevant sections)
[[inputs.mqtt_consumer]]
  servers = ["tcp://192.168.1.2:1883"]
  topics = ["pico/#"]
  data_format = "value"
  data_type = "float"

[[outputs.influxdb_v2]]
  urls = ["http://localhost:8086"]
  token = "your-token"
  org = "your-org"
  bucket = "pico"
```

**Pros:** no Python code, battle-tested, Grafana connects natively to InfluxDB  
**Cons:** two extra services to run (Telegraf + InfluxDB)

---

## Strategy 2 — Python subscriber writing to SQLite

Lightweight, no extra services. A single Python script subscribes and appends to a local SQLite database.

```python
import sqlite3
import paho.mqtt.client as mqtt

conn = sqlite3.connect("dht22.db")
conn.execute("""
    CREATE TABLE IF NOT EXISTS readings (
        ts DATETIME DEFAULT CURRENT_TIMESTAMP,
        topic TEXT,
        value REAL
    )
""")

def on_message(client, userdata, msg):
    value = float(msg.payload.decode())
    conn.execute("INSERT INTO readings (topic, value) VALUES (?, ?)",
                 (msg.topic, value))
    conn.commit()
    print(f"{msg.topic}: {value}")

client = mqtt.Client()
client.on_message = on_message
client.connect("192.168.1.2", 1883)
client.subscribe("pico/#")
client.loop_forever()
```

**Pros:** pure Python, single file, no extra services, easy to query with pandas  
**Cons:** SQLite not ideal for high-frequency time-series; manual dashboard needed

---

## Strategy 3 — InfluxDB + Python (no Telegraf)

Same storage as Strategy 1 but using a Python script instead of Telegraf — more control, slightly more code.

```python
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

write_api = InfluxDBClient(url="http://localhost:8086", token="your-token", org="your-org") \
            .write_api(mode=SYNCHRONOUS)

def on_message(client, userdata, msg):
    value = float(msg.payload.decode())
    point = Point("dht22").tag("topic", msg.topic).field("value", value)
    write_api.write(bucket="pico", record=point)

client = mqtt.Client()
client.on_message = on_message
client.connect("192.168.1.2", 1883)
client.subscribe("pico/#")
client.loop_forever()
```

**Pros:** full time-series DB, Grafana-ready, more control than Telegraf  
**Cons:** requires InfluxDB running; slightly more setup than Strategy 2

---

## Strategy 4 — Python subscriber writing to TimescaleDB (PostgreSQL)

Best of both worlds: standard SQL interface with time-series performance. TimescaleDB is a PostgreSQL extension — if you already run Postgres, this is a natural fit.

```
Pico W → EMQX → Python subscriber → TimescaleDB (PostgreSQL) → Grafana
```

**Docker Compose:**

```yaml
services:
  timescaledb:
    image: timescale/timescaledb:latest-pg16
    container_name: timescaledb
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: pico
      POSTGRES_PASSWORD: pico
      POSTGRES_DB: sensors
    restart: always
```

**Create the hypertable (run once):**

```sql
CREATE TABLE readings (
    ts          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    topic       TEXT        NOT NULL,
    value       DOUBLE PRECISION NOT NULL
);

SELECT create_hypertable('readings', 'ts');
```

**Python subscriber:**

```python
import psycopg2
import paho.mqtt.client as mqtt

conn = psycopg2.connect(
    host="192.168.1.2", dbname="sensors",
    user="pico", password="pico"
)
conn.autocommit = True

def on_message(client, userdata, msg):
    value = float(msg.payload.decode())
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO readings (topic, value) VALUES (%s, %s)",
            (msg.topic, value)
        )
    print(f"{msg.topic}: {value}")

client = mqtt.Client()
client.on_message = on_message
client.connect("192.168.1.2", 1883)
client.subscribe("pico/#")
client.loop_forever()
```

**Install dependencies:**

```sh
pip install paho-mqtt psycopg2-binary
```

**Query examples:**

```sql
-- Last 10 readings
SELECT * FROM readings ORDER BY ts DESC LIMIT 10;

-- Average temp per hour (last 24h)
SELECT time_bucket('1 hour', ts) AS hour,
       AVG(value) AS avg_temp
FROM readings
WHERE topic = 'pico/temperature/dht22'
  AND ts > NOW() - INTERVAL '24 hours'
GROUP BY hour ORDER BY hour;
```

**Pros:** standard SQL, Grafana-ready (PostgreSQL datasource), scales well, familiar tooling  
**Cons:** heavier than SQLite; TimescaleDB extension required

---

## Comparison

| Strategy | Extra services | Code needed | Query / visualize |
|----------|---------------|-------------|-------------------|
| Telegraf + InfluxDB | Telegraf, InfluxDB | None (config only) | Grafana |
| Python + SQLite | None | ~20 lines | pandas, custom |
| Python + InfluxDB | InfluxDB | ~20 lines | Grafana |
| Python + TimescaleDB | TimescaleDB (PostgreSQL) | ~20 lines | Grafana, plain SQL |

---

## Quick recommendation

- **Just want to get started fast?** → Strategy 2 (SQLite). Single script, runs anywhere.
- **Want dashboards and long-term storage?** → Strategy 1 (Telegraf + InfluxDB + Grafana). Most scalable.
- **Already have InfluxDB but not Telegraf?** → Strategy 3.
- **Already run PostgreSQL or prefer SQL?** → Strategy 4 (TimescaleDB). Best query flexibility.
