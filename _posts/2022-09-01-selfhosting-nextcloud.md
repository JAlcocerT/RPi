---
title: Raspberry Pi as your Cloud Storage -  with Nextcloud & Docker
author: JAlcocerT
date: 2022-09-01 14:10:00 +0800
categories: [RPi Setup]
tags: [Self-Hosting, Docker]
render_with_liquid: false
---

To install nextcloud in RPi, we need to include MariaDB in the installation (it supports ARM processors, not like mysql).


## Installing Docker Stuff

First things first. [Get Docker](https://fossengineer.com/docker-first-steps-guide-for-data-analytics/) and Docker-Compose ready in your Rpi.

## Deploy Nextcloud with Docker

Let's use **Docker-Compose** to have nextcloud server installed without any complications:


```yml
version: '2'

volumes:
  nextcloud:
  db:

services:
  db:
    image: linuxserver/mariadb
    restart: always
    container_name: nextclouddb
    volumes:
      - /home/Docker/nextcloud/db:/var/lib/mysql
    environment:
      - MYSQL_INITDB_SKIP_TZINFO=1
      - MYSQL_ROOT_PASSWORD=rootpass
      - MYSQL_PASSWORD=ncpass
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
#    networks: ["nginx_nginx_network"] #optional 

  app:
    image: nextcloud #latest
    container_name: nextcloud
    restart: always
    ports:
      - 8080:80
    links:
      - db
    volumes:
      - /home/Docker/nextcloud/html:/var/www/html
    environment:
      - MYSQL_PASSWORD=ncpass
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_HOST=db
      - NEXTCLOUD_TRUSTED_DOMAINS=http://0.0.0.0:8080 #https://nextcloud.yourduckdnsubdomain.duckdns.org/
#    networks: ["nginx_nginx_network"] #optional 
 
# networks: #optional
#   nginx_nginx_network: #optional
#     external: true #optional
```


## FAQ

Remember to update the list of trusted domains so that other devices can log, we can see the current list with:

```sh
sudo docker exec --user www-data nextcloud_container php occ config:system:get trusted_domains
```

To add a new domain/internal/local ip, simply pass it in the end of this CLI command:


```sh
sudo docker exec --user www-data nextcloud_container php occ config:system:set trusted_domains 7 --value 192.168.1.22:8080
```

Remember that you can check your device (the RPi here) internal IP adress with:


```sh
hostname -I
```

To access nextcloud while being out of home, simply [configure your VPN, for example with tailscale](https://jalcocert.github.io/Linux/debian/ubuntu/linux_vpn_setup/), and add the internal Ip address assign by tailscale as shown two commands before.