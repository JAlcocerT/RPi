---
title: "Raspberry Pi as your Cloud Storage: Nextcloud with Docker"
date: 2022-10-30T23:20:21+01:00
draft: false
tags: ["Self-Hosting","Projects","Docker"]
---

To install nextcloud in RPi, we need to include MariaDB in the installation (it supports ARM processors, not like mysql).


Let's use **Docker-Compose** to have it installed with Docker:

{{< gist jalcocert cf73aed383470d8764642499f034d5dc
"Docker-Backups-nextcloud-RPi.yml">}}

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

To access nextcloud while being out of home, simply [configure your VPN, for example with tailscale](https://jalcocert.github.io/Linux/debian/ubuntu/linux_vpn_setup/), and add the internal Ip address assign by tail scale as shown two commands before.
