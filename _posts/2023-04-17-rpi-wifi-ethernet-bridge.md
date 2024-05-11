---
title: Raspberry Pi - Wifi to Ethernet Bridge (Through Wireguard VPN)
author: JAlcocerT
date: 2023-04-17 14:10:00 +0800
categories: [Networking]
tags: [Networking]
render_with_liquid: false
---


## Raspberry Pi: Wifi Bridge


I was inspired by the awsome work of **[William Halley in his blog](https://www.willhaley.com/blog/raspberry-pi-wifi-ethernet-bridge/)**, where I was able to follow succesfully the option 2 that it is proposed: *to share Wifi through Ethernet on a separated subnet*.

- [ ] What do we need? 🎯
  + [x] A Raspberry Pi (Im using a Pi4 2gb, ARM32) with [Raspberry Pi OS installed](https://jalcocert.github.io/RPi/posts/getting-started/#how-to-get-started-with-a-rpi)
  + [x] A [custom script](#rpi-bridge-wifi-to-eth-with-vpn) to route our RPi Wifi connectivity to Ethernet and pass its VPN connectivity
  + [ ] A Wireguard Server: You can [use any provider](#vpn-providers) like [Mullvad VPN](https://fossengineer.com/selfhosting-qBittorrent-with-docker-and-VPN/), [Proton VPN](https://fossengineer.com/transmission-with-vpn-torrent/), NordVPN...or **create your own VPN Server**
  + [ ] An Ethernet Cable - Most likely you Router brought some
  + [ ] (Optional) USB-C to Ethernet or some HUB with multiple ports if your device does not have Ethernet

### Initial Setup: Option 2 - Separate Subnet

This original approach does not require any VPN, as we are just providing the same internet connection that our RPi receives via Wifi, to our laptop/any other device, via ethernet.

The Raspberry and your device will have the same connection details ☝️

The script that is provided is this one (again, [credits to](#aknowledgments) William):

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

```sh
ifconfig
```

The end result is that **the Raspberry Pi will act as a bridge between the WiFi connection and the Ethernet connection**, providing Internet access to devices connected via Ethernet- to the RPi.


### RPi Bridge: Wifi to Eth (With VPN)

That was really great and I was really impressed and happy that it worked perfectly the first time I tried.

Then, I wondered...*if the Raspberry Pi would be having a VPN connection, could we provide to the ethernet connected device that same connection?*

I decided to try with **Wireguard** (you will need a working VPN server that generates Wireguard config) and surprisingly **it worked with some modification**:


1) First, we need to have wireguard installed:


```sh
sudo apt install wireguard
cp /home/Downloads/your_vpn_wireguard_configuration.conf /etc/wireguard #download the wireguard config: account-wireguard configuration
sudo wg-quick your_vpn_wireguard_configuration #the name of the .conf file that you have downloaded
```

This will make your wireguard client to be connected to the server. Do you want to check your public IP?


```sh
curl -sS https://ipinfo.io/json #the command to use
```

And if you need, to disconnect from Wireguard, just:


```sh
wg-quick down <name>
sudo wg-quick down your_vpn_wireguard_configuration
#sudo nano /etc/resolv.conf #to check/adapt DNS name (optional)
#sudo reboot (optional)
```

2) Use this command to check which network interface your wireguard VPN has:

```sh
ifconfig
```

3) This will be our new **bridge_wireguard.sh** script to route the WIFI to ethernet and provide VPN connection at the same time:

```sh
sudo nano bridge_wireguard.sh
```

And save this file:

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
{: file='/home/bridge_wireguard.sh'}


```sh
sudo bash bridge_wireguard.sh
sudo reboot
```

Now, when connecting your device via Ethernet to the RPI, you should see that the connectivity is VPN routed:

```sh
curl -sS https://ipinfo.io/json #the command to use
#wget -qO- https://ipinfo.io/json

#for windows you would use
#powershell -Command "(Invoke-WebRequest -Uri https://ipinfo.io/json).Content"
```


---

## FAQ

### Aknowledgments

Original idea from [William Halley in his blog](https://www.willhaley.com/blog/raspberry-pi-wifi-ethernet-bridge/)

* Thanks also to:
  * [Novaspirit Tech](https://www.youtube.com/watch?v=qhe6KUw3D78)
  * How to SelfHost your [VPN with Docker and Gluetun](https://fossengineer.com/gluetun-vpn-docker/)

### VPN Providers

* https://mullvad.net/en/account
* https://account.proton.me/u/0/vpn/dashboard
* https://my.nordaccount.com/dashboard/

```sh
sh <(curl -sSf https://downloads.nordcdn.com/apps/linux/install.sh)
# wget "https://repo.nordvpn.com/deb/nordvpn/debian/pool/main/nordvpn-release_1.0.0_all.deb?nv_tri=TC_7139823260542166_1715430552755&nv_trs=1715430552756_1715430943116_1_25" -O nordvpn-release_1.0.0_all.deb
# sudo dpkg -i nordvpn-release_1.0.0_all.deb

nordvpn --version

#sudo usermod -aG nordvpn $USER
```

You can see other **NordVPN commands** [here](https://support.nordvpn.com/hc/en-us/articles/20196094470929-Installing-NordVPN-on-Linux-distributions)

```sh
nordvpn login
#nordvpn set dns 9.9.9.9 149.112.112.112 #https://www.quad9.net/service/service-addresses-and-features

#nordvpn countries — see the country list.
#nordvpn cities switzerland

nordvpn set lan-discovery enable #— enable/disable LAN discovery.

nordvpn connect #https://nordvpn.com/servers/tools/
nordvpn connect switzerland
#nordvpn status 

curl -sS https://ipinfo.io/json #the command to use

#nordvpn disconnect
```

### How to Run your Wireguard VPN Server



* PiVPN is a set of shell scripts developed to easily turn your Raspberry Pi™ into a VPN server using two free, open-source protocols: Wireguard & OpenVPN https://github.com/pivpn/pivpn