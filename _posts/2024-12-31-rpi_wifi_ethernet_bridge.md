---
title: "Raspberry Pi: Wifi to Ethernet Bridge (through Wireguard VPN)"
date: 2024-12-30T23:20:21+01:00
draft: true
tags: ["Self-Hosting"]
---

<!-- 
openwrt
<https://www.youtube.com/watch?v=fOYmHPmvSVg> -->

<!-- <https://www.youtube.com/watch?v=qhe6KUw3D78> -->


## Raspberry Pi: Wifi Bridge


I was inspired by the awsome work of **[William Halley in his blog](https://www.willhaley.com/blog/raspberry-pi-wifi-ethernet-bridge/)**, where I was able to follow succesfully the option 2 that it is proposed: *to share Wifi through Ethernet on a separated subnet*.

### Initial Setup: Option 2 - Separate Subnet

The script that is provided is this one (again, credits to William):

```sh
#!/usr/bin/env bash

set -e

[ $EUID -ne 0 ] && echo "run as root" >&2 && exit 1

apt update && \
  DEBIAN_FRONTEND=noninteractive apt install -y \
    dnsmasq netfilter-persistent iptables-persistent

# Create and persist iptables rule.
iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
netfilter-persistent save

# Enable ipv4 forwarding.
sed -i'' s/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/ /etc/sysctl.conf

# The Ethernet adapter will use a static IP of 10.1.1.1 on this new subnet.
cat <<'EOF' >/etc/network/interfaces.d/eth0
auto eth0
allow-hotplug eth0
iface eth0 inet static
  address 10.1.1.1
  netmask 255.255.255.0
  gateway 10.1.1.1
EOF

# Create a dnsmasq DHCP config at /etc/dnsmasq.d/bridge.conf. The Raspberry Pi
# will act as a DHCP server to the client connected over ethernet.
cat <<'EOF' >/etc/dnsmasq.d/bridge.conf
interface=eth0
bind-interfaces
server=8.8.8.8
domain-needed
bogus-priv
dhcp-range=10.1.1.2,10.1.1.254,12h
EOF

systemctl mask networking.service
```

* If like me you are new to networking, I think going line by line and taking time to understand what we are doing is important:
  * #!/usr/bin/env bash: This is the shebang line that determines the script's interpreter. In this case, the script will be run using bash shell.
  * set -e: This command causes the shell to exit if any invoked command fails.
  * [ $EUID -ne 0 ] && echo "run as root" >&2 && exit 1: This line checks if the script is run as root. If not, it prints an error message and exits. Root privileges are required to modify system configurations.
  * apt update && \: This command updates the list of available packages from the repositories.
  * DEBIAN_FRONTEND=noninteractive apt install -y \: This installs the necessary packages non-interactively, meaning it won't prompt for user input during installation.
  * dnsmasq netfilter-persistent iptables-persistent: These are the packages being installed. Dnsmasq is a lightweight DHCP and caching DNS server. Netfilter-persistent and iptables-persistent are used for managing and saving iptables rules.
  * iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE: This line adds a rule to iptables that will masquerade all outgoing traffic from the Raspberry Pi as coming from itself, essentially making the Pi act as a gateway for the connected device.
    * We are using wlan0 as is it the default for the Raspberry Pi
  * netfilter-persistent save: This saves the iptables rules so they persist across reboots.
  * sed -i'' s/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/ /etc/sysctl.conf: This line enables IP forwarding, which is necessary for routing traffic.
  * The cat <<'EOF' >/etc/network/interfaces.d/eth0 block: This block creates a network configuration file for the eth0 interface. It sets the interface to use a static IP address (10.1.1.1) and acts as a gateway on the 10.1.1.0/24 subnet.
  * The cat <<'EOF' >/etc/dnsmasq.d/bridge.conf block: This block creates a dnsmasq configuration file that sets the Raspberry Pi to act as a DHCP server on the eth0 interface. This will assign IP addresses to devices connected to the Pi over Ethernet.
  * systemctl mask networking.service: This command prevents the networking service from being started on boot. This is necessary because the script manually configures the network interfaces, and the networking service could interfere with this.

* **Remember**, the names of wlan0 and eth0 used, can be different in other devices, check it with:

{{< cmd >}}
ifconfig
{{< /cmd >}}

The end result is that **the Raspberry Pi will act as a bridge between the WiFi connection and the Ethernet connection**, providing Internet access to devices connected via Ethernet- to the RPi.


## Raspberry Pi Bridge: Wifi to Ethernet (With wireguard)

That was really great and I was really impressed and happy that it worked perfectly the first time I tried.

Then, I wondered...*if the Raspberry Pi would be having a VPN connection, could we provide to the ethernet connected device that same connection?*

I decided to try with **Wireguard** (you will need a working VPN server that generates Wireguard config) and surprisingly **it worked with some modification**:


1) First, we need to have wireguard installed:

