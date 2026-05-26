const tempCanvas = document.getElementById("temp-chart");
const humiCanvas = document.getElementById("humi-chart");
const brokerStatusEl = document.getElementById("broker-status");
const brokerErrorEl = document.getElementById("broker-error");
const tempValueEl = document.getElementById("temp-value");
const humiValueEl = document.getElementById("humi-value");
const tempTimeEl = document.getElementById("temp-time");
const humiTimeEl = document.getElementById("humi-time");
const hoursSelectEl = document.getElementById("hours-select");

function formatReading(reading, unit) {
  if (!reading) {
    return "--";
  }
  return `${Number(reading.value).toFixed(unit === "%" ? 1 : 2)} ${unit}`;
}

function formatTime(value) {
  if (!value) {
    return "No data yet";
  }
  return new Date(value).toLocaleString();
}

function drawSeries(canvas, points, color, label, unit) {
  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;
  const padding = { top: 22, right: 20, bottom: 34, left: 52 };
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;

  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#fffdf9";
  ctx.fillRect(0, 0, width, height);

  if (!points.length) {
    ctx.fillStyle = "#5c666c";
    ctx.font = "16px Georgia";
    ctx.fillText(`No ${label.toLowerCase()} data yet`, padding.left, height / 2);
    return;
  }

  const minX = points[0].ms;
  const maxX = points[points.length - 1].ms;
  let minY = Math.min(...points.map((point) => point.value));
  let maxY = Math.max(...points.map((point) => point.value));

  if (minY === maxY) {
    minY -= 1;
    maxY += 1;
  }

  const pad = (maxY - minY) * 0.15;
  minY -= pad;
  maxY += pad;

  const xScale = (value) =>
    padding.left + ((value - minX) / Math.max(maxX - minX, 1)) * plotWidth;
  const yScale = (value) =>
    padding.top + (1 - (value - minY) / (maxY - minY)) * plotHeight;

  ctx.strokeStyle = "rgba(24, 33, 38, 0.12)";
  ctx.lineWidth = 1;
  ctx.font = "12px Georgia";
  ctx.fillStyle = "#5c666c";

  for (let i = 0; i <= 4; i += 1) {
    const y = padding.top + (plotHeight / 4) * i;
    const value = maxY - ((maxY - minY) / 4) * i;
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    ctx.lineTo(width - padding.right, y);
    ctx.stroke();
    ctx.fillText(`${value.toFixed(1)} ${unit}`, 8, y + 4);
  }

  for (let i = 0; i <= 4; i += 1) {
    const x = padding.left + (plotWidth / 4) * i;
    const index = Math.min(points.length - 1, Math.round(((points.length - 1) / 4) * i));
    const stamp = new Date(points[index].ms);
    const text = stamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    ctx.beginPath();
    ctx.moveTo(x, padding.top);
    ctx.lineTo(x, height - padding.bottom);
    ctx.stroke();
    ctx.fillText(text, x - 18, height - 12);
  }

  const gradient = ctx.createLinearGradient(0, padding.top, 0, height - padding.bottom);
  gradient.addColorStop(0, `${color}44`);
  gradient.addColorStop(1, `${color}08`);

  ctx.beginPath();
  points.forEach((point, index) => {
    const x = xScale(point.ms);
    const y = yScale(point.value);
    if (index === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  });
  ctx.lineTo(xScale(points[points.length - 1].ms), height - padding.bottom);
  ctx.lineTo(xScale(points[0].ms), height - padding.bottom);
  ctx.closePath();
  ctx.fillStyle = gradient;
  ctx.fill();

  ctx.beginPath();
  points.forEach((point, index) => {
    const x = xScale(point.ms);
    const y = yScale(point.value);
    if (index === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  });
  ctx.strokeStyle = color;
  ctx.lineWidth = 3;
  ctx.stroke();

  const lastPoint = points[points.length - 1];
  const lastX = xScale(lastPoint.ms);
  const lastY = yScale(lastPoint.value);
  ctx.beginPath();
  ctx.arc(lastX, lastY, 5, 0, Math.PI * 2);
  ctx.fillStyle = color;
  ctx.fill();
}

async function refresh() {
  const hours = hoursSelectEl.value;
  const [statusRes, seriesRes] = await Promise.all([
    fetch("/api/status"),
    fetch(`/api/series?hours=${encodeURIComponent(hours)}`)
  ]);

  const status = await statusRes.json();
  const series = await seriesRes.json();

  brokerStatusEl.textContent = status.mqttConnected ? `Connected to ${status.mqttUrl}` : `Disconnected from ${status.mqttUrl}`;
  brokerErrorEl.textContent = status.mqttLastError || "none";

  tempValueEl.textContent = formatReading(status.latestTemperature, "C");
  humiValueEl.textContent = formatReading(status.latestHumidity, "%");
  tempTimeEl.textContent = formatTime(status.latestTemperature && status.latestTemperature.received_at);
  humiTimeEl.textContent = formatTime(status.latestHumidity && status.latestHumidity.received_at);

  drawSeries(tempCanvas, series.temperature, "#d4552d", "Temperature", "C");
  drawSeries(humiCanvas, series.humidity, "#177e89", "Humidity", "%");
}

hoursSelectEl.addEventListener("change", () => {
  refresh().catch((error) => {
    brokerErrorEl.textContent = error.message;
  });
});

refresh().catch((error) => {
  brokerErrorEl.textContent = error.message;
});

setInterval(() => {
  refresh().catch((error) => {
    brokerErrorEl.textContent = error.message;
  });
}, 5000);
