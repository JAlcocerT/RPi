const fs = require("fs");
const path = require("path");
const http = require("http");
const url = require("url");
const Database = require("better-sqlite3");
const mqtt = require("mqtt");

const PORT = Number(process.env.PORT || 3000);
const MQTT_HOST = process.env.MQTT_HOST || "192.168.1.106";
const MQTT_PORT = Number(process.env.MQTT_PORT || 1883);
const MQTT_URL = process.env.MQTT_URL || `mqtt://${MQTT_HOST}:${MQTT_PORT}`;
const MQTT_USERNAME = process.env.MQTT_USERNAME || "";
const MQTT_PASSWORD = process.env.MQTT_PASSWORD || "";
const PUBLIC_DIR = path.join(__dirname, "public");
const DATA_DIR = path.join(__dirname, "data");
const DB_PATH = path.join(DATA_DIR, "readings.sqlite");

const TOPIC_MAP = {
  "esp32/temperature/dht11": "temperature",
  "esp32/humidity/dht11": "humidity"
};

fs.mkdirSync(DATA_DIR, { recursive: true });

const db = new Database(DB_PATH);
db.pragma("journal_mode = WAL");
db.exec(`
  CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    metric TEXT NOT NULL,
    value REAL NOT NULL,
    received_at TEXT NOT NULL,
    received_ms INTEGER NOT NULL
  );
  CREATE INDEX IF NOT EXISTS idx_readings_metric_received_ms
  ON readings(metric, received_ms);
`);

const insertReading = db.prepare(`
  INSERT INTO readings (topic, metric, value, received_at, received_ms)
  VALUES (?, ?, ?, ?, ?)
`);

const selectSeries = db.prepare(`
  SELECT metric, value, received_at, received_ms
  FROM readings
  WHERE received_ms >= ?
  ORDER BY received_ms ASC
`);

const selectLatest = db.prepare(`
  SELECT metric, value, received_at
  FROM readings
  WHERE metric = ?
  ORDER BY received_ms DESC
  LIMIT 1
`);

let mqttConnected = false;
let mqttLastError = "";

const mqttClient = mqtt.connect(MQTT_URL, {
  username: MQTT_USERNAME || undefined,
  password: MQTT_PASSWORD || undefined,
  reconnectPeriod: 5000,
  connectTimeout: 5000,
  keepalive: 30
});

mqttClient.on("connect", () => {
  mqttConnected = true;
  mqttLastError = "";
  console.log(`MQTT connected to ${MQTT_URL}`);
  mqttClient.subscribe(Object.keys(TOPIC_MAP), (err) => {
    if (err) {
      mqttLastError = err.message;
      console.error("MQTT subscribe failed:", err.message);
      return;
    }
    console.log("Subscribed to DHT11 topics.");
  });
});

mqttClient.on("reconnect", () => {
  mqttConnected = false;
  console.log("MQTT reconnecting...");
});

mqttClient.on("error", (err) => {
  mqttConnected = false;
  mqttLastError = err.message;
  console.error("MQTT error:", err.message);
});

mqttClient.on("close", () => {
  mqttConnected = false;
});

mqttClient.on("message", (topic, payload) => {
  const metric = TOPIC_MAP[topic];
  if (!metric) {
    return;
  }

  const raw = payload.toString().trim();
  const value = Number.parseFloat(raw);
  if (!Number.isFinite(value)) {
    console.warn(`Skipping invalid payload for ${topic}: ${raw}`);
    return;
  }

  const now = Date.now();
  insertReading.run(topic, metric, value, new Date(now).toISOString(), now);
});

function sendJson(res, statusCode, data) {
  res.writeHead(statusCode, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store"
  });
  res.end(JSON.stringify(data));
}

function sendFile(res, filePath) {
  fs.readFile(filePath, (err, content) => {
    if (err) {
      res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
      res.end("Not found");
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const mimeTypes = {
      ".html": "text/html; charset=utf-8",
      ".css": "text/css; charset=utf-8",
      ".js": "application/javascript; charset=utf-8",
      ".json": "application/json; charset=utf-8"
    };

    res.writeHead(200, { "Content-Type": mimeTypes[ext] || "application/octet-stream" });
    res.end(content);
  });
}

function getSeries(hours) {
  const safeHours = Number.isFinite(hours) && hours > 0 ? Math.min(hours, 24 * 30) : 24;
  const since = Date.now() - safeHours * 60 * 60 * 1000;
  const rows = selectSeries.all(since);

  return {
    temperature: rows
      .filter((row) => row.metric === "temperature")
      .map((row) => ({ value: row.value, at: row.received_at, ms: row.received_ms })),
    humidity: rows
      .filter((row) => row.metric === "humidity")
      .map((row) => ({ value: row.value, at: row.received_at, ms: row.received_ms }))
  };
}

function getStatus() {
  const latestTemperature = selectLatest.get("temperature") || null;
  const latestHumidity = selectLatest.get("humidity") || null;

  return {
    mqttConnected,
    mqttUrl: MQTT_URL,
    mqttLastError,
    latestTemperature,
    latestHumidity
  };
}

const server = http.createServer((req, res) => {
  const parsed = url.parse(req.url, true);

  if (parsed.pathname === "/api/status") {
    sendJson(res, 200, getStatus());
    return;
  }

  if (parsed.pathname === "/api/series") {
    const hours = Number.parseFloat(parsed.query.hours);
    sendJson(res, 200, getSeries(hours));
    return;
  }

  const filePath =
    parsed.pathname === "/"
      ? path.join(PUBLIC_DIR, "index.html")
      : path.join(PUBLIC_DIR, parsed.pathname.replace(/^\/+/, ""));

  if (!filePath.startsWith(PUBLIC_DIR)) {
    res.writeHead(403, { "Content-Type": "text/plain; charset=utf-8" });
    res.end("Forbidden");
    return;
  }

  sendFile(res, filePath);
});

server.listen(PORT, () => {
  console.log(`Dashboard listening on http://localhost:${PORT}`);
  console.log(`SQLite database: ${DB_PATH}`);
});
