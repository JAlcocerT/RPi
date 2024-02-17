---
title: Edge Analytics with Raspberry Pi
author: JAlcocerT
date: 2024-02-28 00:34:00 +0800
categories: [Make your Raspberry Useful]
tags: [IoT, Sensors]
---

Stream Processing at the IoT Edge

> Ekuiper works great when combined with [EMQx Broker](https://jalcocert.github.io/RPi/posts/rpi-mqtt/#install-mqtt-broker)

## Setup Ekuiper

Lets use the [Ekuiper Docker Image](https://hub.docker.com/r/lfedge/ekuiper)

```sh
docker run -p 9081:9081 -d --name ekuiper -e MQTT_SOURCE__DEFAULT__SERVER=tcp://broker.emqx.io:1883 lfedge/ekuiper:latest
```

`http://localhost:9081/`

## Using Ekuiper

https://ekuiper.org/docs/en/latest/getting_started/quick_start_docker.html


---

## FAQ

https://github.com/lf-edge/ekuiper

### AI/ML

* TF Lite - https://ekuiper.org/docs/en/latest/guide/ai/python_tensorflow_lite_tutorial.html
    * https://www.tensorflow.org/lite/guide