# MQTT-MLX90614

Reads object (IR / non-contact) and ambient temperature from an MLX90614 sensor, plus the Pico W internal chip temperature, and publishes all readings to an MQTT broker every 5 seconds.

> Requires `boot.py` to have already connected to WiFi before this runs.

## MQTT Topics

| Topic | Value |
|-------|-------|
| `pico/temperature/internal` | Pico W internal chip temperature (°C) |
| `pico/temperature/object` | IR non-contact object temperature (°C) |
| `pico/temperature/ambient` | MLX90614 ambient temperature (°C) |

## Wiring

| MLX90614 Pin | Pico W Pin |
|---|---|
| VCC | 3.3V (pin 36) |
| GND | GND (pin 38) |
| SDA | GP8 (pin 11) |
| SCL | GP9 (pin 12) |

> No resistors or level shifters needed — the MLX90614 runs at 3.3V and the Pico W I2C pins are 3.3V native.

## Library

The MLX90614 driver is not available via `mip` — install it manually:

```sh
# clone on your computer, then copy to the Pico W via Thonny
git clone https://github.com/mcauser/micropython-mlx90614
```

Copy `mlx90614.py` from the repo to `/lib/mlx90614.py` on the Pico W using Thonny's file panel.

## Configuration

Edit these values at the top of `main.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `MQTT_BROKER` | `192.168.1.2` | IP of your MQTT broker (EMQX) |
| `publish_interval` | `5` | Seconds between publishes |

## Verify sensor is detected (optional)

Run this in the Thonny shell before flashing `main.py`:

```python
from machine import Pin, SoftI2C
i2c = SoftI2C(scl=Pin(9), sda=Pin(8), freq=100000)
print([hex(a) for a in i2c.scan()])  # should print ['0x5a']
```

## Subscribe to readings

```sh
mosquitto_sub -h 192.168.1.2 -t "pico/#" -v
```

## Full stack

To persist and visualise the data, follow the same setup as `MQTT-DHT22`:

```
Pico W → EMQX → mqtt_to_db.py → TimescaleDB → FastAPI WebSocket → Browser
```

The `picow-dht-webapp` works as-is — just add the new topics (`pico/temperature/object`, `pico/temperature/ambient`) to the dashboard cards in `index.html` if needed.
