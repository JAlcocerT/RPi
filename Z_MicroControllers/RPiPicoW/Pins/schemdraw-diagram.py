import schemdraw.elements as elm
import schemdraw.elements.micro as micro

with schemdraw.Drawing() as d:
    # Set the unit to make the diagram smaller and easier to read
    d.unit = 0.5

    # --- Draw the Components ---

    # Raspberry Pi Pico W - Now imported from the 'micro' module
    pico = micro.RaspberryPiPico(label='Pico W')
    d.add(pico)

    # DHT22 Sensor
    dht22 = elm.Resistor(label='DHT22')
    d.add(dht22)

    # Pull-up Resistor
    R1 = elm.Resistor(label='4.7kΩ Pull-up')

    # --- Draw the Connections ---

    # Ground connection
    gnd_pico = pico.gnd
    gnd_dht = dht22.gnd
    d.add(elm.Line().at(gnd_pico).to(gnd_dht).label('GND'))

    # Power (3.3V) connection
    vcc_pico = pico.vdd
    vcc_dht = dht22.vdd
    d.add(elm.Line().at(vcc_pico).to(vcc_dht).label('3V3'))

    # Data connection with a pull-up resistor
    # This is a bit more complex, drawing multiple lines
    data_pico = pico.gp0
    data_dht = dht22.gnd + [0, 1]  # Placeholder for DHT data pin
    d.add(elm.Line().at(data_pico).to(data_dht, direction='right').label('GPIO_Data'))
    d.add(R1)
    d.add(elm.Line().to(vcc_dht, direction='up').label('Pull-up'))

    # Save the drawing
    d.save('pico_dht22_schematic.svg')