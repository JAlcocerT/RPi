# Pico W — DHT22 Live + VPD (Node.js POC)

Single-process Node.js stack. MQTT subscriber + Express + WebSocket + TimescaleDB
`LISTEN/NOTIFY`. Modern dashboard with live cards, dual-axis T/RH chart, VPD
trend, and an interpretation guide.

```
Pico W → EMQX → server.js (mqtt sub) → TimescaleDB
                                            │ NOTIFY
                                       server.js (LISTEN)
                                            │ WebSocket
                                         Browser
```

![alt text](dht22-vpd.png)

## Stack

| Piece | Tech |
|------|------|
| DB | `timescale/timescaledb:latest-pg16` |
| Server | Node 20 (ESM) — `express`, `ws`, `pg`, `mqtt` |
| Frontend | Vanilla JS + Chart.js 4 (no framework, no build) |

## Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | TimescaleDB + Node webapp |
| `Dockerfile` | Node 20 alpine image for the webapp |
| `init.sql` | One-shot schema: hypertable + NOTIFY trigger |
| `server.js` | MQTT → DB writer + HTTP/WS server + NOTIFY listener |
| `public/index.html` | Modern UI shell |
| `public/style.css` | Dark theme |
| `public/app.js` | WS client, charts, VPD math + zone marker |

## Isolation from existing stack

Designed to run alongside the original `Z_SelfHosting/pgsql` stack with **zero
overlap**. Only EMQX (MQTT broker) is shared.

| Thing | Original | This POC |
|-------|----------|----------|
| Container | `timescaledb` | `timescaledb-vpd` |
| Host port (DB) | 5432 | 5433 |
| Postgres user | `pico` | `vpd` |
| Postgres db | `sensors` | `vpd_sensors` |
| Volume | (none) | `timescaledb_vpd_data` |
| Webapp port | 8000 | 8001 |

Both can run at the same time. No data overwrite, no port clash.

### Optional: copy historical readings into POC DB

```sh
# dump from the original container
docker exec timescaledb pg_dump -U pico -d sensors -t readings --data-only > readings.sql

# load into the POC container
docker exec -i timescaledb-vpd psql -U vpd -d vpd_sensors < readings.sql
```

`init.sql` runs once on first volume init — creates table + trigger
idempotently, never touches existing rows.

## Run

```sh
docker compose up -d --build
```

- Web UI: `http://<host>:8001`
- DB:     `localhost:5433` (user `vpd`, pass `vpd`, db `vpd_sensors`)

```sh
docker compose logs -f webapp
docker compose down            # keeps volume
docker compose down -v         # WIPES the POC volume — careful
```

## Configuration

`server.js` reads env vars (set in `docker-compose.yml`):

| Var | Default | Notes |
|-----|---------|-------|
| `PG_DSN`     | `postgresql://vpd:vpd@timescaledb-vpd:5432/vpd_sensors` | Internal docker net |
| `MQTT_URL`   | `mqtt://192.168.1.2:1883` | EMQX broker |
| `MQTT_TOPIC` | `pico/#` | Wildcard sub |
| `PORT`       | `8000` | Internal — host maps to 8001 |
| `HISTORY`    | `300` | Rows sent on WS connect |

Topic map is in `public/app.js`:

```js
const TOPIC = {
  TEMP: 'pico/temperature/dht22',
  HUMI: 'pico/humidity/dht22',
  CHIP: 'pico/temperature/internal',
};
```

## VPD math

```
SVP(T) = 0.6108 · exp( 17.27·T / (T + 237.3) )    [kPa]
VPD    = SVP(T) · (1 − RH/100)                    [kPa]
```

This is **air-VPD** (assumes leaf temp ≈ air temp). For leaf-VPD subtract ~2 °C
from `T` when computing the leaf SVP and use `SVP(T_leaf) − SVP(T_air)·RH/100`.

### Zones

| kPa range | Zone | Meaning |
|-----------|------|---------|
| 0.0 – 0.4 | Danger | Air saturated. Mold, mildew, poor uptake. |
| 0.4 – 0.8 | Propagation | Soft tissue, weak roots — keep humid. |
| 0.8 – 1.2 | Vegetative | Healthy transpiration, fast growth. |
| 1.2 – 1.6 | Flowering | Strong transpiration, dense bloom. |
| 1.6 +     | Stress | Stomata close, growth stalls. |

## Local dev (no docker)

```sh
npm install
PG_DSN=postgresql://vpd:vpd@localhost:5433/vpd_sensors \
MQTT_URL=mqtt://192.168.1.2:1883 \
node server.js
```

Schema must already be applied. Use the SQL block in `init.sql`.
