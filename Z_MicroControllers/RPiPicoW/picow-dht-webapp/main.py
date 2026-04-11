import asyncio
import json
import asyncpg
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

DB_DSN = "postgresql://pico:pico@192.168.1.2:5432/sensors"

app = FastAPI()


@app.get("/")
async def index():
    with open("index.html") as f:
        return HTMLResponse(f.read())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    conn = await asyncpg.connect(DB_DSN)
    queue = asyncio.Queue()

    # Send last 20 readings on connect
    rows = await conn.fetch(
        "SELECT ts, topic, value FROM readings ORDER BY ts DESC LIMIT 20"
    )
    history = [{"ts": str(r["ts"]), "topic": r["topic"], "value": r["value"]} for r in reversed(rows)]
    await websocket.send_text(json.dumps({"type": "history", "data": history}))

    # Listen for new inserts via NOTIFY
    async def handle_notify(conn, pid, channel, payload):
        await queue.put(payload)

    await conn.add_listener("new_reading", handle_notify)

    try:
        while True:
            payload = await asyncio.wait_for(queue.get(), timeout=30)
            await websocket.send_text(json.dumps({"type": "reading", "data": json.loads(payload)}))
    except (asyncio.TimeoutError, WebSocketDisconnect):
        pass
    finally:
        await conn.remove_listener("new_reading", handle_notify)
        await conn.close()
