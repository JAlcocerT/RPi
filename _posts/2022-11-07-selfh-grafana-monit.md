---
title: RPi Monitoring - Eyes on Everything with Grafana
author: JAlcocerT
date: 2022-11-07 14:10:00 +0800
categories: [IoT & Data Analytics]
tags: [Self-Hosting,Docker,InfluxDB,Prometheus]
render_with_liquid: false
---


## Why Grafana?

Its been a while that I have been talking about self-hosting.

At some point, we can be wondering how our devices (probably small Raspberry Pi's or old laptops) are doing with all of that workload.

This is the moment where you will be interested to know about Grafana.

* <https://github.com/JAlcocerT/Docker/tree/main/IoT>
* <https://hub.docker.com/r/grafana/grafana-oss>
* This video was of great help to me: <https://www.youtube.com/watch?v=IoD3vFuep64&t=370s>


## Grafana: with Prometheus and Node Exporter

* <https://github.com/starsliao/Prometheus>
* <https://grafana.com/grafana/dashboards/11074-node-exporter-for-prometheus-dashboard-en-v20201010/>

```yml
version: '3'

volumes:
  prometheus-data:
    driver: local

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - /home/Docker/monitoringserver/prometheus:/etc/prometheus
      - prometheus-data:/prometheus
    restart: unless-stopped
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
  node_exporter:
    image: quay.io/prometheus/node-exporter:latest
    container_name: node_exporter
    command:
      - '--path.rootfs=/host'
    pid: host
    restart: unless-stopped
    volumes:
      - '/home/Docker/monitoringserver/nodeexporter/:/host:ro,rslave' 
  grafana:
    image: grafana/grafana-oss:latest
    container_name: grafana
    ports:
      - "3457:3000"
    networks: ["nginx_nginx_network"] #optional      
    restart: unless-stopped

networks: #optional
  nginx_nginx_network: #optional
    external: true #optional
```    

default creds: *admin/admin*


We will need the /etc/prometheus/prometheus.yml file

in this case here:

```sh
sudo nano /home/Docker/monitoringserver/prometheus/prometheus.yml
```


Then, spin up the docker containers with: docker-compose up -d

<http://localhost:9090/graph?g0.expr=&g0.tab=1&g0.stacked=0&g0.show_exemplars=0&g0.range_input=1h>
<http://localhost:3457/dashboards>

* #Add Prometheus as grafana data source ---> http://localhost:9090
http://127.0.0.1:3457/connections/your-connections/datasources
http://127.0.0.1:3457/connections/your-connections/datasources/edit/d8d34b8f-1618-45ad-922c-53bbb9a19f90

* Import existing dashboard with its ID:
    * <https://grafana.com/grafana/dashboards/11074-node-exporter-for-prometheus-dashboard-en-v20201010/>
    * Use the prometheus DB


* Visit your dashboard: http://127.0.0.1:3457/d/xfpJB9FGz/1-node-exporter-for-prometheus-dashboard-en-20201010?orgId=1&from=now-1h&to=now





## Grafana with: InfluxDB and Telegraph

This resources were of great help to me to understand this topic:

* <https://www.youtube.com/watch?v=NOWoLfpY2kE>
    * Telegraph inputs: <https://github.com/influxdata/telegraf/tree/master/plugins/inputs>
    * <https://github.com/shazforiot/How-To-Setup-Influxdb-Telegraf-And-Grafana-using-Docker-Compose/tree/main>


We will need:

<https://github.com/jmlcas/grafana-influxdb-telegraf>

<https://github.com/JAlcocerT/Docker/blob/main/IoT/Grafana_InfluxDB_Telegraf_docker-compose.yaml>

<https://hub.docker.com/_/telegraf/tags>
<https://hub.docker.com/_/influxdb/tags>




```yml
version: '3.6'
services:
  telegraf:
    image: telegraf
    container_name: telegraf_TIG
    restart: always
    volumes:
    - /home/Docker/Monitoring_TIG/telegraf.conf:/etc/telegraf/telegraf.conf:ro
    depends_on:
      - influxdb
    links:
      - influxdb
    ports:
    - '8125:8125'

  influxdb:
    image: influxdb:1.8 #influxdb:1.8-alpine #x86 only
    container_name: influxdb_TIG
    restart: always
    environment:
      - INFLUXDB_DB=influx
      - INFLUXDB_ADMIN_USER=admin
      - INFLUXDB_ADMIN_PASSWORD=admin
    ports:
      - '8066:8086'
    volumes:
      - /home/Docker/Monitoring_TIG/influxdb_data:/var/lib/influxdb

  grafana:
    image: grafana/grafana
    container_name: grafana-server_TIG
    restart: always
    depends_on:
      - influxdb
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
    links:
      - influxdb
    ports:
      - '3003:3000'
```

Telegraph config: **CREATE IT BEFORE DEPLOYING!**

```sh
sudo nano /home/Docker/Monitoring_TIG/telegraf.conf
```

```yml
#Grafana_InfluxDB_Telegraf_docker-compose.yaml
#docker compose up -d

 [global_tags]

[agent]
  interval = "60s"
  round_interval = true
  metric_batch_size = 1000
  metric_buffer_limit = 10000
  collection_jitter = "0s"
  flush_interval = "10s"
  flush_jitter = "0s"
  precision = ""
  hostname = "192.168.3.200"
  omit_hostname = false

[[outputs.influxdb]]
  urls = ["http://influxdb:8066"]
  database = "influx"
  timeout = "5s"
  username = "telegraf"
  password = "metricsmetricsmetricsmetrics"


[[inputs.cpu]]
  percpu = true
  totalcpu = true
  collect_cpu_time = false
  report_active = false


[[inputs.disk]]
  ignore_fs = ["tmpfs", "devtmpfs", "devfs", "iso9660", "overlay", "aufs", "squashfs"]


[[inputs.diskio]]

[[inputs.kernel]]

[[inputs.mem]]

[[inputs.processes]]

[[inputs.swap]]

[[inputs.system]]
```


## Grafana with: Prometheus, nodexp and Cadvisor

<https://grafana.com/grafana/dashboards/15120-docker-and-os-metrics-for-raspberry-pi/>

<https://github.com/JAlcocerT/Docker/blob/main/IoT/cAdvisor_docker-compose.yml>
<https://github.com/JAlcocerT/Docker/blob/main/IoT/Grafana_Prometheus_Cadvisor_NodeExp_docker-compose.yaml>

Prometheus config:

```yml
#Grafana_Prometheus_Cadvisor_NodeExp_docker-compose.yaml
#sudo docker-compose up -d

scrape_configs:
  - job_name: 'prometheus'
    scrape_interval: 30s
    static_configs:
      - targets: ['localhost:9090', 'cadvisor:8080', 'node-exporter:9100']
```