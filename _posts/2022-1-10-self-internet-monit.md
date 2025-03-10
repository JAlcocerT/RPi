---
title: RPi Monitoring - Quality of our Internet
author: JAlcocerT
date: 2022-11-10 14:10:00 +0800
categories: [Make your Raspberry Useful, Networking]
tags: [Self-Hosting,Docker,Networking]
render_with_liquid: false
---

Some services that we can use in our Raspberry Pi's (or any computer) to **monitor our internet Status and Speed**.

> Lan Monitoring Tools with [docker **compose** config files](https://github.com/JAlcocerT/Docker/tree/main/Security/Lan_Monitoring) and [here](https://github.com/JAlcocerT/Docker/tree/main/IoT/InternetQuality)
{: .prompt-info }


## WhatchYourLan

```yml
---
version: "3"
services:
  wyl:
    image: aceberg/watchyourlan
    container_name: watchyourlan	
    network_mode: "host"        
    restart: unless-stopped
    volumes:
    - /home/your_user/Docker/watchyourlan/wyl:/data
    environment:
      TZ: Europe/Paris              # required: needs your TZ for correct time
      IFACE: "eth0"                     # required: 1 or more interface, use the command 'ip link conf' and use the second entry
      DBPATH: "/data/db.sqlite"         # optional, default: /data/db.sqlite
      GUIIP: "0.0.0.0"                  # optional, default: localhost
      GUIPORT: "8840"                   # optional, default: 8840
      TIMEOUT: "120"                    # optional, time in seconds, default: 60
      SHOUTRRR_URL: ""                  # optional, set url to notify
      THEME: "darkly"                   # optional
```

## OpenSpeedTest

```yml
version: '3'
services:
  openspeedtest:
    image: openspeedtest/latest
    container_name: openspeedtest
    ports:
      - "6040:3000"
      - "6041:3001"
    restart: unless-stopped
```

>  Remember to have Docker installed and use Portainer or to apply:
```sh
docker-compose up -d
```
{: .prompt-info }

## SpeedTest Tracker

A self-hosted [internet performance tracking](https://github.com/alexjustesen/speedtest-tracker) application that runs speedtest checks against Ookla's Speedtest service.


```yml
version: '3.3'
services:
    speedtest-tracker:
        container_name: speedtest-tracker
        ports:
            - '8080:80'
            - '8443:443'
        environment:
            - PUID=1000
            - PGID=1000
        volumes:
            - '/path/to/directory:/config'
        image: 'ghcr.io/alexjustesen/speedtest-tracker:latest'
        restart: unless-stopped
```