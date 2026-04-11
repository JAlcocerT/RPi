Collection of Python scripts that run on a Raspberry Pi (or any Linux machine) to interact with an MQTT broker.

> Broker: EMQX at `192.168.1.2:1883`

## Files

| File | Purpose |
|------|---------|
| `DHT_to_MQTT.py` | Reads a DHT22/DHT11 sensor wired to the Pi's GPIO and publishes temperature + humidity to MQTT. RPi equivalent of the Pico W `main.py`. |
| `MQTT_to_Streamlit.py` | Subscribes to an MQTT topic and shows the latest message in a Streamlit web UI. Live view only — no history saved. |
| `python_push.py` | One-shot test: publishes a single `"Hello from Python!"` to `python/mqtt`. Useful for verifying the broker is reachable. |
| `Python_push_distribution.py` | Publishes fake sensor data (random normal distribution, 0–50) every 0.5 s to `python/mqtt`. Mock data generator for testing the Streamlit UI without real hardware. |

## Install dependencies

```sh
pip install paho-mqtt streamlit adafruit-circuitpython-dht
```

## Run

```sh
# Read DHT sensor and push to MQTT (RPi with sensor wired to GPIO 4)
python3 DHT_to_MQTT.py

# Live Streamlit viewer (update broker IP and topic before running)
streamlit run MQTT_to_Streamlit.py

# One-shot broker test
python3 python_push.py

# Fake data generator
python3 Python_push_distribution.py
```

## Notes

- `DHT_to_MQTT.py` reads broker/pin/topic from environment variables — no need to edit the file:
  ```sh
  MQTT_BROKER=192.168.1.2 DHT_PIN=4 python3 DHT_to_MQTT.py
  ```
- `MQTT_to_Streamlit.py` is currently pointed at `192.168.3.200` / topic `python/mqtt` — update both to match your setup (`192.168.1.2`, `pico/#`) before running.
- None of these scripts persist data to a database. See `../MQTT-DHT22/historical-data.md` for strategies to save historical readings.

## Install paho-mqtt

```sh
pip install paho-mqtt
```
