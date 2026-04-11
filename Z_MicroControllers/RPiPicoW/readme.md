I wrote about the PicoW and these scrips:

* [here](https://jalcocert.github.io/JAlcocerT/electronics-101/#quick-iot-samples)
* and [here](https://jalcocert.github.io/JAlcocerT/pico-w/)

---

Connecting the RPi to a [RPi Pico W](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html#pico-1-family):

```sh
#pnputil /enum-devices /class Ports
ls /dev/tty*

sudo apt-get update
sudo apt-get install screen

screen /dev/ttyACM0
```

```sh
Put the Pico W in BOOTSEL, copy the UF2, let it reboot. (press by piW button!)
Paste the output of:
ls -l /dev/serial/by-id; ls -l /dev/ttyACM* 2>/dev/null
```

MicroPython v1.20.0 on 2023-04-26; Raspberry Pi Pico W with RP2040.

> To exit that terminal, press **k**

## Boot Workflow

Every time the Pico W powers on or resets, MicroPython runs these two files in order:

```
Power on / Reset
      │
      ▼
 boot.py          ← runs once at startup
 (connect WiFi,   
  configure hw)   
      │
      ▼
 main.py          ← runs forever (infinite loop)
 (read sensors,
  publish MQTT,
  handle errors)
```

- **`boot.py`** — one-time setup: connect to WiFi, configure hardware. If this fails, `main.py` won't have a network.
- **`main.py`** — the actual application loop. Should always wrap its logic in `while True` and handle exceptions internally so the Pico W never halts.

> If only `main.py` is present (no `boot.py`), it still runs — but any setup that `boot.py` would have done (e.g. WiFi) must be handled inside `main.py` itself.

## Projects

* https://projects.raspberrypi.org/en/projects/introduction-to-the-pico/12