// Topic map — adjust if your Pico publishes elsewhere.
const TOPIC = {
  TEMP: 'pico/temperature/dht22',
  HUMI: 'pico/humidity/dht22',
  CHIP: 'pico/temperature/internal',
};

const MAX_POINTS = 120;

// State
const series = {
  ts:   [],
  temp: [],
  humi: [],
  chip: [],
  vpd:  [],
};
let last = { temp: null, humi: null, chip: null };
let prev = { temp: null, humi: null, chip: null };

// VPD math (kPa) — air-VPD approximation
function svp(t) { return 0.6108 * Math.exp((17.27 * t) / (t + 237.3)); }
function vpdKPa(tAir, rh) { return svp(tAir) * (1 - rh / 100); }

function vpdZone(v) {
  if (v < 0.4)  return { idx: 0, label: 'Danger — too humid',     cls: 'z1' };
  if (v < 0.8)  return { idx: 1, label: 'Propagation',            cls: 'z2' };
  if (v < 1.2)  return { idx: 2, label: 'Vegetative',             cls: 'z3' };
  if (v < 1.6)  return { idx: 3, label: 'Flowering',              cls: 'z4' };
  return        { idx: 4, label: 'Stress — too dry',              cls: 'z5' };
}

// Charts
const ctxTH  = document.getElementById('chart-th').getContext('2d');
const ctxVPD = document.getElementById('chart-vpd').getContext('2d');

const commonScales = (yLabel) => ({
  x: {
    ticks: { color: '#8a93b8', maxTicksLimit: 8, font: { size: 10 } },
    grid:  { color: 'rgba(255,255,255,0.04)' },
  },
  y: {
    title: { display: true, text: yLabel, color: '#8a93b8', font: { size: 11 } },
    ticks: { color: '#8a93b8' },
    grid:  { color: 'rgba(255,255,255,0.06)' },
  },
});

const chartTH = new Chart(ctxTH, {
  type: 'line',
  data: {
    labels: series.ts,
    datasets: [
      { label: 'Air T (°C)', data: series.temp, borderColor: '#ff7a45',
        backgroundColor: 'rgba(255,122,69,0.12)', tension: 0.3, pointRadius: 0, borderWidth: 2, yAxisID: 'y' },
      { label: 'RH (%)',     data: series.humi, borderColor: '#38bdf8',
        backgroundColor: 'rgba(56,189,248,0.12)', tension: 0.3, pointRadius: 0, borderWidth: 2, yAxisID: 'y1' },
    ],
  },
  options: {
    animation: false,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: { legend: { labels: { color: '#e6ecff', boxWidth: 14, font: { size: 11 } } } },
    scales: {
      x: { ticks: { color: '#8a93b8', maxTicksLimit: 8, font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.04)' } },
      y:  { position: 'left',  title: { display: true, text: '°C', color: '#ff7a45' }, ticks: { color: '#8a93b8' }, grid: { color: 'rgba(255,255,255,0.06)' } },
      y1: { position: 'right', title: { display: true, text: '%',  color: '#38bdf8' }, ticks: { color: '#8a93b8' }, grid: { drawOnChartArea: false } },
    },
  },
});

const chartVPD = new Chart(ctxVPD, {
  type: 'line',
  data: {
    labels: series.ts,
    datasets: [{
      label: 'VPD (kPa)', data: series.vpd, borderColor: '#34d399',
      backgroundColor: 'rgba(52,211,153,0.18)', tension: 0.3, pointRadius: 0, borderWidth: 2, fill: true,
    }],
  },
  options: {
    animation: false,
    maintainAspectRatio: false,
    plugins: { legend: { labels: { color: '#e6ecff', font: { size: 11 } } } },
    scales: commonScales('kPa'),
  },
});

// Update helpers
function trendArrow(curr, prevVal) {
  if (prevVal === null || curr === null) return '—';
  const d = curr - prevVal;
  if (Math.abs(d) < 0.05) return '→ stable';
  return d > 0 ? `↑ +${d.toFixed(2)}` : `↓ ${d.toFixed(2)}`;
}

function setStatus(state, txt) {
  const el = document.getElementById('status');
  el.className = `status status--${state}`;
  el.textContent = txt;
}

function setVal(id, v, digits = 1) {
  document.getElementById(id).textContent = v == null ? '--' : v.toFixed(digits);
}

function recomputeVPD() {
  if (last.temp == null || last.humi == null) return null;
  const v = vpdKPa(last.temp, last.humi);
  setVal('val-vpd', v, 2);
  const z = vpdZone(v);
  document.getElementById('vpd-zone').textContent = z.label;
  document.getElementById('vpd-readout').textContent = `${v.toFixed(2)} kPa · ${z.label}`;
  // marker position 0..1.8 mapped to 0..100%
  const pct = Math.max(0, Math.min(100, (v / 1.8) * 100));
  document.getElementById('vpd-marker').style.left = `${pct}%`;
  return v;
}

function pushPoint(ts, topic, value) {
  const time = new Date(ts).toLocaleTimeString();

  if (topic === TOPIC.TEMP) {
    prev.temp = last.temp; last.temp = value;
    setVal('val-temp', value, 1);
    document.getElementById('trend-temp').textContent = trendArrow(value, prev.temp);
  } else if (topic === TOPIC.HUMI) {
    prev.humi = last.humi; last.humi = value;
    setVal('val-humi', value, 1);
    document.getElementById('trend-humi').textContent = trendArrow(value, prev.humi);
  } else if (topic === TOPIC.CHIP) {
    prev.chip = last.chip; last.chip = value;
    setVal('val-chip', value, 1);
    document.getElementById('trend-chip').textContent = trendArrow(value, prev.chip);
  } else {
    return;
  }

  const v = recomputeVPD();

  // Add a chart sample only when both T and RH are known.
  if (last.temp != null && last.humi != null) {
    series.ts.push(time);
    series.temp.push(last.temp);
    series.humi.push(last.humi);
    series.chip.push(last.chip);
    series.vpd.push(v);
    while (series.ts.length > MAX_POINTS) {
      series.ts.shift(); series.temp.shift(); series.humi.shift(); series.chip.shift(); series.vpd.shift();
    }
    chartTH.update('none');
    chartVPD.update('none');
    document.getElementById('chart-window').textContent = `last ${series.ts.length} samples`;
  }
}

// WebSocket
function connect() {
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  const ws = new WebSocket(`${proto}//${location.host}/ws`);

  ws.onopen  = () => setStatus('ok', 'live');
  ws.onclose = () => { setStatus('bad', 'disconnected'); setTimeout(connect, 3000); };
  ws.onerror = () => setStatus('bad', 'error');

  ws.onmessage = ({ data }) => {
    let msg;
    try { msg = JSON.parse(data); } catch { return; }
    if (msg.type === 'history') {
      msg.data.forEach(r => pushPoint(r.ts, r.topic, r.value));
    } else if (msg.type === 'reading') {
      pushPoint(msg.data.ts, msg.data.topic, msg.data.value);
    }
  };
}
connect();
