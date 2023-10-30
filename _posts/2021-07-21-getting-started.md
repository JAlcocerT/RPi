---
title: Getting Started with Raspberry Pi Projects
author: JAlcocerT
date: 2021-07-21 20:55:00 +0800
categories: [RPi Setup]
tags: [RPi 101]
pin: true
#img_path: '/posts/20180809'
image:
  path: /img/RPi-Projects.png
  lqip: data:image/webp;base64,UklGRpoAAABXRUJQVlA4WAoAAAAQAAAADwAABwAAQUxQSDIAAAARL0AmbZurmr57yyIiqE8oiG0bejIYEQTgqiDA9vqnsUSI6H+oAERp2HZ65qP/VIAWAFZQOCBCAAAA8AEAnQEqEAAIAAVAfCWkAALp8sF8rgRgAP7o9FDvMCkMde9PK7euH5M1m6VWoDXf2FkP3BqV0ZYbO6NA/VFIAAAA
  alt: A Raspberry Pi Guide for Everyone.
---

# A journey with the Rpi

 Fuel your curiosity with Raspberry Pi - the single board computer that's redefining the future of technology.

## Why RPi?

The Raspberry Pi is a tiny computer, low power consumption (ARM based) that you can use to learn programming through fun, practical projects and also allow us to have our own server to run 24/7 tasks that don’t require the expensive hardware of a PC.

It can run Linux distributions like: Debian, OpenMediaVault or most commonly Raspbian OS. It can also run Android.

All of the services/projects that we can make the RPi to run, can be easily ported to some cloud service, VPS and so on. So it serves as an entry point to learn also about that as well.

## How to Get Started with a RPi?

First I would recommend you to install Raspbian to the RPi.

Raspbian is based on Debian, a Linux distribution. But you dont have to be worried about this as I have created to onboard anyone to Linux and particularly to [Debian based distros here](https://jalcocert.github.io/Linux/debian/).

Under the **RPi Setup** section on this page, I will be including an extra explanation here where some specifics apply to the RPi.


```sh
$ apt update
$ apt upgrade
```

> There are [other Single Board Computers](https://fossengineer.com/testing-performance-orange-pi5-versus-raspberry-pi4/) out there that you can use to do similar projects.
{: .prompt-info }

## Android in a Raspberry Pi?

### Lineage OS

* Visit: <https://konstakang.com/devices/rpi4/>
* Download the latest version: <https://konstakang.com/devices/rpi4/LineageOS20/>
* Create a bootable SD card with the image and boot it
* Download the MindTheGapps file that matches your Lineage version and reboot into recovery mode, then load that file and Google Play Store will be ready to use.

<!-- 
![img-description](https://pbs.twimg.com/media/FJAFshwXoAEf9HV?format=jpg&name=large)

## Video

{% include embed/youtube.html id='Balreaj8Yqs' %}
 -->