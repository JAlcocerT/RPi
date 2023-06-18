---
title: "Raspberry Pi Media server: Docker Stack with NextCloud, Photoview, Navidrome..."
date: 2022-10-30T23:20:21+01:00
draft: false
tags: ["Self-Hosting","Projects","Docker"]
---




<!-- sudo apt-get update & sudo apt-get upgrade -y & sudo reboot
curl -sSL https://get.docker.com | sh

sudo apt-get install libffi-dev libssl-dev & \
sudo apt install python3-dev -y & \
sudo apt-get install -y python3 python3-pip & \

sudo curl https://sh.rustup.rs -sSf | sh & \
sudo pip3 install docker-compose & \
sudo systemctl enable docker & \

sudo systemctl status docker
sudo apt-get install docker-compose-plugin
sudo apt install docker-compose -y
sudo docker compose version

sudo systemctl start docker
systemctl status docker.service

sudo docker run hello-world -->


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