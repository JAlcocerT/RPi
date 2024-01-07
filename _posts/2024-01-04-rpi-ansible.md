---
title: IoT Projects with Ansible and Raspberry Pi
author: JAlcocerT
date: 2024-01-04 00:34:00 +0800
categories: [IoT & Data Analytics]
tags: [Self-Hosting]
---

So you have a Raspberry Pi and want to get started with IoT Project.

But let me guess, you dont have time to read all the Docs, you just want to connect the wirings and get the Data Flowing.

If that resonates with you, keep reading - I will show you how to **leverage Ansible**, an automation tool to Spin up in few IoT Projects with the RPi.

> Yep, still, you will have to connect the cables 😝
{: .prompt-info }

## Ansible with Raspberry Pi

1. Get Raspbian Installed
2. Install Ansible - Just like you would [in any other Debian](https://jalcocert.github.io/Linux/docs/linux__cloud.md/ansible/#installing-ansible).

```sh
#sudo apt update
#sudo apt upgrade
sudo apt install ansible

#ansible --version
```

3. Clone this Repo

```sh
git clone https://github.com/JAlcocerT/RPi ./RPi
#cd ./RPi/Z_ansible
```

So this is it from the Setup side. Now choose the IoT Project you want to have running and execute just one more command.

## IoT Projects with Ansible

### Mongo Project

> Im Talking about: [Raspberry Pi - DHT to MongoDB](https://jalcocert.github.io/RPi/posts/rpi-iot-dht1122-mongo/)
{: .prompt-info }

So you want to have the project that pulls data from DHT11 or DHT22, sends it from Python to Mongo and then Display it in Metabase?

No issues, just execute:

```sh
ansible-playbook ./RPi/Z_ansible/Ansible_py_dht_mongo_arm32.yml -i inventory.ini #execute Meta Project Playbook
#ansible-playbook ./RPi/Z_ansible/Ansible_py_dht_mongo_arm64.yml -i inventory.ini #execute Meta Project Playbook


#docker-compose -f ./RPi/Z_IoT/DHT-to-MongoDB/Ansible_py_dht_mongo_arm64.yml up -d # Basically it spins up Docker and This Stack
```

You can always get inside the created containers with:

```sh
docker exec -it mongodb sh
docker exec -it dht_sensor_mongo sh
```


> Working for me on [RaspiOS Bullseye](https://downloads.raspberrypi.com/raspios_armhf/images/raspios_armhf-2023-05-03/), not in Bookworm due to Adafruit not detecting the platform properly.
{: .prompt-info }


### Influx Project

```sh
ansible-playbook ./RPi/Z_ansible/Ansible_py_dht_influx_grafana.yml -i inventory.ini #execute Influx Project Playbook
```

> This is the one: [Raspberry Pi - DHT to InfluxDB](https://jalcocert.github.io/RPi/posts/rpi-iot-dht11-influxdb/)
{: .prompt-info }


## FAQ

### Containers? What's that?

Container are a way to encapsule all Software Project dependencies.

For example to encapsule: MongoDB, Influx or the Python Script with all the libraries installed at a specified version.

To run containers, Ansible is actually using Docker.

You can check the installed versions with:

```sh
docker --version
docker-compose --version
```

### Why Ansible for SelfHosting?

Because it as a powerful Automation Tool that the Pros are using to do crazy stuff with the cloud.

Why shouldnt we do it with our Pi's?

### Why Docker for SelfHosting?

<https://jalcocert.github.io/RPi/posts/selfhosting-with-docker/>