# Pico W DHT22 — Live Web App

Real-time temperature and humidity dashboard.

FastAPI serves a WebSocket that pushes new readings to the browser the instant they land in TimescaleDB — no polling, no frameworks.

```
Pico W → EMQX → Python subscriber → TimescaleDB
                                          │
                                     FastAPI (WebSocket)
                                          │
                                       Browser
```

> See the `MQTT-DHT22` and setup a emqx server.

## Prerequisites

- TimescaleDB running at `192.168.1.2:5432` (see `historical-data.md` Strategy 4)
- The `readings` hypertable exists with the `notify_new_reading` trigger in place
- The MQTT subscriber from Strategy 4 is running and writing data

## Setup

```sh
#uv init
#uv add
pip install -r requirements.txt
```

## Run

```sh
uvicorn main:app --host 0.0.0.0 --port 8000
```

Then open `http://localhost:8000` in a browser.

## What it does

- On connect: loads the **last 20 readings** from TimescaleDB as history
- Live: PostgreSQL `LISTEN/NOTIFY` pushes each new insert to the browser via **WebSocket** the moment it arrives
- Displays: DHT22 temperature, humidity, and Pico W chip temperature as live cards + scrolling line chart

## Files

| File | Description |
|------|-------------|
| `main.py` | FastAPI app — WebSocket endpoint + PostgreSQL NOTIFY listener |
| `index.html` | Single-page frontend — vanilla JS, Chart.js, no framework |
| `requirements.txt` | Python dependencies |

## DB connection

Edit `DB_DSN` at the top of `main.py`:

```python
DB_DSN = "postgresql://pico:pico@192.168.1.2:5432/sensors"
```
