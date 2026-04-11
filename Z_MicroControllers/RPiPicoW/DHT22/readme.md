# DHT22 — Temperature & Humidity Sensor

Reads temperature and humidity from a DHT22 sensor using the **PIO state machine** on the RP2040, printing results to the serial console.

## Wiring

| DHT22 Pin | Pico W Pin |
|-----------|------------|
| VCC       | 3.3V       |
| DATA      | GPIO 15    |
| GND       | GND        |

> GPIO 15 is configured with an internal pull-up resistor.

## Files

| File | Description |
|------|-------------|
| `DHT22.py` | PIO-based driver by Daniel Perron (MIT License). Uses the RP2040 PIO state machine to handle the timing-critical DHT22 protocol in hardware. |
| `main.py` | Reads temperature and humidity every 500 ms and prints to console. |

## Output

```
Temp: 23.4 °C, Humi: 55.2 %
```

Returns `"Sensor error"` on checksum failure.

## References

* [YouTube walkthrough](https://www.youtube.com/watch?v=eNF3X3D0cH4&list=PLKkN4aWr9O7Ev2dbxR6Qc-DxsFqFrG0Vr)
* [Original driver source](https://github.com/neeraj95575/Temperature-sensor-connect-to-raspberry-pi-pico/tree/main)
