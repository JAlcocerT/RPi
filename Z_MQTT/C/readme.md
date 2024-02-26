
```sh
sudo apt-get update
#sudo apt-get install libpaho-mqtt-dev
sudo apt-get install build-essential git cmake



gcc -o mqtt_publish mqtt_publish.c -lpaho-mqtt3c
./mqtt_publish
#gcc -o mqtt_publish_server mqtt_publish_server.c -lpaho-mqtt3c
#./mqtt_publish_server

```