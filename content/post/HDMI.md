---
title: "Adjust HDMI signal"
date: 2022-10-30T23:20:21+01:00
draft: false
tags: ["Setup"] 
---

While connecting your RPi to some displays, you might get no signal to display the desktop.

Try connecting through SSH or to a smaller display, then:

{{< cmd >}}sudo cp /boot/config.txt /boot/configbackup.txt{{< /cmd >}}

{{< cmd >}}sudo nano /boot/config.txt{{< /cmd >}}


And uncomment: hdmi_force_hotplug=1

Then save the file by pressing: CTRL+O and exit with: CTRL+X

