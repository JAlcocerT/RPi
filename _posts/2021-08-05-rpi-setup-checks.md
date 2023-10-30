---
title: RPi System Checks
author: JAlcocerT
date: 2021-08-05 14:10:00 +0800
categories: [RPi Setup]
tags: [RPi 101]
render_with_liquid: false
---


A collection of some of the checks that I needed to do regarding Linux and Firmware versions.


## Firmware version


### EEPROM

This command is used to update the Raspberry Pi's bootloader and EEPROM (Electrically Erasable Programmable Read-Only Memory) firmware.

The EEPROM firmware includes the firmware responsible for booting the Raspberry Pi, as well as other critical system functions. It is typically used for updating low-level firmware that is responsible for the initial boot process and hardware initialization.

It's a more focused update for the bootloader and EEPROM and is less likely to introduce compatibility issues with the operating system and software.

* Check firmware version with :

```sh
$sudo rpi-eeprom-update
```
  
* Update it with:

```sh
$sudo rpi-eeprom-update
```

Recommended: 

```sh
#shutdown -r now
reboot -r now
```

### Regular Firmware

This command is used to update the Raspberry Pi's kernel and firmware, which includes device drivers, firmware for peripherals, and other software-related components.

It updates the higher-level software components of the Raspberry Pi's firmware. It can include updates to the Linux kernel and various device drivers, and it may also update userland software packages.

While it can bring new features and improvements, it has a greater potential to introduce compatibility issues with the operating system and software compared to rpi-eeprom-update.

* Check current version:

```sh
vcgencmd version
```

* or alternatively with:


```sh
hostnamectl
```



* Update it with:


```sh
sudo apt install rpi-update
sudo rpi-update
```




## Kernel version


The Linux kernel receives important updates regularly, you can check its version with:


```sh
uname --kernel-release
```

And to update it:

```sh
sudo apt update
#sudo apt full-upgrade
```

## Checking Rpi's Architechture

There are few alternatives:

```sh
dpkg --print-architecture
```

```sh
cat /proc/cpuinfo 
```


```sh
uname -a
```

## Installed Packages

* Check all installed packages with:


```sh
apt list --installed
#apt list --installed 2>/dev/null | grep -i 'py'
```

> Dont forget to **update** all the packages **regularly** with: 
```console
$sudo apt update && sudo apt upgrade
```
{: .prompt-info }




## Configure a VNC server

```sh
$ sudo apt-get install tightvncserver
$ vncserver
```

Remember that VNC default port is 5901.


## Checking the Raspberry Pi’s Temperature

We can do this with one alias.

```sh
$  nano ~/.bash_aliases
```
Add this line to know the RPi’s temperature by typing ‘temp’ on the terminal:



```sh
alias temp='/opt/vc/bin/vcgencmd measure_temp' ### TEMP RPi
```


Use this command to be able to use the new alias already in the current session:

```sh
$ source ~/.bashrc
$ temp
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