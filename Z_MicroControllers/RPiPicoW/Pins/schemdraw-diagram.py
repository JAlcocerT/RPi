"""
Wiring diagrams for Pico W sensor connections.
Generates SVG files for DHT22 and MLX90614.

Run:
    uv run schemdraw-diagram.py
"""

import schemdraw
import schemdraw.elements as elm
from schemdraw.elements import IcPin


# ─────────────────────────────────────────────
# Diagram 1: Pico W + DHT22
# ─────────────────────────────────────────────
with schemdraw.Drawing() as d:
    d.config(unit=3, fontsize=12)

    pico = d.add(elm.Ic(
        pins=[
            IcPin(name='VCC',  side='right', pin='36'),
            IcPin(name='GP15', side='right', pin='20'),
            IcPin(name='GND',  side='right', pin='38'),
        ],
        edgepadW=1.5, edgepadH=0.5, pinspacing=2, lblsize=12,
    ).label('Raspberry Pi\nPico W', loc='center'))

    dht = d.add(elm.Ic(
        pins=[
            IcPin(name='VCC',  side='left', pin='1'),
            IcPin(name='DATA', side='left', pin='2'),
            IcPin(name='GND',  side='left', pin='4'),
        ],
        edgepadW=1.2, edgepadH=0.5, pinspacing=2, lblsize=12,
    ).label('DHT22', loc='center').at((10, 0)))

    # VCC → VCC  (red)
    d.add(elm.Line().right().at(pico.pVCC).tox(dht.pVCC).color('red').label('3.3V', loc='top'))

    # GP15 → DATA  (blue)
    d.add(elm.Line().right().at(pico.pGP15).tox(dht.pDATA).color('blue').label('DATA', loc='top'))

    # GND → GND  (black)
    d.add(elm.Line().right().at(pico.pGND).tox(dht.pGND).color('black').label('GND', loc='top'))

    d.save('dht22-wiring.svg')
    print("Saved dht22-wiring.svg")


# ─────────────────────────────────────────────
# Diagram 2: Pico W + MLX90614
# ─────────────────────────────────────────────
with schemdraw.Drawing() as d:
    d.config(unit=3, fontsize=12)

    pico = d.add(elm.Ic(
        pins=[
            IcPin(name='VCC', side='right', pin='36'),
            IcPin(name='SDA', side='right', pin='11'),
            IcPin(name='SCL', side='right', pin='12'),
            IcPin(name='GND', side='right', pin='38'),
        ],
        edgepadW=1.5, edgepadH=0.5, pinspacing=2, lblsize=12,
    ).label('Raspberry Pi\nPico W', loc='center'))

    mlx = d.add(elm.Ic(
        pins=[
            IcPin(name='VCC', side='left', pin='1'),
            IcPin(name='SDA', side='left', pin='2'),
            IcPin(name='SCL', side='left', pin='3'),
            IcPin(name='GND', side='left', pin='4'),
        ],
        edgepadW=1.2, edgepadH=0.5, pinspacing=2, lblsize=12,
    ).label('MLX90614', loc='center').at((10, 0)))

    # VCC → VCC  (red)
    d.add(elm.Line().right().at(pico.pVCC).tox(mlx.pVCC).color('red').label('3.3V', loc='top'))

    # SDA → SDA  (blue)
    d.add(elm.Line().right().at(pico.pSDA).tox(mlx.pSDA).color('blue').label('SDA / GP8', loc='top'))

    # SCL → SCL  (green)
    d.add(elm.Line().right().at(pico.pSCL).tox(mlx.pSCL).color('green').label('SCL / GP9', loc='top'))

    # GND → GND  (black)
    d.add(elm.Line().right().at(pico.pGND).tox(mlx.pGND).color('black').label('GND', loc='top'))

    d.save('mlx90614-wiring.svg')
    print("Saved mlx90614-wiring.svg")
