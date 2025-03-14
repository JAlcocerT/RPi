---
title: Getting Started with Raspberry Pi Projects
author: JAlcocerT
date: 2021-07-21 20:55:00 +0800
categories: [RPi Setup, Home Server]
tags: [RPi 101]
pin: true
#img_path: '/posts/20180809'
image:
  path: /img/RPi-Projects.png
  lqip: data:image/webp;base64,UklGRpoAAABXRUJQVlA4WAoAAAAQAAAADwAABwAAQUxQSDIAAAARL0AmbZurmr57yyIiqE8oiG0bejIYEQTgqiDA9vqnsUSI6H+oAERp2HZ65qP/VIAWAFZQOCBCAAAA8AEAnQEqEAAIAAVAfCWkAALp8sF8rgRgAP7o9FDvMCkMde9PK7euH5M1m6VWoDXf2FkP3BqV0ZYbO6NA/VFIAAAA
  alt: A Raspberry Pi Guide for Everyone.
---

**A journey with the Raspberry Pi.**

Fuel your curiosity with Raspberry Pi: *a single board computer that can be our companion to learn a lot of cool stuff*.

## Why RPi?

The Raspberry Pi is a tiny computer, low power consumption (ARM based) that you can use to learn programming, practical IoT projects and also allow us to have our own server to run 24/7 tasks that don’t require the expensive hardware of a PC / server.

It can run Linux distributions like: Debian, OpenMediaVault or *most commonly* Raspbian OS.

It can also run [Android](#android-in-a-raspberry-pi).

All of the services/projects that we can make the RPi to run, can be easily ported to some cloud service, VPS and so on.

> So a Raspberry Pi serves as an entry point to learn also about Cloud/Linux/Docker as well.

And ofc, the IoT: sensors, electronic...with its **great GPIO**.

## How to Get Started with a RPi?

First I would recommend you to install Raspbian to the RPi.

* **Raspbian/Raspberry Pi OS** is based on Debian, a Linux distribution.
* You can also Try [Home Assistant OS](#home-assistant-os), with strong Focus on IoT Home Project, [even Android!](#other-oss)

But you dont have to be worried about this as I have created to onboard anyone to Linux and particularly to [**Debian based** distros here](https://jalcocert.github.io/Linux/docs/debian/).

If you are doing the **RPi Setup**, 99% of that information is applicable to our SBC.

Install Raspbian from any computer with **RPi Imager**:

```sh
apt update
apt upgrade

sudo snap install rpi-imager
```

![rpi-imager](/img/rpi-imager.png)
_Getting the OS ready at the RPi_

Now plug the SD Card to the RPi and make sure to [enable SSH Access](https://jalcocert.github.io/Linux/docs/linux__cloud/selfhosting/) & open the related port 22.

You can **pre-enable SSH Access** by:

1. Open the boot partition of the SD card. This partition should be automatically accessible from any computer, as it is formatted in a standard FAT32 format.

2. In the root (main) directory of the boot partition, create an empty file named `ssh`. Ensure the file has **no file extension** — it should NOT be `ssh.txt` or any other variant.

> There are [other Single Board Computers](https://jalcocert.github.io/RPi/posts/pi-vs-orange/) out there that you can use to do similar projects.
{: .prompt-info }

<!-- How To Use Your Laptop As A Display For Your Raspberry Pi (with OBS + VIDEO CAPTURE KARTA)
https://youtu.be/uO0XtSckHOM -->

### Other OS's

### Android in a Raspberry Pi?

Yes, it is possible to run Android in our SBC.

#### Lineage OS

* Visit: <https://konstakang.com/devices/rpi4/>
  * Download the latest version: <https://konstakang.com/devices/rpi4/LineageOS20/>
  * Create a bootable SD card with the image and boot it
  * Download the **MindTheGapps** file that matches your Lineage version and reboot into recovery mode, then load that file and **Google Play Store** will be ready to use.

### Light OS for Raspberry Pi

* Raspberry Pi OS Lite
* DietPi

### Home Assistant OS

To install HA OS on the Pi:

1. Get ready RPi Imager 
2. Select: Other Speficic Purpose OS -> HA and Home Automation.

Make sure your Pi is connected to ethernet when booting and you will get a local IP with **port 8123** to see the **UI of the installation**

![Desktop View](/img/ha-installation.jpeg){: width="972" height="589" }

>  [Add-ons](https://www.home-assistant.io/addons) are only available with the Home Assistant Operating System.
{: .prompt-info }

After a while, this will be saying Hi to you:

![Desktop View](/img/ha.png){: width="772" height="389" }


You can give **HA a try with Docker** as well.

But you wont see these add-ons with the container image:

![Desktop View](/img/ha-addons.png){: width="772" height="489" }

```sh
ha --help
```

#### Other Home Automations / IoT OS

* [Homebridge](https://github.com/homebridge/docker-homebridge)
* OpenHAB... (you can also install them with Rpi Imager).

You can also use a Pi together with the Cloud: 

* [Google Pub/Sub](https://cloud.google.com/free/docs/free-cloud-features#pub-sub)
* [AWS IoT](https://www.youtube.com/watch?v=hgQ-Ewrm48c)


### Analytical Software for IoT Projects

>  See more aobut [BI Tools](https://jalcocert.github.io/JAlcocerT/setup-bi-tools-docker/)
{: .prompt-info }

| **Tool** | FOSS | Pros | Cons |
|------|------|------|------|
| **Metabase** | Yes | Easy to use for creating dashboards and reports. Strong in data visualization and business intelligence. Supports a wide range of databases | Limited in advanced analytics capabilities. Not as flexible for custom data processing as some other tools |
| **Apache Superset** | Yes | Open-source data visualization and data exploration platform. Supports SQL querying. Customizable and extensible | Requires technical knowledge for setup and customization. May have performance issues with very large datasets |
| **Kibana** | Yes | Part of the Elastic Stack, excellent for visualizing Elasticsearch data. Great for log and time-series analytics. Real-time data visualization | Primarily tailored to Elasticsearch data. Can be complex to configure and optimize. Less versatile for non-Elasticsearch data |

* **Others**: Grafana, Redash, Node-Red, JS ([Epoch](https://epochjs.github.io/epoch/real-time/), [Plotly](https://plotly.com/javascript/streaming/), [chartjs](https://nagix.github.io/chartjs-plugin-streaming/1.9.0/))


### How to BackUP a RPi

There are some cool ideas around:

1. Reddit, like [this](https://www.reddit.com/r/selfhosted/comments/1advwg7/best_way_to_backup_everything_from_raspberry_pi/) and this post

2. https://github.com/UnconnectedBedna/shrink-backup/tree/main

> A utility to backup SBC:s (like Raspberry pi) into minimal bootable img files