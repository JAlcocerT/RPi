---
title: "Raspberry Pi OS: Common Steps with Debian"
date: 2022-10-30T23:20:21+01:00
draft: false
tags: ["Setup"] 
---

## [Schedule Crontab Tasks](https://jalcocert.github.io/Linux/debian/ubuntu/securing_linux/#setup-fail2ban)

## [Setup Fail2ban](https://jalcocert.github.io/Linux/debian/ubuntu/securing_linux/#setup-fail2ban)

## [Firewall Setup (UFW)](https://jalcocert.github.io/Linux/debian/ubuntu/securing_linux/#setup-fail2ban)

## Create custom aliases

### Checking the Raspberry Pi's Temperature

Lets edit this file:

{{< cmd >}}nano ~/.bash_aliases{{< /cmd >}}

Add this line to know the RPi’s temperature by typing ‘temp’ on the terminal:

{{< cmd >}}alias temp='/opt/vc/bin/vcgencmd measure_temp' ### TEMP RPi{{< /cmd >}}

Use this command to be able to use the new alias already in the current session

{{< cmd >}}source ~/.bashrc{{< /cmd >}}
