I wrote about the PicoW and these scrips [here](https://jalcocert.github.io/JAlcocerT/pico-w/)

---

Connecting the RPi to a [RPi Pico W](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html#pico-1-family):

```sh
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

## Projects

* https://projects.raspberrypi.org/en/projects/introduction-to-the-pico/12