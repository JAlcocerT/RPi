---
title: Youtube Alternatives
author: JAlcocerT
date: 2022-08-10 14:10:00 +0800
categories: [Make your Raspberry Useful]
tags: [Self-Hosting,Docker]
render_with_liquid: false
---

So you have your Raspberry Pi [ready to SelfHost with Docker](https://jalcocert.github.io/RPi/posts/selfhosting-with-docker/) and you are looking for some YT alternatives.

Here you have few of them - Get your RPi's to work!

## Youtube-DL Material

It will allow you to Download YT Videos / Music - Even to Subscribe to your favourite Channels without a Google account..

```sh
#curl -L https://github.com/Tzahi12345/YoutubeDL-Material/releases/latest/download/docker-compose.yml -o docker-compose.yml
```

```yml
version: "2"
services:
    ytdl_material:
        environment: 
            ytdl_mongodb_connection_string: 'mongodb://ytdl-mongo-db:27017'
            ytdl_use_local_db: 'false'
            write_ytdl_config: 'true'
        restart: always
        depends_on:
            - ytdl-mongo-db
        volumes:
            - ./appdata:/app/appdata
            - ./audio:/app/audio
            - ./video:/app/video
            - ./subscriptions:/app/subscriptions
            - ./users:/app/users
        ports:
            - "8998:17442"
        image: tzahi12345/youtubedl-material:latest
    ytdl-mongo-db:
        # If you are using a Raspberry Pi, use mongo:4.4.18
        image: mongo:4
        logging:
            driver: "none"          
        container_name: mongo-db
        restart: always
        volumes:
            - ./db/:/data/db
```

After deployment - just visit: `http://localhost:8998`

if you want to get to know more about the project: <https://tzahi12345.github.io/YoutubeDL-Material/>

## Piped

Another front end for Youtube:

```sh
git clone https://github.com/TeamPiped/Piped-Docker
cd Piped-Docker

./configure-instance.sh

docker compose up -d
```


The project is public at [Github](https://github.com/TeamPiped/Piped).

## My Favourite - MeTube

ANd you can have [MeTube setup on your Raspberry](https://jalcocert.github.io/Linux/docs/linux__cloud.md/ansible/#ansible-like-a-pro) really quick.

I have done it with [Ansible *and Docker*](https://jalcocert.github.io/Linux/docs/linux__cloud.md/ansible/)

---

## FAQ

### How to use RSS to subscribe to YT channels?

<https://fossengineer.com/selfhosting-freshrss-with-docker>

### Other Alternative Youtube Front Ends

You can check other [alternatives to Self-Host your Youtube UI](https://fossengineer.com/youtube-alternative-front-ends), Invidious, YT Downloader...