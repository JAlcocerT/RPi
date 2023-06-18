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

```sh
sudo apt update &&
sudo apt full-upgrade
```

Now restart Raspberry Pi by using:

```sh
sudo shutdown - r now
```

{{< /expandable >}}

Or try:

{{< expandable label="Option 2" level="2" >}}

```sh
sudo apt update && sudo apt upgrade -y \
sudo apt install rpi-eeprom rpi-eeprom-images
```

Install rpi-eeprom:

```sh
sudo apt install rpi-eeprom rpi-eeprom-images
```

Update the Firmware:

```sh
sudo rpi-eeprom-update -a
```


{{< /expandable >}}

Check the linux kernel version:

{{< cmd >}}hostnamectl{{< /cmd >}}
