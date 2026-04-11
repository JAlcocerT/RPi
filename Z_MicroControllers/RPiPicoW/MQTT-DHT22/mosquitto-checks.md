# Mosquitto CLI Checks

Quick commands to verify MQTT data is flowing from the Pico W.

## Install (Ubuntu)

```sh
sudo apt install mosquitto-clients
```

## Subscribe to Pico W topics

```sh
mosquitto_sub -h 192.168.1.2 -t "pico/#" -v #see the data flowing
```

Expected output:

```
pico/temperature/internal 27.43
pico/temperature/dht22 23.1
pico/humidity/dht22 55.3
```

## Subscribe to all topics on the broker

```sh
mosquitto_sub -h 192.168.1.2 -t "#" -v
```

## With authentication

```sh
mosquitto_sub -h 192.168.1.2 -t "pico/#" -v -u <username> -P <password>
```

## Publish a test message

```sh
mosquitto_pub -h 192.168.1.2 -t "test/hello" -m "world"
```

## Check Mosquitto service status (on the broker server)

```sh
sudo systemctl status mosquitto
```

## View broker logs (on the broker server)

```sh
sudo journalctl -u mosquitto -f
```
