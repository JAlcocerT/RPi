---
title: RPi IoT Project - GPS Data (VK-162) with Apache Superset
author: JAlcocerT
date: 2024-12-11 00:10:00 +0800
categories: [IoT & Data Analytics]
tags: [Sensors,Python,MongoDB]
image:
  path: /img/superset.png
  alt: IoT Project with Python, MongoDB, DHT11/22 sensors and Metabase.
render_with_liquid: false
---

* <https://www.youtube.com/watch?v=Z7cJ59sixpk&t=197s>
<https://www.youtube.com/watch?v=3ysOqliO6F8>

## ToDo list

- [ ] Job Done!
  + [ ] Setup BI - Superset
  + [ ] Hardware Checks
  + [ ] Connecting everything

<https://www.youtube.com/watch?v=Z7cJ59sixpk>

## Apache Superset Setup

Apache Superset is a [Free BI Web Tool](https://superset.apache.org/docs/intro/) that we can [use with our RPi projects locally](https://superset.apache.org/docs/installation/installing-superset-using-docker-compose/).


```sh
git clone https://github.com/apache/superset.git
cd superset

docker compose -f docker-compose-non-dev.yml up -d

#git checkout 3.0.0
#TAG=3.0.0 docker compose -f docker-compose-non-dev.yml up
```

Then, just use Superset with its UI at: **http://localhost:8088/login/**

![Desktop View](/img/superset-working.png){: width="972" height="589" }
_DHT22 connection to a Raspberry Pi 4_

*Default credentials are: admin/admin*

- [ ] Job Done!
  + [x] Setup BI - Superset
  + [ ] Hardware Checks
  + [ ] Connecting everything


## Sensors

* VK-162
* Columbus V-800 + [gpsd-gps](https://gpsd.io/) client
* BY-353 USB GPS

* GPS GNSS GPS MTK3333 adafruit 4279
* https://www.reddit.com/r/robotics/comments/18jgsmr/rtk_gps_lap_timing/
* https://www.reddit.com/r/UAVmapping/comments/10utv7b/cheapest_way_to_get_cmlevel_gps/
* ublox f9p

* Neo 6M GPS Sensor
  * https://www.youtube.com/watch?v=N8fH0nc9v9Q

## Comercial Sensors

* mychron 5s gos
& mylaps transponders
* tag heuer transponders

* https://www.reddit.com/r/rccars/comments/15iukhz/made_my_own_lap_timer_that_reads_mylaps/

## Software

https://github.com/GPSBabel/gpsbabel

---

## FAQ

### Apache SuperSet with Portainer

This is the [Stack to deploy Superset] with Docker.



### Apache Supserset DS's and API

* Data Sources: <https://superset.apache.org/docs/databases/db-connection-ui>
* API info: <https://superset.apache.org/docs/api>

### PhyPhox

* You can also save GPS data thanks to the [F/OSS PhyPhox](https://github.com/phyphox/phyphox-android) - An app that allow us to use phone's sensors for physics experiments:
  * Also available for [ESP32 with micropython](https://github.com/phyphox/phyphox-micropython)
  * And [also for Arduino](https://github.com/phyphox/phyphox-arduino)