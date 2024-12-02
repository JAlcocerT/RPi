#!/usr/bin/env bash

set -e

[ $EUID -ne 0 ] && echo "run as root" >&2 && exit 1

apt update && \
  DEBIAN_FRONTEND=noninteractive apt install -y \
    dnsmasq netfilter-persistent iptables-persistent

# Create and persist iptables rule.
# The change: we're using the WireGuard interface (your_vpn_wireguard_netw_interface) instead of the WiFi interface (wlan0).
iptables -t nat -A POSTROUTING -o proton -j MASQUERADE
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