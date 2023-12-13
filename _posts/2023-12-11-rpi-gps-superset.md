---
title: RPi IoT Project - GPS Data (VK-162) with Apache Superset
author: JAlcocerT
date: 2023-12-11 00:10:00 +0800
categories: [IoT & Data Analytics]
tags: [Sensors,Python,MongoDB]
image:
  path: /img/superset.png
  alt: IoT Project with Python, MongoDB, DHT11/22 sensors and Metabase.
render_with_liquid: false

---


## ToDo list

- [ ] Job Done!
  + [ ] Setup BI - Superset
  + [ ] Hardware Checks
  + [ ] Connecting everything


## Apache Superset Setup

Apache Superset is a [Free BI Web Tool](https://superset.apache.org/docs/intro/) that we can [use with our RPi projects locally](https://superset.apache.org/docs/installation/installing-superset-using-docker-compose/).


```sh
git clone https://github.com/apache/superset.git
cd superset

docker compose -f docker-compose-non-dev.yml up -d

#git checkout 3.0.0
#TAG=3.0.0 docker compose -f docker-compose-non-dev.yml up
```

Then, just use Superset with its UI at: **http://localhost:8088/login/**

![Desktop View](/img/superset-working.png){: width="972" height="589" }
_DHT22 connection to a Raspberry Pi 4_

*Default credentials are: admin/admin*

- [ ] Job Done!
  + [x] Setup BI - Superset
  + [ ] Hardware Checks
  + [ ] Connecting everything


## Sensors

* VK-162
* Columbus V-800 + [gpsd-gps](https://gpsd.io/) client
* BY-353 USB GPS


## FAQ

### Apache SupetSet with Portainer

This is the Stack in case that you can to deploy Superset with Portainer:

```yml
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
x-superset-image: &superset-image apachesuperset.docker.scarf.sh/apache/superset:${TAG:-latest-dev}
x-superset-depends-on: &superset-depends-on
  - db
  - redis
x-superset-volumes:
  &superset-volumes # /app/pythonpath_docker will be appended to the PYTHONPATH in the final container
  - ./docker:/app/docker
  - superset_home:/app/superset_home

version: "3.7"
services:
  redis:
    image: redis:7
    container_name: superset_cache
    restart: unless-stopped
    volumes:
      - redis:/data

  db:
    env_file: docker/.env-non-dev
    image: postgres:14
    container_name: superset_db
    restart: unless-stopped
    volumes:
      - db_home:/var/lib/postgresql/data
      - ./docker/docker-entrypoint-initdb.d:/docker-entrypoint-initdb.d

  superset:
    env_file: docker/.env-non-dev
    image: *superset-image
    container_name: superset_app
    command: ["/app/docker/docker-bootstrap.sh", "app-gunicorn"]
    user: "root"
    restart: unless-stopped
    ports:
      - 8088:8088
    depends_on: *superset-depends-on
    volumes: *superset-volumes

  superset-init:
    image: *superset-image
    container_name: superset_init
    command: ["/app/docker/docker-init.sh"]
    env_file: docker/.env-non-dev
    depends_on: *superset-depends-on
    user: "root"
    volumes: *superset-volumes
    healthcheck:
      disable: true

  superset-worker:
    image: *superset-image
    container_name: superset_worker
    command: ["/app/docker/docker-bootstrap.sh", "worker"]
    env_file: docker/.env-non-dev
    restart: unless-stopped
    depends_on: *superset-depends-on
    user: "root"
    volumes: *superset-volumes
    healthcheck:
      test:
        [
          "CMD-SHELL",
          "celery -A superset.tasks.celery_app:app inspect ping -d celery@$$HOSTNAME",
        ]

  superset-worker-beat:
    image: *superset-image
    container_name: superset_worker_beat
    command: ["/app/docker/docker-bootstrap.sh", "beat"]
    env_file: docker/.env-non-dev
    restart: unless-stopped
    depends_on: *superset-depends-on
    user: "root"
    volumes: *superset-volumes
    healthcheck:
      disable: true

volumes:
  superset_home:
    external: false
  db_home:
    external: false
  redis:
    external: false
```


### Apache Supserset DS's and API

* Data Sources: <https://superset.apache.org/docs/databases/db-connection-ui>
* API info: <https://superset.apache.org/docs/api>

### PhyPhox

* You can also save GPS data thanks to the [F/OSS PhyPhox](https://github.com/phyphox/phyphox-android) - An app that allow us to use phone's sensors for physics experiments:
  * Also available for [ESP32 with micropython](https://github.com/phyphox/phyphox-micropython)
  * And [also for Arduino](https://github.com/phyphox/phyphox-arduino)