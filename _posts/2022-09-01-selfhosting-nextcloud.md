---
title: Raspberry Pi as your Cloud Storage - With Nextcloud & Docker
author: JAlcocerT
date: 2022-09-01 14:10:00 +0800
categories: [Make your Raspberry Useful]
tags: [Self-Hosting, Docker]
render_with_liquid: false
---

To install **Nextcloud in a Pi**, we need to include a working DB.

For example, lets use **MariaDB** in the installation.

Tt supports ARM/x86 processors, *unlike mysql*.

## Nextcloud for Raspberry Pi

### Installing Docker Stuff

First things first.

Lets get ready for SelfHosting

[Get Docker](https://jalcocert.github.io/Linux/docs/linux__cloud/selfhosting/) and Docker-Compose ready in your Rpi.

### Deploy Nextcloud with Docker

Let's use **Docker-Compose** to have nextcloud server installed without any complications.

>  See the **Nextcloud [config file](https://github.com/JAlcocerT/Docker/blob/main/Backups/NextCloud/nc_mariadb.yml)** and more [here](https://github.com/JAlcocerT/Docker/tree/main/Backups/NextCloud).
{: .prompt-info }

```yml
#version: '2'

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
    image: nextcloud #latest #27.0.0
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

---

## FAQ

Remember to update the **list of trusted domains** so that other devices can log, we can see the current list with:

```sh
sudo docker exec --user www-data nextcloud_container php occ config:system:get trusted_domains
```

To add a new domain/internal/local ip, simply pass it in the end of this CLI command:

```sh
sudo docker exec --user www-data nextcloud_container php occ config:system:set trusted_domains 7 --value 192.168.1.22:8080
#sudo docker exec --user www-data nextcloud_container php occ config:system:set trusted_domains 7 --value nextcloud.yourgreatname.duckdns.org
```

Remember that you can check your device (the RPi here) internal IP adress with:

```sh
hostname -I
#ifconfig
```

To access nextcloud while being out of home, simply [configure your VPN, for example with tailscale](https://jalcocert.github.io/Linux/debian/ubuntu/linux_vpn_setup/), and add the internal Ip address assign by tailscale as shown two commands before.

You can also **see your files with the WebDav** feature, just add in your file manager:

```sh
davs://example.com/nextcloud/remote.php/dav/files/USERNAME/
#davs://nextcloud.yourgreatname.duckdns.org/nextcloud/remote.php/dav/files/USERNAME/
```

> If your server connection is not HTTPS-secured, use `dav://` instead of `davs://`.

Alternatively - you can [try FileBrowser](https://fossengineer.com/selfhosting-filebrowser-docker/)

### How to use a External Drive with NextCloud

```sh
lsblk
lsblk -a
lsblk -f
sudo fdisk -l
```

Once you have identify the drive, format it.

For example, with NTFS:

```sh
#sudo mkfs.ntfs /dev/sda1 #make sure it is /dev/sda1 as well for you
#sudo mkfs.ntfs -Q /dev/sda1 #quick version
```

Then, mount the drive:

```sh
sudo mkdir /usbdrive
sudo mount /dev/sda1 /usbdrive
```

If you `df -h` - you will see the drive mounted.

You can always **copy the data with**:

```sh
#sudo cp -R ./files/* /mnt/mydrive/
sudo rsync -avh --progress ./files/* /mnt/mydrive/ #with progress
```

And you can **check the full size of the copied folder**:

```sh
du -sh ./files
```

### Other Interesting Selhostable Tools

1. Cosmos Server: It will ask you to connect to a DB (it can create one itself)

> Use this **[config file](https://github.com/JAlcocerT/Docker/blob/main/Z_Dockge/stacks/cosmosserver/compose.yml)**. See the UI at `http://192.168.0.12:800/cosmos-ui/newInstall`

2. [NGINX Proxy Manager](https://fossengineer.com/selfhosting-nginx-proxy-manager-docker/): To get https certificates for Nextcloud or any other docker service. [**Config file**](https://github.com/JAlcocerT/Docker/blob/main/Security/Proxy/nginx_docker_compose.yaml).

3. See also: Portainer, Yatch, Dockge or [CasaOS](https://github.com/IceWhaleTech/CasaOS). 

> CasaOS: Community-based open source software focused on delivering simple personal cloud experience around Docker ecosystem.