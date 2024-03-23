---
title: Battle of the Boards - Raspberry Pi 4 vs. Orange Pi 5
author: JAlcocerT
date: 2023-05-02 14:10:00 +0800
categories: [RPi Setup]
tags: [RPi 101]
render_with_liquid: false
image:
  path: /img/Orange-vs-Pi/Blog-Orange_vs_Rasp.png
  lqip: data:image/webp;base64,UklGRpoAAABXRUJQVlA4WAoAAAAQAAAADwAABwAAQUxQSDIAAAARL0AmbZurmr57yyIiqE8oiG0bejIYEQTgqiDA9vqnsUSI6H+oAERp2HZ65qP/VIAWAFZQOCBCAAAA8AEAnQEqEAAIAAVAfCWkAALp8sF8rgRgAP7o9FDvMCkMde9PK7euH5M1m6VWoDXf2FkP3BqV0ZYbO6NA/VFIAAAA
  alt: Performance comparison of SBCs -  Raspberry Pi 4 versus Orange Pi 5..
---


The Orange Pi 5 is a versatile device suitable for high-end tablets, Home Assistant integration, edge computing, AI, cloud computing, AR/VR, and smart security. It caters to various AIoT industries and offers flexibility for different use cases. With its advanced 8nm LP fabrication technology and the Rockchip RK3588S chip, it provides exceptional performance and reduced power consumption.

On the other hand, the **Raspberry Pi 4** supports multimedia playback and video output, making it ideal for home media centers and retro gaming. It is also suitable for IoT projects, offers educational opportunities, and is compatible with various sensors and actuators. The Raspberry Pi 4 is a popular choice for academic projects and provides hands-on learning in programming, electronics, and computer concepts.

## The contender: Orange Pi 5