{{< cmd >}}
sudo apt install wireguard
cp /home/Downloads/your_vpn_wireguard_configuration.conf /etc/wireguard #download the wireguard config: account-wireguard configuration
sudo wg-quick your_vpn_wireguard_configuration #the name of the .conf file that you have downloaded
{{< /cmd >}}

This will make your wireguard client to be connected to the server. Do you want to check your public IP?

{{< cmd >}}
curl -sS https://ipinfo.io/json #the command to use
{{< /cmd >}}

And if you need, to disconnect from Wireguard, just:

{{< cmd >}}
wg-quick down <name>
sudo wg-quick down your_vpn_wireguard_configuration
#sudo nano /etc/resolv.conf #to check/adapt DNS name (optional)
#sudo reboot (optional)
{{< /cmd >}}

2) Use this command to check which network interface your wireguard VPN has:

{{< cmd >}}
ifconfig
{{< /cmd >}}

3) This will be our new **bridge_wireguard.sh** script to route the WIFI to ethernet and provide VPN connection at the same time:



{{< cmd >}}
sudo nano bridge_wireguard.sh
{{< /cmd >}}

```sh
#!/usr/bin/env bash

set -e

[ $EUID -ne 0 ] && echo "run as root" >&2 && exit 1

apt update && \
  DEBIAN_FRONTEND=noninteractive apt install -y \
    dnsmasq netfilter-persistent iptables-persistent

# Create and persist iptables rule.
# Here's the change: we're using the WireGuard interface (your_vpn_wireguard_netw_interface) instead of the WiFi interface (wlan0).
iptables -t nat -A POSTROUTING -o your_vpn_wireguard_netw_interface -j MASQUERADE
netfilter-persistent save

# Enable ipv4 forwarding.
sed -i'' s/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/ /etc/sysctl.conf

# The Ethernet adapter will use a static IP of 10.1.1.1 on this new subnet.
cat <<'EOF' >/etc/network/interfaces.d/eth0
auto eth0
allow-hotplug eth0
iface eth0 inet static
  address 10.1.1.1
  netmask 255.255.255.0
  gateway 10.1.1.1
EOF

# Create a dnsmasq DHCP config at /etc/dnsmasq.d/bridge.conf. The Raspberry Pi
# will act as a DHCP server to the client connected over ethernet.
cat <<'EOF' >/etc/dnsmasq.d/bridge.conf
interface=eth0
bind-interfaces
server=8.8.8.8
domain-needed
bogus-priv
dhcp-range=10.1.1.2,10.1.1.254,12h
EOF

systemctl mask networking.service
```

{{< cmd >}}
sudo bash bridge_wireguard.sh
sudo reboot
{{< /cmd >}}

<!-- 
## with Tailscale VPN  -->


<!-- 

With open vpn it works:
https://www.youtube.com/watch?v=h0sR7tKuI-U

https://switchedtolinux.com/tutorials/wireless-internet-passed-to-ethernet-with-raspberry-pi -->


<!-- 

```sh
tailscale status #to check to which one
sudo tailscale up --exit-node=100.100.157.71 #sudo tailscale up --exit-node=<exit-node-ip>
```

```sh
sudo nano bridge_tailscale.sh
```

```sh
#!/usr/bin/env bash

set -e

[ $EUID -ne 0 ] && echo "run as root" >&2 && exit 1

apt update && \
  DEBIAN_FRONTEND=noninteractive apt install -y \
    dnsmasq netfilter-persistent iptables-persistent

# Create and persist iptables rule.
# Here's the change: we're using the Tailscale interface (tailscale0) instead of the WireGuard interface (se-mma-wg-004).
iptables -t nat -A POSTROUTING -o tailscale0 -j MASQUERADE
netfilter-persistent save

# Enable ipv4 forwarding.
sed -i'' s/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/ /etc/sysctl.conf

# The Ethernet adapter will use a static IP of 10.1.1.1 on this new subnet.
cat <<'EOF' >/etc/network/interfaces.d/eth0
auto eth0
allow-hotplug eth0
iface eth0 inet static
  address 10.1.1.1
  netmask 255.255.255.0
  gateway 10.1.1.1
EOF

# Create a dnsmasq DHCP config at /etc/dnsmasq.d/bridge.conf. The Raspberry Pi
# will act as a DHCP server to the client connected over ethernet.
cat <<'EOF' >/etc/dnsmasq.d/bridge.conf
interface=eth0
bind-interfaces
server=8.8.8.8
domain-needed
bogus-priv
dhcp-range=10.1.1.2,10.1.1.254,12h
EOF

systemctl mask networking.service
```



```sh
sudo bash bridge_tailscale.sh
sudo reboot
```


 -->

<!-- 
## with Docker - GLUETUN and MULLVAD

1) Get Docker installed
2) Get Gluetun installed

