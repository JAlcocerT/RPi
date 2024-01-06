---
title: IoT Projects with Ansible and Raspberry Pi
author: JAlcocerT
date: 2024-01-04 00:34:00 +0800
categories: [IoT & Data Analytics]
tags: [Self-Hosting]
---



## Ansible with RPi

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
git clone https://github.com/JAlcocerT/RPi ./RPi1
#cd ./RPi/Z_ansible


```

### Mongo Project

So you want to have the project that pulls data from DHT11 or DHT22, sends it from Python to Mongo and then Display it in Metabase?

No issues, just execute:

```sh
ansible-playbook ./RPi/Z_ansible/Ansible_py_dht_mongo_meta.yml -i inventory.ini #execute Meta Project Playbook
```


> Im Talking about: [Raspberry Pi - DHT to MongoDB](https://jalcocert.github.io/RPi/posts/rpi-iot-dht1122-mongo/)
{: .prompt-info }


### Influx Project

```sh
ansible-playbook ./RPi/Z_ansible/Ansible_py_dht_influx_grafana.yml -i inventory.ini #execute Influx Project Playbook
```

> This is the one: [Raspberry Pi - DHT to InfluxDB](https://jalcocert.github.io/RPi/posts/rpi-iot-dht11-influxdb/)
{: .prompt-info }