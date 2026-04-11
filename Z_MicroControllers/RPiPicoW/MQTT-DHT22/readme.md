# MQTT-DHT22

Reads temperature and humidity from a DHT22 sensor (plus the Pico W's internal chip temperature) and publishes all readings to an MQTT broker every 5 seconds.

> Requires `boot.py` to have already connected to WiFi before this runs.

## MQTT Topics

| Topic | Value |
|-------|-------|
| `pico/temperature/internal` | Pico W internal chip temperature (°C) |
| `pico/temperature/dht22` | DHT22 temperature (°C) |
| `pico/humidity/dht22` | DHT22 humidity (%) |

## Wiring

| DHT22 Pin | Pico W Pin |
|-----------|------------|
| VCC       | 3.3V       |
| DATA      | GPIO 15    |
| GND       | GND        |

## Configuration

Edit these values at the top of `main.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `MQTT_BROKER` | `192.168.1.11` | IP of your MQTT broker (EMQX) |
| `publish_interval` | `5` | Seconds between publishes |

## Files

| File | Description |
|------|-------------|
| `main.py` | Main loop — connects to MQTT broker, reads sensors, publishes every 5 seconds |
| `DHT22.py` | PIO-based DHT22 driver by Daniel Perron (MIT License) |

## Error Handling

- **MQTT failure** — disconnects, waits 5 s, reconnects
- **OS error** — calls `machine.reset()` to fully restart the Pico W
- **DHT22 read failure** — logs `"DHT22 sensor error, retrying..."` and skips that publish cycle
