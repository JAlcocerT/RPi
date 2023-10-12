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

```sh
ifconfig
```

The end result is that **the Raspberry Pi will act as a bridge between the WiFi connection and the Ethernet connection**, providing Internet access to devices connected via Ethernet- to the RPi.


## Raspberry Pi Bridge: Wifi to Ethernet (With wireguard)

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