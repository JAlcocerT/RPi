import asyncio
import json
import asyncpg
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

DB_DSN = "postgresql://pico:pico@192.168.1.2:5432/sensors"

pool = None

SENSOR_TOPICS = {
    "all":   [
        "pico/temperature/dht22", "pico/humidity/dht22",
        "esp32/temperature/dht11", "esp32/humidity/dht11",
        "pico/temperature/internal",
    ],
    "picow": ["pico/temperature/dht22", "pico/humidity/dht22"],
    "esp32": ["esp32/temperature/dht11", "esp32/humidity/dht11"],
}

# TimescaleDB bucket size per requested hour range
# Safe whitelist — values never come from user input
BUCKET = {1: "1 minute", 6: "5 minutes", 24: "15 minutes", 168: "1 hour"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    pool = await asyncpg.create_pool(DB_DSN, min_size=2, max_size=5)
    yield
    await pool.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def index():
    with open("index.html") as f:
        return HTMLResponse(f.read())


@app.get("/history")
async def history(hours: int = 1, sensor: str = "all"):
    topics = SENSOR_TOPICS.get(sensor, SENSOR_TOPICS["all"])
    bucket = BUCKET.get(hours, "15 minutes")

    async with pool.acquire() as conn:
        # bucket and hours are from hardcoded whitelists — safe to inline
        rows = await conn.fetch(
            f"""
            SELECT time_bucket('{bucket}', ts) AS t,
                   topic,
                   AVG(value) AS value
            FROM readings
            WHERE topic = ANY($1)
              AND ts > NOW() - INTERVAL '{hours} hours'
            GROUP BY t, topic
            ORDER BY t
            """,
            topics,
        )

    return [
        {"ts": r["t"].isoformat(), "topic": r["topic"], "value": round(r["value"], 2)}
        for r in rows
    ]


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    conn = await asyncpg.connect(DB_DSN)
    queue: asyncio.Queue = asyncio.Queue()

    def handle_notify(conn, pid, channel, payload):
        queue.put_nowait(payload)

    await conn.add_listener("new_reading", handle_notify)

    try:
        while True:
            try:
                payload = await asyncio.wait_for(queue.get(), timeout=30)
                await websocket.send_text(
                    json.dumps({"type": "reading", "data": json.loads(payload)})
                )
            except asyncio.TimeoutError:
                continue
    except WebSocketDisconnect:
        pass
    finally:
        await conn.remove_listener("new_reading", handle_notify)
        await conn.close()
