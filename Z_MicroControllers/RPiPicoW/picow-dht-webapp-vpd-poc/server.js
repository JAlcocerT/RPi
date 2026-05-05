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

// Range query — accepts ?minutes=N (default 60). Auto-downsamples past HARD_CAP
// rows using TimescaleDB time_bucket so 7d views stay snappy.
const HARD_CAP = 5000;

function pickBucketMinutes(minutes) {
  if (minutes <= 60)    return 0;     // raw
  if (minutes <= 360)   return 1;     // 6h → 1m buckets
  if (minutes <= 1440)  return 5;     // 24h → 5m buckets
  if (minutes <= 10080) return 30;    // 7d → 30m buckets
  return 60;                          // > 7d → 1h buckets
}

app.get('/api/history', async (req, res) => {
  const minutes = Math.max(1, Math.min(parseInt(req.query.minutes || '60', 10), 60 * 24 * 90));
  const bucketMin = pickBucketMinutes(minutes);

  try {
    if (bucketMin === 0) {
      const { rows } = await pool.query(
        `SELECT ts, topic, value
         FROM readings
         WHERE ts >= NOW() - ($1::int * INTERVAL '1 minute')
         ORDER BY ts ASC
         LIMIT $2`,
        [minutes, HARD_CAP]
      );
      return res.json({ rows, minutes, bucketMin: 0, downsampled: false, count: rows.length });
    }
    const { rows } = await pool.query(
      `SELECT time_bucket(($1::int * INTERVAL '1 minute'), ts) AS ts,
              topic,
              AVG(value)::float8 AS value
       FROM readings
       WHERE ts >= NOW() - ($2::int * INTERVAL '1 minute')
       GROUP BY 1, topic
       ORDER BY 1 ASC`,
      [bucketMin, minutes]
    );
    res.json({ rows, minutes, bucketMin, downsampled: true, count: rows.length });
  } catch (e) {
    console.error('History err', e.message);
    res.status(500).json({ error: e.message });
  }
});

const server = createServer(app);
const wss = new WebSocketServer({ server, path: '/ws' });

// WS only streams live readings — history is fetched on demand via /api/history
// so the client controls the time window.
wss.on('connection', (ws) => {
  wsClients.add(ws);
  ws.on('close', () => wsClients.delete(ws));
});

server.listen(PORT, '0.0.0.0', () => console.log(`Listening on http://0.0.0.0:${PORT}`));
