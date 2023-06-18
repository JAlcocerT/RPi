---
title: "RPi as Portable Router - RaspAP"
date: 2022-10-30T23:20:21+01:00
draft: false
tags: ["Networking"] 
---

Make your RPi work as a router that you can trust on your trips while connecting to unknown networks:


```sh
 sudo apt-get update
 sudo apt-get full-upgrade
 sudo reboot
 
 sudo raspi-config
 
curl -sL https://install.raspap.com | bash
```

Following a reboot, the wireless AP network will be configured as follows:


```sh
IP address: 10.3.141.1
Username: admin 
Password: secret
DHCP range: 10.3.141.50 — 10.3.141.255
SSID: raspi-webgui
Password: ChangeMe
```
