# Pico W DHT22 — Live Web App

Real-time temperature and humidity dashboard. FastAPI serves a WebSocket that pushes new readings to the browser the instant they land in TimescaleDB — no polling, no frameworks.

```
Pico W → EMQX → mqtt_to_db.py → TimescaleDB
                                      │
                                 FastAPI (WebSocket)
                                      │
                                   Browser
```

> See `MQTT-DHT22/` for the Pico W side and EMQX setup.

## Files

| File | Description |
|------|-------------|
| `mqtt_to_db.py` | Subscribes to EMQX `pico/#` and writes every reading to TimescaleDB |
| `main.py` | FastAPI app — WebSocket endpoint + PostgreSQL NOTIFY listener |
| `index.html` | Single-page frontend — vanilla JS, Chart.js, no framework |
| `requirements.txt` | Python dependencies |
| `mqtt-to-db.service` | systemd unit to run `mqtt_to_db.py` in the background |

## 1. TimescaleDB

```sh
docker run -d --name timescaledb \
  -e POSTGRES_USER=pico \
  -e POSTGRES_PASSWORD=pico \
  -e POSTGRES_DB=sensors \
  -p 5432:5432 \
  timescale/timescaledb:latest-pg16
```

## 2. Create table + trigger (run once)

```sh
docker exec -it timescaledb psql -U pico -d sensors
```

```sql
CREATE TABLE readings (
    ts    TIMESTAMPTZ      NOT NULL DEFAULT NOW(),
    topic TEXT             NOT NULL,
    value DOUBLE PRECISION NOT NULL
);

SELECT create_hypertable('readings', 'ts');

CREATE OR REPLACE FUNCTION notify_new_reading()
RETURNS trigger AS $$
BEGIN
  PERFORM pg_notify('new_reading', row_to_json(NEW)::text);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER readings_notify
AFTER INSERT ON readings
FOR EACH ROW EXECUTE FUNCTION notify_new_reading();
```

## 3. Install dependencies

```sh
#uv add -r requirements.txt
pip install -r requirements.txt
# or
uv sync
```

## 4. Run the MQTT subscriber in the background

**Quick (foreground test):**

```sh
uv run mqtt_to_db.py
```

**Persistent (systemd — survives reboots):**

```sh
# copy the service file and enable it
sudo cp mqtt-to-db.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mqtt-to-db
sudo systemctl start mqtt-to-db

# check it's running
sudo systemctl status mqtt-to-db
```

## 5. Run the web app

```sh
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

Then open `http://192.168.1.2:8000` in a browser.

## What it does

- On connect: loads the **last 20 readings** from TimescaleDB as history
- Live: PostgreSQL `LISTEN/NOTIFY` pushes each new insert to the browser via **WebSocket** the moment it arrives
- Displays: DHT22 temperature, humidity, and Pico W chip temperature as live cards + scrolling line chart

## tmux — running over SSH (e.g. from Termux)

`mqtt_to_db.py` and `uvicorn` both block the terminal. 

If you're on SSH, closing the connection kills both. 

Use tmux so processes survive disconnects.

```sh
# start each process in its own named session and leave it running
tmux new-session -d -s mqtt "uv run mqtt_to_db.py"
tmux new-session -d -s webapp "uv run uvicorn main:app --host 0.0.0.0 --port 8000"
```

```sh
# attach to a session to see its output
tmux attach -t mqtt
tmux attach -t webapp

# detach without killing it
Ctrl+B  then  D

# list all running sessions
tmux ls

# kill a session
tmux kill-session -t mqtt
```

> If you want to leave both running overnight and just close your Termux SSH — just detach and disconnect. They keep running on the server.

## Configuration

All connection settings are at the top of each script:

| Setting | File | Default |
|---------|------|---------|
| MQTT broker | `mqtt_to_db.py` | `192.168.1.2` |
| DB connection | `main.py` | `postgresql://pico:pico@192.168.1.2:5432/sensors` |
| DB connection | `mqtt_to_db.py` | `192.168.1.2:5432` |
