# Tech Stack — Pico W VPD POC

End-to-end inventory: hardware → wire protocol → storage → server → browser →
container runtime. Every piece, what it does, why it was picked, what would
replace it.

```
┌────────────┐   WiFi    ┌────────┐  TCP   ┌─────────────┐  TCP  ┌────────────────┐  WS  ┌─────────┐
│  Pico W    │──────────▶│  EMQX  │───────▶│  Node.js    │──────▶│  TimescaleDB   │─────▶│ Browser │
│ MicroPython│  MQTT     │ broker │ MQTT   │  server.js  │  pg   │   PostgreSQL   │ NOTIFY│ Chart.js│
└────────────┘           └────────┘        └─────────────┘       └────────────────┘      └─────────┘
   sensor                  pub/sub             ingest +              hypertable             live UI
                                               LISTEN                + trigger
```

## 1. Hardware — edge

| Piece | Choice | Why |
|------|--------|-----|
| MCU | **Raspberry Pi Pico W** (RP2040 + CYW43439 WiFi) | Cheap, native MicroPython, dual-core M0+, on-board WiFi, on-die temp sensor (ADC ch4). |
| Sensor | **DHT22 (AM2302)** | One-wire, ±0.5 °C / ±2 %RH, good enough for VPD trends. Limit: 0.5 Hz read rate, no leaf temp. |
| (Optional) | MLX90614 IR | Adds non-contact leaf temp → upgrade air-VPD to leaf-VPD. |
| Power | USB / battery | Pico W draws ~30–80 mA active. |

Firmware: **MicroPython v1.20** (`RPiPicoW/MQTT-DHT22/main.py`). One `boot.py`
brings up WiFi, `main.py` loops sensor read + MQTT publish.

## 2. Transport — MQTT

