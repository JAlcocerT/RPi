---
title: RPi System Checks
author: JAlcocerT
date: 2021-08-05 14:10:00 +0800
categories: [RPi Setup]
tags: [RPi 101]
render_with_liquid: false
---


A collection of *some of the checks* that I needed to do regarding **Linux and Firmware versions**.

If you just got a **Pi and are new to [Linux](https://jalcocert.github.io/Linux/)**, this can be beneficial to follow.

## Firmware version


### EEPROM

This command is used to update the Raspberry Pi's **bootloader and EEPROM** (Electrically Erasable Programmable Read-Only Memory) firmware.

The **EEPROM firmware** includes the firmware responsible for booting the Raspberry Pi, as well as other critical system functions.

It is typically used for updating **low-level firmware** that is responsible for the initial boot process and hardware initialization.

It's a more focused update for the bootloader and EEPROM and is less likely to introduce compatibility issues with the operating system and software.

1. Check firmware version with :

```sh
sudo rpi-eeprom-update
```
  
2. Update it with:

```sh
sudo rpi-eeprom-update
```

Recommended step:

```sh
#shutdown -r now
reboot -r now
```

### Regular Firmware

This command is used to **update the Raspberry Pi's kernel and firmware**, which includes device drivers, firmware for peripherals, and other software-related components.

It updates the **higher-level** software components of the Raspberry Pi's firmware.

It can include updates to the Linux kernel and various device drivers, and it may also update userland software packages.

While it can bring new features and improvements, it has a greater potential to introduce compatibility issues with the operating system and software compared to rpi-eeprom-update.

* Check current version:

```sh
vcgencmd version
```

* Or alternatively with:

```sh
hostnamectl
```

**Update the firmware** with:

```sh
sudo apt install rpi-update
sudo rpi-update
```

## Kernel version

The Linux kernel receives important updates regularly.

You can check its version with:

```sh
uname --kernel-release
```

And to update the kernel:

```sh
sudo apt update
#sudo apt full-upgrade
```

## Checking Rpi's Architechture

There are few alternatives:

1. Use dpkg:

```sh
dpkg --print-architecture
```

2. Inspect cpuinfo:

```sh
cat /proc/cpuinfo 
```

3. Simply with uname:

```sh
uname -a
```

## Installed Packages

* Check all installed packages with:


```sh
apt list --installed
#apt list --installed 2>/dev/null | grep -i 'py'
```

> Dont forget to **update** all the packages **regularly**! 
{: .prompt-info }

```sh
sudo apt update && sudo apt upgrade
```

---

## Just Getting Started with a Pi

### Configure a VNC server

Use your PI from another computer:

```sh
sudo apt-get install tightvncserver
vncserver
```

Remember that VNC default port is `5901`.

## Observing the Pi

> See these [monitoring Tools](https://jalcocert.github.io/JAlcocerT/how-to-setup-beszel-monitoring/) and [perform such **benchmarks**](https://jalcocert.github.io/JAlcocerT/benchmarking-computers/)
{: .prompt-info }

### Checking the Raspberry Pi’s Temperature

We can do this with one **alias**.

```sh
nano ~/.bash_aliases
```
Add this line to know the **RPi’s temperature** by typing ‘temp’ on the terminal:

```sh
alias temp='/opt/vc/bin/vcgencmd measure_temp' ### TEMP RPi
```

Use this command to be able to use the new alias already in the current session:

```sh
source ~/.bashrc
temp
```

### Checking Performance and Temp - HTOP


A simple, yet useful CLI tool to check how well our RPi is doing:

```sh
apt install -y htop
#htop --v

htop
```

### Stress Test - STUI

```sh
sudo apt install python3-pip
sudo pip install s-tui
#s-tui
```