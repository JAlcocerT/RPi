---
title: Raspberry Pi & How to Self-Host anything
author: JAlcocerT
date: 2022-07-25 14:10:00 +0800
categories: [RPi Setup]
tags: [Self-Hosting, Docker, RPi 101]
render_with_liquid: false
---

So you already have your [RPi and the OS Setup](https://jalcocert.github.io/RPi/posts/getting-started/)

[**Self-Hosting** can be simplified](https://jalcocert.github.io/Linux/docs/linux__cloud/selfhosting/) with Docker.

>  Use your Raspberry with [other **services** with docker](https://github.com/JAlcocerT/Docker)
{: .prompt-info }

Thanks to the great work of the community that **bundles a lot of Apps/services** into container images and make them available, together with their code.

## Install Docker


To install docker in the RPI, we need a different installation since their processors are ARM based.

```sh
apt-get update && sudo apt-get upgrade && curl -fsSL https://get.docker.com -o get-docker.sh
```

```sh
sh get-docker.sh && docker version

#Test that docker works with this image:
#sudo docker run hello-world
```
### Install Docker-Compose

```sh
apt install docker-compose -y
```
Check the version with:

```sh
docker-compose --version
```
And check the status with:

```sh
systemctl status docker
#sudo systemctl start docker #if it is not running
#systemctl list-units --type=service
#systemctl list-units --type=service --state=running
```
#### Installing Portainer


```sh
docker run -d -p 8000:8000 -p 9000:9000 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce
```


## Trying *any* App with Docker

Remember that the RPi works with an **ARM processors**, so expect some changes in the `.yml` configuration files when another compatible image has to be used.

When pulling the images, docker will find the one that suits your machine (if no specific version is specified) when available. 


> Make sure that the Docker image tag that you are pulling supports multi-arch*itecture* and that ARM (32 or 64) is between them.
{: .prompt-tip }

## Example: deploying several Apps at once with Docker-Compose

### One App - Whoogle

```yml
---
version: "2"
services:
  whoogle:
    image: benbusby/whoogle-search:latest
    container_name: whoogle
    ports:
      - 5000:5000
    restart: unless-stopped
    
#sudo docker run --name whoogle -d -p 5000:5000/udp -p 5000:5000/tcp \
#--restart=always benbusby/whoogle-search:latest

#docker run --publish 5000:5000 --detach --name whoogle benbusby/whoogle-search:latest
```

### Several Apps - Raspberry Pi Media server

[Docker Stack](https://github.com/JAlcocerT/Docker/tree/main/Z_Dockge/stacks) with: NextCloud, Photoview, Navidrome,...





```yml
version: "3"

services:
  db:
    image: linuxserver/mariadb
    restart: always
    environment:
      - MYSQL_DATABASE=photoview
      - MYSQL_USER=photoview
      - MYSQL_PASSWORD=photosecret
      - MYSQL_RANDOM_ROOT_PASSWORD=1
    volumes:
      - db_data:/var/lib/mysql

  photoview:
    image: viktorstrate/photoview:2
    restart: always
    ports:
      - "8099:80"
    depends_on:
      - db
    environment:
      - PHOTOVIEW_DATABASE_DRIVER=mysql
      - PHOTOVIEW_MYSQL_URL=photoview:photosecret@tcp(db)/photoview
      - PHOTOVIEW_LISTEN_IP=photoview
      - PHOTOVIEW_LISTEN_PORT=80
      - PHOTOVIEW_MEDIA_CACHE=/app/cache
    volumes:
      - api_cache:/app/cache
      # Change This: to the directory where your photos are located on your server.
      # If the photos are located at `/home/user/photos`, then change this value
      # to the following: `/home/user/photos:/photos:ro`.
      # You can mount multiple paths, if your photos are spread across multiple directories.
      - ~/Docker/Syncthing/config/Photoview:/photos:ro #it respects your file system photo organization & remember to mention /photos/whatever_path in the initial setup 

# volumes:
#   db_data:
#   api_cache:


  syncthing:
    image: ghcr.io/linuxserver/syncthing
    container_name: syncthing
    hostname: syncthing #optional
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Warsaw
    volumes:
      - /home/rpi_user_name/Docker/Syncthing/config:/config
      - /home/rpi_user_name/Docker/Syncthing/Photoview:/data1
      - /media/pi/Nowy/Syncthing_RPi:/data2
    ports:
      - 8384:8384
      - 22000:22000/tcp
      - 22000:22000/udp
      - 21027:21027/udp
    restart: unless-stopped
    
    

  navidrome:
    image: deluan/navidrome:latest
    ports:
      - "4533:4533"
    environment:
      # Optional: put your config options customization here. Examples:
      ND_SCANSCHEDULE: 1h
      ND_LOGLEVEL: info  
      ND_BASEURL: ""
    volumes:
      - "~/Docker/navidrome/data:/data"
      - "~/Docker/Syncthing/config/Aficiones/Musica:/music:ro"
      


  db:
    image: linuxserver/mariadb
    restart: always
    container_name: nextclouddb
    volumes:
      - /home/rpi_user_name/Docker/nextcloud/db:/var/lib/mysql
    environment:
      - MYSQL_INITDB_SKIP_TZINFO=1
      - MYSQL_ROOT_PASSWORD=rootpass
      - MYSQL_PASSWORD=ncpass
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud

  app:
    image: nextcloud
    container_name: nextcloud
    restart: always
    ports:
      - 8080:80
    links:
      - db
    volumes:
      - /home/rpi_user_name/Docker/nextcloud/html:/var/www/html
    environment:
      - MYSQL_PASSWORD=ncpass
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_HOST=db
      - NEXTCLOUD_TRUSTED_DOMAINS=http://192.168.3.31:8080 http://0.0.0.0:8080


  duplicati:
    image: ghcr.io/linuxserver/duplicati
    container_name: duplicati
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Madrid
      - CLI_ARGS= #optional
    volumes:
    - ~/Docker/Duplicati/config:/config
    - ~/Docker:/source
    - ~/Docker/backups:/backups
    ports:
      - 8200:8200
    restart: unless-stopped

volumes:
  db_data:
  api_cache:
  nextcloud:
  db:    
```

---

## FAQ

### Looking Forward to Self-Host other Apps?

I have been consolidating a list of docker-compose files to deploy several F/OSS Apps in [my Docker repository](https://github.com/JAlcocerT/Docker)

* See more **detailed guides** [here](https://fossengineer.com/tags/self-hosting)

### Monitoring the server performance?

You can have a look on how the things are going with [**Netdata** and Docker](https://fossengineer.com/selfhosting-server-monitoring-with-netdata-and-docker/).