| | |
|---|---|
| **Broker** | **EMQX** (open-source MQTT 5 broker) at `192.168.1.2:1883` |
| **Client lib (edge)** | `umqtt.simple` (MicroPython) |
| **Client lib (server)** | [`mqtt`](https://www.npmjs.com/package/mqtt) v5.x for Node |
| **QoS** | 0 (fire-and-forget) — fine for non-critical telemetry |
| **Topic shape** | `pico/<measurement>/<sensor>` e.g. `pico/temperature/dht22` |

Why MQTT over HTTP polling: tiny RAM/CPU footprint on Pico W, push semantics,
broker decouples publishers from consumers (multiple subs, retained messages,
LWT possible later).

## 3. Storage — TimescaleDB

| | |
|---|---|
| **Image** | `timescale/timescaledb:latest-pg16` |
| **Engine** | PostgreSQL 16 + TimescaleDB extension |
| **Schema** | single hypertable `readings(ts TIMESTAMPTZ, topic TEXT, value DOUBLE PRECISION)` |
| **Index** | `(topic, ts DESC)` for fast “last N for topic X” lookups |
| **Realtime fan-out** | `LISTEN/NOTIFY` channel `new_reading` + `AFTER INSERT` trigger that emits `row_to_json(NEW)` |
| **Volume** | named: `timescaledb_vpd_data` |

Why Timescale, not plain Postgres: hypertables = automatic time-based
partitioning, retention policies, continuous aggregates (e.g. minute averages)
when the data grows. Uses standard SQL — drop-in for any pg client.

Why a trigger + NOTIFY (not polling): browser sees inserts ~immediately, server
holds a single dedicated `LISTEN` connection, no per-client query loop.

## 4. Server — Node.js single process

| | |
|---|---|
| **Runtime** | **Node 20 LTS (Alpine)** |
| **Module system** | ESM (`"type": "module"` in `package.json`) |
| **Process model** | One process, three concurrent roles: MQTT subscriber, HTTP/WS server, pg LISTENer |
| **HTTP** | [`express`](https://expressjs.com) ^4.19 — static file serving + `/api/history` |
| **WebSocket** | [`ws`](https://www.npmjs.com/package/ws) ^8.18 — pure WS server attached to the same `http.Server` |
| **Postgres client** | [`pg`](https://node-postgres.com) ^8.13 — `Pool` for inserts/queries, dedicated `Client` for LISTEN |
| **MQTT client** | [`mqtt`](https://www.npmjs.com/package/mqtt) ^5.10 — auto-reconnect every 5 s |
| **DB readiness** | bespoke `waitForDb()` — retries `SELECT 1` 30× × 2 s |

Why Node: single async runtime handles MQTT events + WS broadcast + pg LISTEN
all on one event loop. Zero build step (vanilla ESM), small Alpine image.

Why `express` + `ws` (not Fastify, not Socket.IO): minimal deps, no protocol
extension on top of WS — frontend uses native `WebSocket`, no client lib.

Why two pg connections: `LISTEN` ties up a connection — keeping it on the pool
would block other queries. Pool for writes/reads, dedicated `Client` for
LISTEN.

## 5. Frontend — vanilla, no build

| | |
|---|---|
| **Framework** | **None.** Plain HTML + ES modules. |
| **Charting** | [Chart.js 4.4](https://www.chartjs.org) via CDN (UMD bundle) |
| **Realtime** | native `WebSocket` API, auto-reconnect on close |
| **Style** | hand-written CSS, custom-properties theming, dark/glassy gradient |
| **Layout** | CSS Grid + Flexbox, mobile-first breakpoints at 800/460 px |

Why no React/Vue/Svelte: dashboard is ~150 LOC of glue + 2 charts. No build
toolchain to maintain, page hot-loads on save. CDN script-tag for Chart.js
keeps Dockerfile copy minimal.

## 6. VPD compute (client-side)

```js
SVP(T) = 0.6108 · exp( 17.27·T / (T + 237.3) )    // Tetens formula, kPa
VPD    = SVP(T) · (1 − RH/100)                    // air-VPD approximation
```

Lives in `public/app.js` — cheap, runs on every reading, no server round-trip.
Could move to a Postgres generated column or continuous aggregate if you want
historical VPD without recomputing.

Zone thresholds (kPa) — horticulture convention: <0.4 danger, 0.4–0.8
propagation, 0.8–1.2 vegetative, 1.2–1.6 flowering, >1.6 stress.

## 7. Container & orchestration

| | |
|---|---|
| **Engine** | Docker / Docker Compose v2 |
| **Compose project** | this folder; 2 services: `timescaledb-vpd`, `webapp` |
| **Network** | implicit default bridge, services reach each other by service name |
| **Build** | `Dockerfile` → `node:20-alpine` base, `npm install --omit=dev`, copies `server.js` + `public/` |
| **Init** | `init.sql` mounted at `/docker-entrypoint-initdb.d/init.sql:ro` (runs once on empty volume) |
| **Restart** | `restart: always` on both — survives reboots |
| **Persistence** | named volume `timescaledb_vpd_data` (NOT bind mount — portable) |

Host port mapping (intentionally non-conflicting with the legacy stack):

| Service | Container port | Host port |
|---------|----------------|-----------|
| timescaledb-vpd | 5432 | **5433** |
| webapp | 8000 | **8078** (current; was 8001) |

## 8. Versions snapshot

```
node:           20-alpine     (Dockerfile)
postgres:       16            (timescale/timescaledb:latest-pg16)
timescaledb:    latest        (whichever ships with -pg16 tag at pull time)
express:        ^4.19.2
ws:             ^8.18.0
pg:             ^8.13.1
mqtt:           ^5.10.1
chart.js:       4.4.4         (CDN pin)
```

Pin `latest-pg16` to a digest if you want fully reproducible rebuilds.

## 9. What's intentionally NOT here

| Skipped | Why |
|--------|-----|
| Auth (login, JWT) | LAN-only POC. Add reverse-proxy + basic-auth or Authelia if exposed. |
| TLS | Same — terminate at Caddy/Traefik if needed. |
| Migration tool | One-table schema, idempotent SQL, no churn. Add `node-pg-migrate` if it grows. |
| ORM | Two queries total. Raw `pg` is clearer than Prisma/Drizzle here. |
| Test suite | POC. Manual smoke test = open browser. |
| TypeScript | Build step not justified for ~200 LOC. |
| Logging stack | `console.log` to stdout → `docker compose logs`. Pipe to Loki/journald if fleet grows. |
| Secret manager | Creds are `vpd:vpd` in compose — fine for LAN, do not ship as-is. |

## 10. Where each layer lives

| Concern | File(s) |
|--------|---------|
| Sensor + publish | `RPiPicoW/MQTT-DHT22/main.py` (outside this folder) |
| Broker | EMQX container (outside this folder) |
| Schema | `init.sql` |
| Ingest + LISTEN + WS + HTTP | `server.js` |
| UI shell | `public/index.html` |
| Styling | `public/style.css` |
| Logic + charts + VPD | `public/app.js` |
| Build | `Dockerfile`, `.dockerignore` |
| Orchestration | `docker-compose.yml` |
| Deps lock | `package.json` (no lockfile committed yet — add `package-lock.json` for reproducible builds) |
