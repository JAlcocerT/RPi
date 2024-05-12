---
title: The Raspberry Pi as a Portable router with RaspAP
author: JAlcocerT
date: 2021-11-25 14:10:00 +0800
categories: [Networking]
tags: [Networking]
render_with_liquid: false
---

Make your **RPi work as a router** that you can trust on your trips while connecting to unknown networks.

There are 2 modalities:

* RPi + RaspAP as Wifi Repeater
  + [x] A Raspberry Pi (Im using a Pi4 2gb, ARM32) with [Raspberry Pi OS installed](https://jalcocert.github.io/RPi/posts/getting-started/#how-to-get-started-with-a-rpi)
  + [x] Ethernet Cable
  + [ ] We will use Ethernet to connect the RPi to Internet and then server an amplified WIfi signal with the built in Wifi  


* RPi + RaspAP as Wifi AP
  + [x] A Raspberry Pi, ofc
  + [ ] A Wifi dongle / usb stick compatible

> And there is also a containerized [(Docker) way to use RaspAP](#raspap-with-docker)

## RaspAP is All You Need

* https://github.com/RaspAP/raspap-webgui

> The [Official docs](https://raspap.com/) are using **RaspOS Lite 32bits**

```sh
cat /etc/os-release #will specify the OS name, example RaspOS `bookworm`
uname -a #kernel check
```

### RaspAP Quick Setup

* https://github.com/RaspAP/raspap-webgui?tab=readme-ov-file#quick-installer

```sh
sudo apt-get update
sudo apt-get full-upgrade
sudo reboot
 
sudo raspi-config #to select your wifi country: localization options -> WLAN country
 
curl -sL https://install.raspap.com | bash
```


The built in wlan0, will be generating our hotspot (by default)

Following a reboot, the wireless AP network will be configured as follows:


```sh
IP address: 10.3.141.1
Username: admin 
Password: secret
DHCP range: 10.3.141.50 — 10.3.141.255
SSID: raspi-webgui
Password: ChangeMe
```

You can check the status of the services with:

```sh
#sudo systemctl status
sudo systemctl status hostapd #allows your Raspberry Pi to act as a wireless access point
sudo systemctl status dnsmasq #provides DNS and DHCP services, including handing out IP addresses to connected clients.

#sudo systemctl status raspap
#sudo systemctl disable raspapd.service

sudo systemctl status lighttpd #web interface running
```

The wireless interface should also be ready:

```sh
ip a
#iwconfig
```

You should be able to **access the Web UI interface** from any local network device at `http://your_rpi_localip`.

![Enable WLan0 RASP-AP](/img/RaspAP-start-wlan0.png){: width="972" height="589" }
_Dont Forget to Enable the WLAN0 to connect to RaspAP_

> Remember, the **default AP WIFI** pass is `ChangeMe`, you can configure it by accessing the UI: `10.3.141.1` when connected to the AP


### RaspAP with Docker

We can also combine [RaspAP with Docker](https://github.com/RaspAP/raspap-webgui?tab=readme-ov-file#docker-support) to make a perfect bundle:

1. Get [Docker and Portainer](https://jalcocert.github.io/Linux/docs/linux__cloud/selfhosting/) UI Ready
2. Run RaspAP as Docker container with: *as per [Official Github](https://github.com/RaspAP/raspap-docker)*

```sh
#sudo systemctl status docker

docker run --name raspap -it -d --privileged --network=host -v /sys/fs/cgroup:/sys/fs/cgroup:ro --cap-add SYS_ADMIN ghcr.io/raspap/raspap-docker:latest
```
> Web GUI should be accessible on `http://localhost` by default

---

## Aknowledgments

* For WIFI AP (WIFI 2 WIFI):
    * https://www.youtube.com/watch?v=3PvDqb66Rw4
    * https://www.youtube.com/watch?v=jlHWnKVpygw&t=1528s

* For WIFI extender mode:
    * https://www.youtube.com/watch?v=nifXL_5MZeM&t=54s
    * https://www.youtube.com/watch?v=Z85ma0xTakE
    * https://www.youtube.com/watch?v=GdNK2p3RhB0

--- 

## FAQ

* The Wifi adapter must be **OpenWRT compatible** (?)

* https://github.com/morrownr/USB-WiFi?tab=readme-ov-file
    * https://github.com/morrownr/USB-WiFi/blob/main/home/AP_Mode/Bridged_Wireless_Access_Point.md

### WIFI Repeaters for RaspAP

* TP-LINK Archer T3U Plus 
* TPLINK: TL-WN821N 
* Edimax EW-7611ULB (Recommended in the docs)


### How to Use a VPN with RaspAP

* OpenVPN
* Wireguard Compatible
* VPN Providers support: Mullvad, NordVPN...


### How to make a RPi Pico W local AP

* https://www.youtube.com/watch?v=cZNoXXIEPbg
* https://shillehtek.com/blogs/news/creating-a-wireless-network-with-raspberry-pi-pico-w-ap-mode-walkthrough-part-1