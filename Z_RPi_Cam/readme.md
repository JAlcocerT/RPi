* Further **info** at::
	* https://jalcocert.github.io/JAlcocerT/blog/tinker-rpi-cv/
	* https://github.com/JAlcocerT/rpi-mjpg-streamer
	( https://jalcocert.github.io/JAlcocerT/raspberry-pi-camera-setup/)
	* Related to [DJI Cam Drone](https://jalcocert.github.io/JAlcocerT/dji-tello-python-programming/)

```sh
git clone https://github.com/meinside/rpi-mjpg-streamer #https://github.com/JAlcocerT/rpi-mjpg-streamer
cd rpi-mjpg-streamer
```

Build the image:

```sh
sudo docker build -t streamer:latest \
		--build-arg PORT=9999 \
		--build-arg RESOLUTION=400x300 \
		--build-arg FPS=24 \
		--build-arg ANGLE=0 \
		--build-arg FLIPPED=false \
		--build-arg MIRRORED=false \
		--build-arg USERNAME=user \
		--build-arg PASSWORD=some-password \
		.
```

Deploy the image:

```sh
docker run -p 9999:9999 --device /dev/video0 -it streamer:latest
```


---

## Pre-Requisites

Get a Rpi and [install the OS](https://github.com/raspberrypi/rpi-imager/releases/tag/v2.0.8) and docker:

```sh
choco install rpi-imager
```

![alt text](rpi-imager.png)

I2C has to be enabled!