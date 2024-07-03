---
title: PI's vs MiniPC for Home Server
author: JAlcocerT
date: 2024-03-15 00:34:00 +0800
categories: [RPi Setup, Home Server]
tags: [Self-Hosting, Docker]
---

Let's compare some popular SBC Boards (RPi4 and [Orange Pi 5](https://jalcocert.github.io/RPi/posts/pi-vs-orange/)) with a MiniPC

> Should I buy a Raspberry or a MiniPC? Lets have a look 👇

## PI's

Some time ago I was making a [performance comparison between 2 popular ARM boards](https://jalcocert.github.io/RPi/posts/pi-vs-orange/).

Now, it is the time to see how these SBC's stand when compared with a **similar in cost mini-PC**.

* For benchmarking I've used:
  * Real Scenario: Docker Building Image time for [my Python Trip Planner](https://github.com/JAlcocerT/Py_Trip_Planner/):
  * Synthetic tests
    * Sysbench
    * Phoronix
  * Netdata

> The Orange Pi (8gb) idles ~ and the RPi 4 (2gb) ~

## The Mini PC - BMAX B4

* Intel N95 (4 cores)
* 16GB RAM 2600mhz
* Dimensions - 12.5 cm (W) × 11.2 cm (L) × 4.4 cm (H) - **0,62L**

```sh
lscpu
```

To connect via ssh I needed:

```sh
sudo apt update
sudo apt install openssh-server
sudo ufw allow ssh

#ssh username@<local_minipc_server_ip>
```


```sh
sudo apt install sysbench 
sysbench cpu --threads=4 run #https://github.com/akopytov/sysbench#general-command-line-options
```


![BMAX B4 - Sysbench Test](/img/minipc-vs-pis/sysbench_bmaxb4.png)
_BMAX B4 - Sysbench Test_


> The BMAX idles around ~9w with Lubuntu 22.4 LTS and the max I observed so far is ~16W. Wifi/Bluetooh and an additional sata ssd included.


```sh
git clone https://github.com/JAlcocerT/Py_Trip_Planner/
docker build -t pytripplanner .
```

It took ~45 seconds for the N95 - Instead of 3600s and 1700s.


![BMAX B4 - Docker Build Test](/img/minipc-vs-pis/buildingtest.png)
_BMAX B4 - Docker Build Test_

And a max Temp of 64C:

![BMAX B4 - Temperature during Docker Build](/img/minipc-vs-pis/temperature_during_test.png)
_BMAX B4 - Temperature during Docker Build_

And these are the temperatures [registered by NetData](https://fossengineer.com/selfhosting-netdata/)

### BMAX B4 vs Orange Pi 5

Comparing N95 (x86) with the Rockchip RK3588S (ARM64).

#### Temperatures

```sh
sudo stress --cpu  8 --timeout 120
```

* Orange Pi 5 - 80C & 8w peak power (no fan enabled) and it quickly goes back to the ~45C after the test
* BMax B4 (N95, fan enabled that goes to full speed) - 66C and 15W peak power


#### Phoronix

For Synthetic benchmarks I have used [phoronix](#how-to-benchmark-with-phoronix-test-suite):

![BMAX B4 - Temperature during Docker Build](/img/minipc-vs-pis/n95-cpu-phoronix.png)
_Intel N95 4 cores with phoronix Open Source Benchmark_

![BMAX B4 - Temperature during Docker Build](/img/minipc-vs-pis/orangepi5-cpu-phoronix.png)
_The Orange Pi 8 Cores is a beast scoring 38s_

For reference, I [benchmarked *bigger* CPUs here](https://jalcocert.github.io/Linux/docs/linux__cloud/benchmark/).

> Plot twist, both CPUs, *specially the Rockchip*, has nothing to envy

![BMAX B4 - Performance vs i5 gen 11](/img/minipc-vs-pis/i5-1135g7.png)
_Performance of i51135g7 (Laptop CPU) with same Benchmark_

---

## FAQ

* Now you can have a *[DB Less Cloud](https://fossengineer.com/selfhosting-filebrowser-docker/)*

<details>
  <summary>Click to expand</summary>
  <p>This is the content that was hidden, but now you see it!</p>
</details>

* Get the latest Kernel for the orange pi 5 - https://github.com/Joshua-Riek/ubuntu-rockchip/releases

### Why changing the MiniPC to Linux?

In this case, the BMAX B4 came with W11 fully activated by default - which for the price I would say its a pretty good deal.

I tried it and it moved daily tasks fluently, but the task manager was showing quite high CPU loads the next day (just installed docker with couple containers).

That's why I decided to switch to [a lighter Linux Distribution](https://jalcocert.github.io/Linux/docs/#what-is-the-best-linux-for-low-resources) - Lubuntu starts at ~800mb RAM, instead of the 2.8GB of W11.

> The max consumption registered was ~15w in this case

#### How to Disable Wifi/Bluetooh

To further lower the consumption, you can disable wifi with:

```sh
nmcli radio wifi off #on
#nmcli radio help   
```

> Here you **improve by ~10%** the power efficiency, aka: -1W 😜

And also, turnoff Bluetooth if you dont need it with:

```sh
sudo service bluetooth stop #start
#service bluetooth status
```


### Projects for a MiniPC

* MiniPC as a Free Home Cloud
  * <https://fossengineer.com/selfhosting-filebrowser-docker/>
  * <https://jalcocert.github.io/RPi/posts/selfhosting-with-docker/>


### How to use LLMs in a MiniPC

We can use [Ollama together with Docker](https://fossengineer.com/selfhosting-llms-ollama/) and try one of the small models with the CPU.

```sh
docker run -d --name ollama -p 11434:11434 -v ollama_data:/root/.ollama ollama/ollama
#docker exec -it ollama ollama --version #I had 0.1.29

docker exec -it ollama /bin/bash
ollama run gemma:2b
```

![BMAX B4 - Trying LLMs with a MiniPC](/img/minipc-vs-pis/minipc-gemma2b.png)
_BMAX B4 - Trying LLMs with a MiniPC_

The system was using 12/16GB (im running couple other containers) and the replies with Gemma 2B Model were pretty fast.


You can see how for the python question, which answer was pretty detailed, took ~30s and a max Temp of ~70C (fan full speed).

![BMAX B4 - MiniPC Performance while LLM inference](/img/minipc-vs-pis/minipc_gemma_temps.png)
_BMAX B4 - MiniPC Performance while LLM inference_


### How to Benchmark the MiniPC?

* Using Sysbench
* [Monitor with Netdata](https://fossengineer.com/selfhosting-netdata/)
* https://github.com/WebKit/Speedometer - Speedometer 3.0 for Browser Benchmark
* With Phoronix Test Suite

#### Benchmark MiniPC with Phoronix Test Suite

We can have an idea by being part of [openbenchmarking](https://openbenchmarking.org/) by using the [F/OSS Phoronix Test Suite](https://github.com/phoronix-test-suite/phoronix-test-suite/releases)

```sh
wget https://github.com/phoronix-test-suite/phoronix-test-suite/releases/download/v10.8.4/phoronix-test-suite_10.8.4_all.deb
sudo dpkg -i phoronix-test-suite_10.8.4_all.deb
sudo apt-get install -f
```

Then, just use:

```sh
phoronix-test-suite benchmark smallpt
#phoronix-test-suite system-info
```
<!-- 
https://openbenchmarking.org/result/2403181-NE-TESTBENCH60
https://openbenchmarking.org/result/2403181-NE-TESTORANG02 -->

<!-- ### How to Monitor MiniPC Temperatures
https://www.youtube.com/watch?v=h1kyncK--vQ
-->

<!-- {% include embed/{youtube}.html id='{h1kyncK--vQ}' %} -->
