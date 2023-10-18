---
title: Better Home Internet with PiHole, RaspAlert, Unbound and SearXNG
author: JAlcocerT
date: 2022-12-20 14:10:00 +0800
categories: [Networking]
tags: [Self-Hosting,Docker,Networking]
render_with_liquid: false
---

The good thing about Single Board Computers like the Raspberry, is that additionally to our Iot Projects we can learn about networking as well.

The benefit of this? We can have a better and safer home internet. Let's have a look which free and open source services can help us.

## Pi-Hole

Pi-hole is a network-wide ad blocker that acts as a DNS sink. This means that it intercepts DNS queries from all devices on your network and blocks any queries to known ad-serving domains. Pi-hole can [block ads on all devices on your network](https://fossengineer.com/selfhosting-PiHole-docker/), including computers, smartphones, tablets, smart TVs, and even gaming consoles.


```yml
### https://hub.docker.com/r/pihole/pihole


version: "3"
services:
  pihole:
    container_name: pihole
    image: pihole/pihole:latest
    ports:
      - 53:53/tcp
      - 53:53/udp
      - 67:67/udp
      - 86:80/tcp
      - 446:443/tcp
    environment:
      TZ: Europe/Madrid
      WEBPASSWORD: password_change_me #recommended
    # Volumes store your data between container upgrades
    volumes:
      - ~/Docker/pihole/:/etc/pihole/
      - ~/Docker/pihole/etc-dnsmasq.d/:/etc/dnsmasq.d/
    # Recommended but not required (DHCP needs NET_ADMIN)
    cap_add:
      - NET_ADMIN
    restart: unless-stopped
```



## Pi-Alert

A project that offers us a  WIFI / LAN intruder detector. Check the devices connected and alert you with unknown devices. It also warns of the disconnection of "always connected" devices

```yml
version: "3.7"

services:
  pialert:
    image: jokobsk/pi.alert
    container_name: pialert
    ports:
      - "80:80"
    volumes:
      - "./config:/etc/pi.alert"
      - "./database:/var/lib/pi.alert"
      - "./logs:/var/log/pi.alert"

networks:
  pialert_net:
    name: pialert_net

depends_on:
  pialert:
    - pialert_scanner
```

You can customize the Pi.Alert configuration by editing the files in the ./config directory. For more information on how to configure Pi.Alert, please see the Pi.Alert documentation: <https://github.com/pucherot/Pi.Alert>.

## Unbound DNS


We can also use Unbound as an alternative DNS with this [docker-compose](https://github.com/JAlcocerT/Docker/blob/main/Security/unbound_docker-compose.yml):

```yml
version: "3.7"

services:
  unbound:
    image: unbound:latest
    container_name: unbound
    ports:
      - "53:53"

networks:
  unbound_net:
    name: unbound_net

depends_on:
  unbound:
    - pialert_scanner

```

You can customize the unbound DNS configuration by editing the unbound.conf file in the unbound DNS container.

If you are using unbound DNS as your DNS server, you may need to flush the DNS cache on your devices. You can do this by running the following command on your devices:

```sh
dscacheutil -flushcache
```


## SearXNG

The [SearXNG project](https://github.com/searxng/searxng) is developing and maintaining a self-hosted **metasearch engine**. This means that anyone can install and run their own Searx instance, and **customize it** to their liking. 

You can spin it with this simple docker-compose:

```yml

version: "3.7"

services:
  searxng:
    image: searxng/searxng
    container_name: searxng
    ports:
      #- "${PORT}:8080"
      - "3003:8080"
    volumes:
      #- "${PWD}/searxng:/etc/searxng"
      - "/home/Docker/searxng:/etc/searxng"
    environment:
      #- BASE_URL=http://localhost:$PORT/
      - BASE_URL=http://localhost:3003/
      - INSTANCE_NAME=my-instance
```