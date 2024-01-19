---
title: Future Projects
author: JAlcocerT
date: 2024-12-12 00:10:00 +0800
categories: [IoT & Data Analytics]
tags: [Sensors]
image:
  path: /img/metabase.png
  alt: IoT Project with Python, MongoDB, DHT11/22 sensors and Metabase.
render_with_liquid: false
---

* <https://www.youtube.com/@proyectosmicropic/videos>

### GPS Tracker

https://www.traccar.org/docker/
https://github.com/traccar/traccar-docker

### ESP32 HA + Batteries

<https://www.youtube.com/watch?v=aR044Dk6c_0>

### ESP32 HA w ESPHome

<https://www.youtube.com/watch?v=pBT5p5XaWNE>

### ESP32 Web

<https://www.youtube.com/watch?v=Ra3iWgOfveQ>

### Pico DHT22



https://www.youtube.com/watch?v=eNF3X3D0cH4

https://github.com/neeraj95575/Temperature-sensor-connect-to-raspberry-pi-pico

### ESP DHT22





GND
VIN (3v3 also works)
D23


<https://registry.platformio.org/libraries/adafruit/DHT%20sensor%20library> ---> <https://github.com/adafruit/DHT-sensor-library>


in platformio.ini

adafruit/DHT sensor library@^1.4.4



lib_deps=
https://github.com/blynkkk/blynk-library.git
https://github.com/adafruit/Adafruit_Sensor
https://github.com/adafruit/DHT-sensor-library



in the main.cpp

#include <DHT.h>

https://github.com/adafruit/DHT-sensor-library

not this one: adafruit/Adafruit Unified Sensor@^1.1.13



lib_deps =
  https://github.com/adafruit/DHT-sensor-library.git

OR

lib_deps =
  adafruit/DHT sensor library@^1.4.4

### MPU acelerometer


There are many 3-axis accelerometers that you can use with the Raspberry Pi Pico. Some of the most popular options include:

MPU-6050: This is a popular and versatile accelerometer that is also compatible with the Raspberry Pi Pico. It has a wide range of features, including a built-in gyroscope.


**biblioman09**

<https://www.youtube.com/watch?v=JXyHuZyqjxU>

### DSB18B20

-55 to 125C

<!-- 
blackc able - gnd
red - 3.3 to 5v
yellow - data -->


data to D13

### Pi off grid - Solar panels

<https://www.reddit.com/r/raspberry_pi/comments/2b0ccl/anyone_running_their_pi_off_of_solar_panels/>

## HA Security camera

Scrypted

## Hardware for HA

https://forocoches.com/foro/showthread.php?t=6655749


* https://forocoches.com/foro/showthread.php?t=7806376
* https://rpi.uroboros.es/docker.html

## SelfHosting 101

With cosmos

```yml
version: '3'
services:
  cosmos-server:
    image: azukaar/cosmos-server:latest
    container_name: cosmos-server
    hostname: cosmos-server
    privileged: true
    restart: always
    ports:
      - "800:80"
      - "4433:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /:/mnt/host
      - /var/lib/cosmos:/config
    networks:
      - default

networks:
  default:

```
