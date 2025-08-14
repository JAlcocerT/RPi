---
title: RPi + MicroCOntrollers
author: JAlcocerT
date: 2024-12-01 00:10:00 +0800
categories: [IoT & Data Analytics]
tags: [Sensors,Python,MongoDB]
image:
  path: /img/metabase.png
  alt: IoT Project with Python, MongoDB, DHT11/22 sensors and Metabase.
render_with_liquid: false
---





## Pico W



## Pico and MQTT

Message Queue Telemetry Transport

### <https://www.youtube.com/watch?v=jw9zTjKqoUA> with **HiveMQ**

### with RPI and mqttx/mosquitto


<https://mqttx.app/>
<https://github.com/emqx/MQTTX>

```sh
sudo apt install -y mosquitto
sudo apt install -y mosquitto-clients

#sudo apt install python3-pip
sudo pip3 install paho-mqtt

sudo systemctl status mosquitto.service
```

In the absence of a direct configuration entry for the port, the port used by Mosquitto could be the default port (1883 for MQTT or 8883 for MQTT over TLS/SSL).

You can check which one is in used with: netstat -tuln


<https://www.youtube.com/watch?v=GQOqvvei5Do> #also hivemq


#without hivemq <https://www.youtube.com/watch?v=THUGLRGuOU8> GREAT VIDEO!!!!!!!! **To be used mqttx and emqx**
<https://www.donskytech.com/umqtt-simple-micropython-tutorial/>



REQUIRED:

```py

#connect to wifi
import network   # handles connecting to WiFi
import urequests # handles making and servicing network requests

# Connect to network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Fill in your network name (ssid) and password here:
ssid = 'HUAWEI P30'
password = 'yourpassword' #adapt this!
wlan.connect(ssid, password)

#install libraries for mqtt

##with upip
#upip.install("micropython-umqtt-robust")
#upip.install("micropython-umqtt-simple")

##with mip
#https://github.com/micropython/micropython-lib 
#https://github.com/micropython/micropython-lib/tree/master/micropython/umqtt.robust
mip.install("umqtt.robust")

#https://github.com/micropython/micropython-lib/tree/master/micropython/umqtt.simple
mip.install("umqtt.simple")

```

then the code <https://github.com/donskytech/micropython-raspberry-pi-pico/tree/main/umqtt.simple>


`boot.py`

```py
# boot.py -- run on boot-up
import network, utime, machine

# Replace the following with your WIFI Credentials
SSID = "HUAWEI P30"
SSID_PASSWORD = "mokradupa68"


def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(SSID, SSID_PASSWORD)
        while not sta_if.isconnected():
            print("Attempting to connect....")
            utime.sleep(1)
    print('Connected! Network config:', sta_if.ifconfig())
    
print("Connecting to your wifi...")
do_connect()
```


main.py


```py
import time
import ubinascii
from umqtt.simple import MQTTClient
import machine
import random

# Default  MQTT_BROKER to connect to
MQTT_BROKER = "192.168.3.200"
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
SUBSCRIBE_TOPIC = b"led"
PUBLISH_TOPIC = b"temperature"

# Setup built in PICO LED as Output
led = machine.Pin("LED",machine.Pin.OUT)

# Publish MQTT messages after every set timeout
last_publish = time.time()
publish_interval = 5

# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    print((topic, msg))
    if msg.decode() == "ON":
        led.value(1)
    else:
        led.value(0)


def reset():
    print("Resetting...")
    time.sleep(5)
    machine.reset()
    
# Generate dummy random temperature readings    
def get_temperature_reading():
    return random.randint(20, 50)


def get_chip_temperature_reading(): #added this function to read the Pico's Temp Sensor
    sensor_temp = machine.ADC(4)
    conversion_factor = 3.3 / (65535) #pico's datasheet
    #while True:
    reading = sensor_temp.read_u16() * conversion_factor
    temperature = 27 - (reading - 0.706)/0.001721
        #print(temperature)
    return(temperature)
   
def main():
    print(f"Begin connection with MQTT Broker :: {MQTT_BROKER}")
    mqttClient = MQTTClient(CLIENT_ID, MQTT_BROKER, keepalive=60)
    mqttClient.set_callback(sub_cb)
    mqttClient.connect()
    mqttClient.subscribe(SUBSCRIBE_TOPIC)
    print(f"Connected to MQTT  Broker :: {MQTT_BROKER}, and waiting for callback function to be called!")
    while True:
            # Non-blocking wait for message
            mqttClient.check_msg()
            global last_publish
            if (time.time() - last_publish) >= publish_interval:
                #temp = get_temperature_reading()
                temp=get_chip_temperature_reading()
                mqttClient.publish(PUBLISH_TOPIC, str(temp).encode())
                last_publish = time.time()
            time.sleep(1)


if __name__ == "__main__":
    while True:
        try:
            main()
        except OSError as e:
            print("Error: " + str(e))
            reset()

```

