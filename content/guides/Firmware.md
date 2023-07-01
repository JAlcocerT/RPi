---
title: "RPi Firmware Update"
date: 2022-10-30T23:20:21+01:00
draft: false
tags: ["Setup"] 
---

## RPi Firmware Update

Check firmware version with :

{{< cmd >}}sudo rpi-eeprom-update{{< /cmd >}}

{{< expandable label="Option 1" level="2" >}}

{{< cmd >}}
sudo apt update &&
sudo apt full-upgrade
{{< /cmd >}}

Now restart Raspberry Pi by using:

{{< cmd >}}
sudo shutdown - r now
{{< /cmd >}}

{{< /expandable >}}

Or try:

{{< expandable label="Option 2" level="2" >}}

{{< cmd >}}
sudo apt update && sudo apt upgrade -y \
sudo apt install rpi-eeprom rpi-eeprom-images
{{< /cmd >}}

Install rpi-eeprom:

{{< cmd >}}
sudo apt install rpi-eeprom rpi-eeprom-images
{{< /cmd >}}

Update the Firmware:

{{< cmd >}}
sudo rpi-eeprom-update -a
{{< /cmd >}}


{{< /expandable >}}

Check the linux kernel version:

{{< cmd >}}hostnamectl{{< /cmd >}}
