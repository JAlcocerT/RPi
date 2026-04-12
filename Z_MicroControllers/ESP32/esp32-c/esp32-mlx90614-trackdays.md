# ESP32 + MLX90614 — Brake Temperature Monitoring for Track Days

Using the GY-906 MLX90614 to monitor brake disc temperatures during track days and road use.

---

## What a pyrometer is

A pyrometer measures temperature from a distance using infrared radiation — no physical contact with the target needed. The MLX90614 is a low-cost pyrometer. Professional motorsport versions are the same principle, built for harsher environments and with a much narrower field of view.

---

## MLX90614 vs professional pyrometers

| Device | FOV | Max range | Price | Use case |
|--------|-----|-----------|-------|----------|
| MLX90614 GY-906 (yours) | 90° | 380°C | ~€5 | Hobby, road car, track days |
| MLX90640 (thermal array) | 55°×35° | 300°C | ~€40 | Hotspot mapping, thermal imaging |
| Optris CS / similar | ~2° | 1000°C | ~€300 | Serious circuit use |
| Professional motorsport pyrometer | 1–5° | 1500°C+ | €500+ | Motorsport, endurance racing |

---

## What the MLX90614 can realistically do on a car

**Good for:**
- Detecting brake overheating on track days
- Comparing left vs right disc temperature (sticking caliper shows one side running much hotter)
- Logging temperature trends over a session
- Spotting if brake pads are past their thermal limit

**Not good for:**
- Pinpoint spot readings — 90° FOV means at 10 cm distance you're averaging a ~18 cm diameter circle (disc + caliper + air)
- Sustained use in the engine bay — ESP32 is rated to **85°C max**, engine bays often exceed this
- Carbon ceramic discs — those exceed the 380°C measurement limit under hard braking on circuit

---

## Brake disc temperature reference

| Condition | Disc temp (approx) |
|-----------|-------------------|
| Cold / road driving | 50–150°C |
| Spirited road driving | 150–300°C |
| Track day (standard pads) | 300–500°C |
| Track day (performance pads) | 400–700°C |
| Endurance / motorsport | 600–900°C+ |

> The MLX90614's 380°C limit covers road use and light track days comfortably. Hard circuit use with performance brake pads will exceed this.

---

## Mounting recommendations

- **Distance:** 5–15 cm from the disc face — closer reduces the cone of measurement
- **Angle:** perpendicular to the disc surface for best accuracy
- **Location:** behind the wheel arch liner or through a small hole in the dust shield — away from direct road spray
- **Avoid:** pointing at the caliper (much hotter than the disc and will give misleading readings)
- **Heat shield:** wrap the GY-906 module and ESP32 in fibreglass sleeving or mount behind a small aluminium shield — radiated heat from the disc will warm the sensor housing and skew ambient readings

---

## Known limitations in automotive environments

| Issue | Impact | Mitigation |
|-------|--------|------------|
| 90° wide FOV | Reads disc + air + caliper averaged together | Mount as close as practical (5–10 cm) |
| ESP32 max 85°C | Will brownout or crash if housing gets too hot | Mount away from disc radiated heat; add heat shield |
| I2C noise from ignition/alternator | Corrupted readings or sensor lockup | Use short SDA/SCL wires; twist the pair; add 100nF decoupling cap on VCC |
| Vibration | PCB module not rated for automotive vibration | Pot the module in silicone or use a rigid enclosure with foam padding |
| 380°C measurement limit | Saturates under hard circuit braking | Accept clipped readings as "very hot" events; use as warning trigger |

---

## Practical use — what to look for in the data

**Sticking caliper:**
One side stays 80–100°C hotter than the other at the same axle after a session. The hot side caliper pistons are not retracting fully.

**Brake fade warning:**
Object temperature climbing above 300°C with standard pads — time to cool down. Pad compounds have a max operating temperature; exceed it and braking distance increases sharply.

**Pad bedding check:**
New pads should be gradually heat-cycled. Log temperatures during the bedding session — consistent readings on both sides confirm even contact.

**Session comparison:**
Compare peak temperatures across sessions with the same setup to detect brake bias changes or pad wear.

---

## MQTT topics (from `esp32-mlx90614-mqtt.cpp`)

| Topic | Value |
|-------|-------|
| `esp32/temperature/mlx/object` | Disc-facing IR temperature (°C) |
| `esp32/temperature/mlx/ambient` | Sensor board ambient temperature (°C) |

The ambient reading is useful to confirm the sensor housing is not overheating — if ambient climbs above 60–70°C the housing is getting too hot and needs better shielding.

---

## Upgrade path

If the MLX90614 proves useful and you want more accuracy:

1. **MLX90640** (~€40) — 32×24 thermal array, can map temperature across the whole disc face and find hotspots. Same I2C wiring, different library.
2. **Narrowband pyrometer module** (~€100–300) — 2–5° FOV, analog 0–5V or RS232 output, needs a voltage divider to interface with ESP32 ADC.
3. **Two MLX90614s per axle** — one per disc, compare left vs right directly in the dashboard.