```yml
version: "3"
services:
  gluetun:
    image: qmcgaw/gluetun
    container_name: your_gluetun_container_name    
    cap_add:
      - NET_ADMIN
    network_mode: host #this has to be included 
    environment:
      - VPN_SERVICE_PROVIDER=mullvad
      - VPN_TYPE=wireguard
      - WIREGUARD_PRIVATE_KEY==you_will_need_this_input
      - WIREGUARD_ADDRESSES=and_also_the_ipv4_version
      - SERVER_CITIES=New York NY #choose any available city
    volumes:
      - /Home/Docker/Gluetun:/gluetun
    restart: unless-stopped
```

With this configuration, the Gluetun container will share the network stack with the host machine, and it will be able to directly access network interfaces, ports, and other network resources on the host.

Please note that using host networking can have security implications, as it gives the container full access to the host's network resources. **It also bypasses the network isolation provided by Docker**, which can lead to conflicts if multiple containers try to use the same network resources. Use host networking with caution, and only when necessary.

3) Get to know the docker network of gluetun

```sh
docker network ls
```
You will see something like: *vpn-mullvad_default* <stackname_default>

Remember the **Network id**

You can also inspect it with its name:

```sh
docker network inspect vpn-mullvad_default
```

Then, have a look to *ifconfig* and find a network interface that combines br-<network_id> we just found:


You can also check if gluetun is properly connected to the VPN server with:

```sh
docker exec -it gluetun /bin/sh
```

curl is not added and the base image of gluetun is Alpine.

It is: local and bridge, but what else?

actually with netdata under the category Network interfaces you will see more


4) identify which of the network interfaces (docker0, br-xxxxxx, or vethxxxxx...) listed in ifconfig is our docker container with Gluetun

for that i used a trick with netdata and discovered that the container routing traffic is: br-d3a974f1a730 (the others were not transmitting any data). I tried downloading with [qbittorrent routed with Gluetun](https://fossengineer.com/selfhosting-qBittorrent-with-docker-and-VPN/) the lates Raspberry PI image to make evident were the traffic was.


br-d3a974f1a730: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.18.0.1  netmask 255.255.0.0  broadcast 172.18.255.255
        inet6 fe80::42:23ff:feae:9bcc  prefixlen 64  scopeid 0x20<link>
        ether 02:42:23:ae:9b:cc  txqueuelen 0  (Ethernet)
        RX packets 3668  bytes 514241 (502.1 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 5732  bytes 6635627 (6.3 MiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0 -->

<!-- 
you can also use wireshark -->
<!-- 
```sh
sudo nano bridge_docker_mullvad.sh
```


```sh
#!/usr/bin/env bash

set -e

[ $EUID -ne 0 ] && echo "run as root" >&2 && exit 1

apt update && \
  DEBIAN_FRONTEND=noninteractive apt install -y \
    dnsmasq netfilter-persistent iptables-persistent

# Create and persist iptables rule.
# Here's the change: we're using the Docker network interface (br-d3a974f1a730) instead of the WireGuard interface (se-mma-wg-004).
iptables -t nat -A POSTROUTING -o br-d3a974f1a730 -j MASQUERADE
netfilter-persistent save

# Enable ipv4 forwarding.
sed -i'' s/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/ /etc/sysctl.conf

# The Ethernet adapter will use a static IP of 10.1.1.1 on this new subnet.
cat <<'EOF' >/etc/network/interfaces.d/eth0
auto eth0
allow-hotplug eth0
iface eth0 inet static
  address 10.1.1.1
  netmask 255.255.255.0
  gateway 10.1.1.1
EOF

# Create a dnsmasq DHCP config at /etc/dnsmasq.d/bridge.conf. The Raspberry Pi
# will act as a DHCP server to the client connected over ethernet.
cat <<'EOF' >/etc/dnsmasq.d/bridge.conf
interface=eth0
bind-interfaces
server=8.8.8.8
domain-needed
bogus-priv
dhcp-range=10.1.1.2,10.1.1.254,12h
EOF

systemctl mask networking.service
```




```sh
sudo bash bridge_docker_mullvad.sh
sudo reboot
``` -->

---

## FAQ

### Checking WIFI Networks the RPi Connects 

```sh
nano /etc/wpa_supplicant/wpa_supplicant.conf
```

### Installing ping


```sh
apt-get install -y iputils-ping
```
<!-- 

### How to add Debian Buster Backports to Raspberry Pi OS (libseccomp2)

> FOR JELLYFIN & QBITTORRENT TO WORK:

```sh
$ echo 'deb http://deb.debian.org/debian buster-backports main contrib non-free' | sudo tee -a /etc/apt/sources.list
$ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 04EE7237B7D453EC 648ACFD622F3D138
$ sudo apt update
$ sudo apt install -t buster-backports [package]
sudo apt install -t buster-backports youtube-dl

```

```sh
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 04EE7237B7D453EC 648ACFD622F3D138
echo "deb http://deb.debian.org/debian buster-backports main" | sudo tee -a /etc/apt/sources.list.d/buster-backports.list
sudo apt update
sudo apt install -t buster-backports libseccomp2
``` -->