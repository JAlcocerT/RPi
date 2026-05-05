import express from 'express';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';
import pg from 'pg';
import mqtt from 'mqtt';
import path from 'path';
import { fileURLToPath } from 'url';

const { Pool, Client } = pg;
const __dirname = path.dirname(fileURLToPath(import.meta.url));

const PG_DSN     = process.env.PG_DSN     || 'postgresql://vpd:vpd@timescaledb-vpd:5432/vpd_sensors';
const MQTT_URL   = process.env.MQTT_URL   || 'mqtt://192.168.1.2:1883';
const MQTT_TOPIC = process.env.MQTT_TOPIC || 'pico/#';
const PORT       = parseInt(process.env.PORT || '8000', 10);
const HISTORY    = parseInt(process.env.HISTORY || '300', 10);

const pool = new Pool({ connectionString: PG_DSN });

async function waitForDb(retries = 30) {
  for (let i = 0; i < retries; i++) {
    try {
      await pool.query('SELECT 1');
      return;
    } catch (e) {
      console.log(`DB not ready (${i + 1}/${retries}): ${e.message}`);
      await new Promise(r => setTimeout(r, 2000));
    }
  }
  throw new Error('DB unreachable after retries');
}

await waitForDb();
console.log('DB connected');

// MQTT subscriber → DB insert
const mqttClient = mqtt.connect(MQTT_URL, { reconnectPeriod: 5000 });
mqttClient.on('connect', () => {
  console.log(`MQTT connected: ${MQTT_URL}`);
  mqttClient.subscribe(MQTT_TOPIC, (err) => {
    if (err) console.error('MQTT subscribe err', err.message);
    else console.log(`Subscribed: ${MQTT_TOPIC}`);
  });
});
mqttClient.on('error', (e) => console.error('MQTT err', e.message));
mqttClient.on('message', async (topic, payload) => {
  const value = parseFloat(payload.toString());
  if (Number.isNaN(value)) return;
  try {
    await pool.query('INSERT INTO readings (topic, value) VALUES ($1, $2)', [topic, value]);
    console.log(`${topic}: ${value}`);
  } catch (e) {
    console.error('Insert err', e.message);
  }
});

// Dedicated LISTEN client (notifications need their own connection)
const wsClients = new Set();

async function startListener() {
  const listenClient = new Client({ connectionString: PG_DSN });
  listenClient.on('error', async (e) => {
    console.error('Listener err, reconnecting:', e.message);
    setTimeout(startListener, 3000);
  });
  await listenClient.connect();
  await listenClient.query('LISTEN new_reading');
  listenClient.on('notification', (msg) => {
    let data;
    try { data = JSON.parse(msg.payload); } catch { return; }
    const json = JSON.stringify({ type: 'reading', data });
    for (const ws of wsClients) {
      if (ws.readyState === 1) ws.send(json);
    }
  });
  console.log('LISTEN new_reading active');
}
await startListener();

// HTTP + WS
const app = express();
app.use(express.static(path.join(__dirname, 'public')));

app.get('/api/history', async (req, res) => {
  const limit = Math.min(parseInt(req.query.limit || HISTORY, 10), 5000);
  const { rows } = await pool.query(
    'SELECT ts, topic, value FROM readings ORDER BY ts DESC LIMIT $1',
    [limit]
  );
  res.json(rows.reverse());
});

const server = createServer(app);
const wss = new WebSocketServer({ server, path: '/ws' });

wss.on('connection', async (ws) => {
  wsClients.add(ws);
  ws.on('close', () => wsClients.delete(ws));
  try {
    const { rows } = await pool.query(
      'SELECT ts, topic, value FROM readings ORDER BY ts DESC LIMIT $1',
      [HISTORY]
    );
    ws.send(JSON.stringify({ type: 'history', data: rows.reverse() }));
  } catch (e) {
    console.error('History err', e.message);
  }
});

server.listen(PORT, '0.0.0.0', () => console.log(`Listening on http://0.0.0.0:${PORT}`));
