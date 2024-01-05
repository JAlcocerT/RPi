---
title: Adjust HDMI Signal
author: JAlcocerT
date: 2024-01-04 00:34:00 +0800
categories: [RPi Setup]
tags: [RPi 101]
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
git clone https://github.com/JAlcocerT/RPi ./RPi
#cd ./RPi/Z_ansible


```

### Mongo Project

```sh
ansible-playbook ./RPi/Z_ansible/Ansible_py_dht_mongo_meta.yml -i inventory.ini #execute Meta Project Playbook
```

### Influx Project

```sh
ansible-playbook ./RPi/Z_ansible/Ansible_py_dht_influx_grafana.yml -i inventory.ini #execute Influx Project Playbook
```
