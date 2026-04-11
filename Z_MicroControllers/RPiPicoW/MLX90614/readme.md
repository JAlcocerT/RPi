# MLX90614 — IR Non-Contact Temperature Sensor

Reads object (IR) and ambient temperature from an MLX90614 sensor via I2C and prints to the serial console.

## Wiring

| MLX90614 Pin | Pico W Pin |
|---|---|
| VCC | 3.3V (pin 36) |
| GND | GND (pin 38) |
| SDA | GP8 (pin 11) |
| SCL | GP9 (pin 12) |

> No resistors or level shifters needed — the MLX90614 runs at 3.3V natively.

## Library

Not available via `mip` — install manually:

```sh
git clone https://github.com/mcauser/micropython-mlx90614
```

Copy `mlx90614.py` into `/lib/mlx90614.py` on the Pico W using Thonny's file panel.

## Verify sensor is detected

Run this in the Thonny shell before flashing `main.py`:

```python
from machine import Pin, SoftI2C
i2c = SoftI2C(scl=Pin(9), sda=Pin(8), freq=100000)
print([hex(a) for a in i2c.scan()])  # should print ['0x5a']
```

## Output

```
T1 (ambient) = 23.450000
T2 (object)  = 36.120000
```

## Files

| File | Description |
|------|-------------|
| `main.py` | Reads ambient + object temperature every 500 ms via I2C and prints to console |

## References

* [YouTube walkthrough](https://www.youtube.com/watch?v=FsdSkhdfOqY&t=24s)
* [Driver library](https://github.com/mcauser/micropython-mlx90614)
* [embeddedclub MicroPython examples](https://github.com/embeddedclub/micropython)
