##!/bin/sh

# Check for root privileges
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi


echo "Adding automatic updates..."
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades


### BETTER DNS ###

### Changes the DNS for the active interface and shows the status before and after ###

# Display initial DNS status
echo "Initial DNS settings for the active interface:"
interface=$(resolvectl status | grep -A 1 'Link 2' | awk -F '[()]' '/Link 2/{print $2}') ##enp2s0 // ##wlx984827ec3e41
resolvectl status $interface

# Change DNS servers to Quad9
echo "Changing DNS to Quad9 (9.9.9.9, 149.112.112.112) for interface $interface."
resolvectl dns $interface 9.9.9.9 149.112.112.112 ##https://www.quad9.net/

# Display new DNS settings
echo "Updated DNS settings for interface $interface:"
resolvectl status $interface

echo "Confirming the Updated DNS settings for: $interface:"
resolvectl status | grep 'DNS Servers'


### CONTAINERS SETUP ###



# Function to install Docker and Docker Compose
install_docker() {
    echo "Updating system and installing required packages..."
    apt-get update && apt-get upgrade -y
    echo "Downloading Docker installation script..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    echo "Docker installed successfully. Checking Docker version..."
    docker version
    echo "Testing Docker installation with 'hello-world' image..."
    docker run hello-world
    echo "Installing Docker Compose..."
    apt install docker-compose -y
    echo "Docker Compose installed successfully. Checking version..."
    docker-compose --version
    echo "Checking status of Docker service..."
    #systemctl status docker
    systemctl status docker | grep "Active"
    docker run -d -p 8000:8000 -p 9000:9000 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce

}

install_podman() {
    echo "Installing Podman OCI..."
    apt install podman
    podman --version
}



# Ask user if they want to install Docker - https://jalcocert.github.io/RPi/posts/selfhosting-with-docker/#install-docker
echo "Do you want to install Containers on your system? (yes/no)"
read install_docker_answer
case $install_docker_answer in
    [yY] | [yY][eE][sS])
        install_docker #Docker Containers
        install_podman #Podman Containers
        ;;
    [nN] | [nN][oO])
        echo "Docker installation skipped."
        ;;
    *)
        echo "Invalid response. Exiting."
        exit 1
        ;;
esac

### TAILSCALE VPN ###

# Function to install Tailscale VPN - https://jalcocert.github.io/Linux/docs/debian/linux_vpn_setup/#tailscale
install_tailscale() {
    echo "Installing Tailscale VPN..."
    curl -fsSL https://tailscale.com/install.sh | sh
    sudo tailscale up
    echo "Tailscale VPN installed and activated."

    ip_address=$(tailscale ip -4)
    echo "The IP address assigned by Tailscale is: $ip_address"
}


# Ask user if they want to install Tailscale VPN
echo "Do you want to install Tailscale VPN on your system? (yes/no)"
read install_tailscale_answer
case $install_tailscale_answer in
    [yY] | [yY][eE][sS])
        install_tailscale
        ;;
    [nN] | [nN][oO])
        echo "Tailscale VPN installation skipped."
        ;;
    *)
        echo "Invalid response. Exiting."
        exit 1
        ;;
esac