In my recent journey towards self-hosting, I discovered the Orange Pi 5, a powerful single-board computer that has become an invaluable asset in my quest for independence from cloud services, like [Google Cloud Run](https://fossengineer.com/dash-docker-gcr/).

Migrating from Google Cloud Run to [self-hosting the Python DASH APP](https://fossengineer.com/selfhosting-python-dash-apps-with-docker/) that allows any user to [plan trips according to weather patterns](https://fossengineer.com/tags/trip-planner/), has been an empowering experience [*as I also learnt how to expose the services securely with Cloudflare Tunnels*](https://fossengineer.com/selfhosting-python-dash-apps-with-docker/), and the Orange Pi 5 has played a significant role in this transition. 

Its reliability and energy efficiency make it ideal for running my self-hosted services, offering a reliable and cost-effective alternative to cloud-based solutions.

* Rockchip RK3588S that features eight Arm Cores (4xCortex-A76 @ 2.4GHz plus 4x1.8GHz Cortex-A55).
    * The Rockchip SoC also features a Mali G510 MP4 graphics processor, which has open-source driver hope via the Panfrost driver stack - providing solid graphics processing capabilities.

### Orange Pi 5 - CPU Benchmark

The CPU benchmark (8 threads) provided: ~13.4k events/s

![Orange Pi 5 - CPU Benchmark 8 threads](/img/Orange-vs-Pi/orange-benchmark-8.JPG)
_Orange Pi 5 - CPU Benchmark 8 threads_


And to have kneck to kneck comparison - I tried with 4 threads with the Orange Pi 5: ~10.2k events/s
![Orange Pi 5 - CPU Benchmark 4 threads](/img/Orange-vs-Pi/orange-benchmark-4.JPG)
_Orange Pi 5 - CPU Benchmark 4 threads_

<!-- 
I used it for a couple of dash.. -->

<!-- ## small disip

~10 min to cooldown  44
~2min 86.853



### no disp
~10 min to cooldown  44
~2min 87  53

### disip
max 85 
-->


## The Raspberry Pi 4

* The Raspberry Pi 4 is powered by a quad-core ARM Cortex-A72 CPU, providing reliable performance for a range of applications.
    * The Raspberry Pi 4 is equipped with a VideoCore VI GPU, ensuring smooth graphics rendering and multimedia performance.

### Raspberry Pi 4 - CPU Benchmark

The CPU benchmark (4 threads) provided: ~11.3k events/s

![RPi 4 - CPU Benchmark](/img/Orange-vs-Pi/raspberry-bench-4.JPG)
_RPi 4 - CPU Benchmark_

<!-- ## Summary: Hardware versus Software Support & I/O
 -->

## Orange Pi vs Raspberry - Real CPU Test

Recently, I have been working on my [Python Trip Planner with Weather](https://fossengineer.com/tags/trip-planner/) to have an open source tool that allows anyone to look for historical weather patterns with an interactive UI, so that [planning our next adventures](https://fossengineer.com/tags/cyclingthrougheurope/) can be easier.

This provided me with the **perfect opportunity to test the CPU performance** of both, Raspberry Pi 4 and Orange Pi 5 in a real scenario - [building the docker containers](https://fossengineer.com/building-docker-container-images/#building-images-locally-x86-arm32-arm64) for that Python App.

To check how both SBC's were keeping up with the temperatures and how the CPUs struggled, I used [netdata](https://fossengineer.com/selfhosting-server-monitoring-with-netdata-and-docker/).


<!-- DOCKER_BUILDKIT=1 docker build --no-cache --progress=plain --cpuset-cpus 0,1,2 -t trip_planner . 2>&1 | tee docker_build.log -->


### Benchmarking the Docker Build Process

And here we have the results. The Raspberry Pi 4 (2GB ARM32) took ~ 3672s


![RPi 4 - CPU usage during Docker Build](/img/Orange-vs-Pi/rpi_docker_build_cpu.PNG)
_RPi 4 - CPU usage during Docker Build_

*The CPU use was ~25%, that's 1/4 cores that were used during the build process*

And the Orange Pi 5 (8GB) ~ 1777s

![Orange Pi 5 - CPU usage during Docker Build](/img/Orange-vs-Pi/orange_docker_build_cpu.PNG)
_Orange Pi 5 - CPU usage during Docker Build_

*As you can see here, the CPU use was ~13%, that's 1/8 cores that were used during the build process*.

This gives a clear result: the **Orange Pi 5 is x2 faster per CPU core than the Raspberry Pi 4**. *At least for Docker Builds*.

### Benchmarking Temperature during Docker Build Process

That's great, but how where their temperature doing? Again, Netdata has something to show us:

* The Raspberry Pi 4 had a peak of ~46C and was bouncing around ~39C:

![RPi 4 - Temperature during Docker Build](/img/Orange-vs-Pi/rpi_docker_build.PNG)
_RPi 4 - Temperature during Docker Build_

* The Orange Pi 5 had a peak of ~65C and was around 50C when using the 13% of CPU:

![Orange Pi 5 - Temperature during Docker Build](/img/Orange-vs-Pi/orange_docker_build.JPG)
_Orange Pi 5 - Temperature during Docker Build_

---

## FAQ 

### How to Run the Synthetic Benchmarks?

```sh
sudo apt install sysbench
sysbench cpu --threads=8 run #https://github.com/akopytov/sysbench#general-command-line-options
```
<!-- 
sysbench --test=cpu --cpu-max-prime=1000 -threads=4 run -->

### How to Stress the CPU?

```sh
apt install s-tui stress
s-tui
```

* How to check the number of cores?

```sh
nproc
```

* How to check the CPU information?

```sh
lscpu
```

or with:

```sh
cat /proc/cpuinfo
```

### Tweaking the Orange Pi 5

#### Installing Updates

```sh
sudo apt update &&
sudo apt upgrade
```

```sh
orangepi-config
```

```sh
sudo fdisk -l
```

```sh
ip r
```

```sh
sudo apt-get install openssh-client
```

#### GPU Acceleration - Armbian and Orange Pi 5

The [Armbian project](https://www.armbian.com/orangepi-5/) recently added GPU acceleration support for the Orange Pi 5:

To enable it, we can benefit of the great contribution of *liujianfeng1994*:

```sh
sudo add-apt-repository ppa:liujianfeng1994/panfork-mesa
sudo add-apt-repository ppa:liujianfeng1994/rockchip-multimedia
sudo apt update
sudo apt dist-upgrade
sudo apt install mali-g610-firmware rockchip-multimedia-config
```

#### Testing GPU in the Orange Pi 5

```sh
chrome://gpu
```

Also we can test it with: <https://www.wirple.com/bmark/>


```sh
apt install mesa-utils
glxgears
```

#### Fixing no space left on device with ARMBIAN

<!-- ```sh
/var/log
``` -->

you can check with

```sh
df -h
```

and you will see that there is something wrong at /var/log... 

Then, we can remove the 5 oldest:

```sh
ls -rt /var/log/sysstat/sa* | head -5 | sudo xargs rm
```

See with this command that they are actually out: 

```sh
sudo du -sh /var/log/sysstat | sort -hr
```


#### Using NVMe with the Orange Pi 5

* Check that the NMVe disk is recognized:

```sh
sudo fdisk -l | grep "nvme0n1"
```

* Use GParted to format the new disk: ext4 would do the trick

* Balena Etcher: 1st step
    * Copy uboot to orangepi mem: flash from file
        * Source: /usr/lib/linux-u-boot-legacy-orangepi5_1.1.4_arm64/rkspi_loader.img
        * Target: the flash memory -> /dev/mtdblock0

* Balena Etcher: 2nd step and optional
    * Clone drive: from your sd card, to the ssd if you want to keep everything as it is
        * Source: /dev/mmcblk1
        * Target: /dev/nvme0n1


<!-- ## X86

Video 4600g

i7

### Performance



https://cpu.userbenchmark.com/Compare/Intel-Core-i7-1185G7-vs-AMD-Ryzen-5-4600G/m1268967vsm1344633 

### CPU Consumption

The orange idles ~2W


### Build Consumption




### Netdata

## ARM32

## ARM64         -->