#### MQTT to NodeRed

NodeRed will subscribe to the topic


```yml
version: '3'

services:
  emqx:
    image: emqx/emqx
    container_name: emqx
    ports:
      - "1883:1883"
      - "8083:8083"
      - "8883:8883"
      - "8084:8084"
      - "18083:18083"
    restart: always

  nodered:
    image: nodered/node-red
    container_name: nodered
    ports:
      - "1880:1880"
    restart: always

```


<https://www.youtube.com/watch?v=_DO2wHI6JWQ&t=21s>
<https://learnembeddedsystems.co.uk/easy-raspberry-pi-iot-server>


###

https://www.youtube.com/watch?v=ybCMXqsQyDw&t=19s


## Pico to Pico Wifi comm

<https://www.youtube.com/watch?v=ACAmVg6MakI>

## Pico W web server

<https://www.youtube.com/watch?v=ufK_knxWn08>

and also <https://www.youtube.com/watch?v=AK8UYh7pMGM>





## Pico W with MLX90614

GND is pin38
3v3 out is pin 36

11 (GP8) is I2C0 SDA
12 (GP9) is I2C0 SCL

<https://www.youtube.com/watch?v=FsdSkhdfOqY&t=24s> and they are giving their own library: <https://github.com/embeddedclub/micropython>

we need to install: <https://github.com/mcauser/micropython-mlx90614>
it is not available in mip, the new package manager

so cloned the repo and copied into /lib/mlx/mlx90614.py (i did not compiled it into .mpy) the .py file of the repo

in this way, we can import with from mlx.mlx90614 import MLX90614 (we import the class)


```py
from machine import Pin, Timer, I2C, SoftI2C
#from aphanum import ALPHANUM_I2C
from mlx90614 import MLX90614_I2C


i2c2 = SoftI2C(scl=Pin(9),sda=Pin(8),freq=100000)

print("I2C Comm Success")

# d = i2c2.scan()
# print(hex(d[0])
# print(hex(d[1])
# alph = ALPHANUM_I2C(i2c2,0x70,000,15)
# print("Alpha display init")

irtemp = MLX90614_I2C(i2c2,0x5A)

led1 = Pin(25, Pin.OUT)

timer1 = Timer()

def tick_timer(timer):
    global led1
    led1.toggle()
    t1 = irtemp.get_temperature(0)
    t2 = irtemp.get_temperature(1)
    print("T1 = %f", t1)
    print("T2 = %f", t2)
    alph.set_digit(int(t2*100),2);
timer1.init(freq=2,mode=Timer.PERIODIC,callback=tick_timer)

```



## Languages

C/C++
MicroPython
TinyGo (?)
CircuitPython (?)

O.S FreeRTS ??? <https://www.youtube.com/watch?v=5pUY7xVE2gU>

## Sensors

### BME280

Temp Hum and Preassure

I2C

<https://www.youtube.com/watch?v=GQOqvvei5Do>

### DHT22 Pico

https://www.youtube.com/watch?v=eNF3X3D0cH4

https://github.com/neeraj95575/Temperature-sensor-connect-to-raspberry-pi-pico


### MPU6050


There are many 3-axis accelerometers that you can use with the Raspberry Pi Pico. Some of the most popular options include:

MPU-6050: This is a popular and versatile accelerometer that is also compatible with the Raspberry Pi Pico. It has a wide range of features, including a built-in gyroscope.


**biblioman09**

<https://www.youtube.com/watch?v=JXyHuZyqjxU>

### KY-008

Laser Transmitter Module Overview

- **Remote Signaling**: Use the laser to send signals to a receiver module for remote controls or presence detection.
- **Line Following**: Implement in robots to follow a laser-drawn path.
- **Distance Measurement**: Measure distances by timing the laser reflection from objects.
- **Obstacle Avoidance**: Detect and navigate around obstacles using the laser.
- **Security Systems**: Set up alarms that trigger if the laser path is interrupted.

### Usage Considerations
- **Safety**: The laser can harm eyes; avoid direct exposure.
- **Environment**: Operate in dim environments to minimize interference from sunlight or other bright lights.
- **Alignment**: Ensure the path of the laser beam is clear of obstructions.
- **Adjustability**: Modify beam intensity using the onboard resistor.

Connecting KY-008 to Raspberry Pi Pico

- **Power Requirements**: KY-008 operates with 5V, compatible with Pico’s 5V output.
- **Connection**:
  - `VCC` on KY-008 to `5V` on Pico
  - `GND` on KY-008 to `GND` on Pico