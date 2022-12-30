---
title: "Nextcloud with Docker"
date: 2022-10-30T23:20:21+01:00
draft: false
tags: ["Self-Hosting","Projects","Docker"]
---

To install nextcloud in RPi, we need to include MariaDB in the installation (it supports ARM processors, not like mysql)

In linux systems it is as simple as running the following commands in the terminal after having installed docker:

```
sudo docker run -d -v ~/nextcloud:/var/www/html -p 8080:80 --name nextcloud_container nextcloud 
```


Remember to update the list of trusted domains so that other devices can log, we can see the current list with:

```
sudo docker exec --user www-data nextcloud_container php occ config:system:get trusted_domains
```

To add a new domain/ internal ip, simply:


```
sudo docker exec --user www-data nextcloud_container php occ config:system:set trusted_domains 7 --value 192.168.1.30:8080
```

Remember that you can check your device internal IP adress with:


```
hostname -I
```

To access nextcloud while being out of home, simply configure your VPN, for example with tailscale, and add the internal Ip address assign by tail scale as shown two commands before.

As this would fall under general linux systems, the guide sits on: <https://jalcocert.github.io/Linux/post/forth/#tailscale>
