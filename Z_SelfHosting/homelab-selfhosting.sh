#!/bin/bash

set -euo pipefail

# Check for root privileges
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

log "Adding automatic updates..."
apt-get update -qq
apt-get install unattended-upgrades -y
dpkg-reconfigure -plow unattended-upgrades


### BETTER DNS ###

if command_exists resolvectl; then
    log "Configuring DNS with resolvectl..."
    interface=$(resolvectl status | grep -A 1 'Link 2' | awk -F '[()]' '/Link 2/{print $2}' || echo "")

    if [ -n "$interface" ]; then
        log "Initial DNS settings for interface: $interface"
        resolvectl status "$interface"

        log "Changing DNS to Quad9 (9.9.9.9, 149.112.112.112)..."
        resolvectl dns "$interface" 9.9.9.9 149.112.112.112

        log "Updated DNS settings:"
        resolvectl status "$interface"
    else
        log "Warning: Could not determine active interface, skipping DNS configuration"
    fi
else
    log "Warning: resolvectl not found, skipping DNS configuration"
    log "To configure DNS manually, edit /etc/resolv.conf or use your system's network manager"
fi


### CONTAINERS SETUP ###

install_docker() {
    log "Updating system and installing required packages..."
    apt-get update -qq
    apt-get upgrade -y

    log "Downloading Docker installation script..."
    local max_retries=3
    local retry=0
    local script_url="https://get.docker.com"

    while [ $retry -lt $max_retries ]; do
        if curl -fsSL "$script_url" -o get-docker.sh 2>/dev/null; then
            # Basic check: script should be executable bash/sh
            if head -1 get-docker.sh | grep -q '^#!/'; then
                log "Docker script downloaded, executing..."
                if sh get-docker.sh; then
                    rm -f get-docker.sh
                    return 0
                else
                    log "Docker install script failed, retrying..."
                    retry=$((retry + 1))
                    sleep 5
                    continue
                fi
            fi
        fi
        log "Download attempt $((retry + 1))/$max_retries failed, retrying..."
        retry=$((retry + 1))
        sleep 5
    done

    log "Error: Docker installation failed after $max_retries attempts"
    rm -f get-docker.sh
    return 1

    log "Verifying Docker installation..."
    if ! docker version >/dev/null 2>&1; then
        log "Error: Docker installation failed"
        return 1
    fi

    log "Testing Docker daemon..."
    if ! systemctl is-active --quiet docker; then
        log "Starting Docker service..."
        systemctl start docker
    fi

    # Docker compose is already installed via docker-compose-plugin
    # Skip standalone docker-compose package to avoid conflicts
    if command_exists docker-compose; then
        log "Docker Compose already installed: $(docker-compose --version)"
    elif docker compose version >/dev/null 2>&1; then
        log "Docker Compose (plugin) available: $(docker compose version)"
    else
        log "Warning: Docker Compose not found"
    fi

    log "Testing Docker with hello-world (this may take a moment)..."
    if ! timeout 30 docker run --rm hello-world >/dev/null 2>&1; then
        log "Warning: hello-world test failed (may be network issue), continuing anyway"
    else
        log "Docker test passed"
    fi

    log "Launching Portainer..."
    docker run -d -p 8000:8000 -p 9000:9000 \
        --name=portainer --restart=always \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v portainer_data:/data \
        portainer/portainer-ce || log "Warning: Portainer launch may have failed"

}

install_podman() {
    log "Installing Podman OCI..."
    apt-get install -y podman

    if command_exists podman; then
        log "Podman installed: $(podman --version)"
    else
        log "Error: Podman installation failed"
        return 1
    fi
}



log "Do you want to install Containers on your system? (yes/no)"
read -r install_docker_answer
case $install_docker_answer in
    [yY] | [yY][eE][sS])
        log "Installing Docker and Podman..."
        if install_docker; then
            log "Docker installation completed"
        else
            log "Error: Docker installation failed"
            exit 1
        fi

        if install_podman; then
            log "Podman installation completed"
        else
            log "Warning: Podman installation failed, continuing"
        fi
        ;;
    [nN] | [nN][oO])
        log "Container installation skipped"
        ;;
    *)
        log "Invalid response. Exiting."
        exit 1
        ;;
esac

### TAILSCALE VPN ###

install_tailscale() {
    log "Installing Tailscale VPN..."

    local max_retries=3
    local retry=0
    local script_url="https://tailscale.com/install.sh"

    while [ $retry -lt $max_retries ]; do
        if curl -fsSL "$script_url" 2>/dev/null | sh; then
            log "Tailscale installation completed"
            return 0
        fi
        log "Tailscale install attempt $((retry + 1))/$max_retries failed, retrying..."
        retry=$((retry + 1))
        sleep 5
    done

    log "Error: Tailscale installation failed after $max_retries attempts"
    return 1

    if ! command_exists tailscale; then
        log "Error: Tailscale not found after installation"
        return 1
    fi

    log "Run 'tailscale up' to authenticate and activate"
    log "Visit https://login.tailscale.com to complete authentication"

    if tailscale status >/dev/null 2>&1; then
        ip_address=$(tailscale ip -4 2>/dev/null || echo "not assigned yet")
        log "Tailscale IP: $ip_address"
    fi
}

log "Do you want to install Tailscale VPN on your system? (yes/no)"
read -r install_tailscale_answer
case $install_tailscale_answer in
    [yY] | [yY][eE][sS])
        if install_tailscale; then
            log "Tailscale installation completed"
        else
            log "Error: Tailscale installation failed"
            exit 1
        fi
        ;;
    [nN] | [nN][oO])
        log "Tailscale VPN installation skipped"
        ;;
    *)
        log "Invalid response. Exiting."
        exit 1
        ;;
esac

### INSTALLATION SUMMARY ###

log "Homelab setup complete! Installed versions:"
echo ""

# Unattended upgrades
if command_exists unattended-upgrade; then
    echo "✓ unattended-upgrades: $(dpkg -l | grep unattended-upgrades | awk '{print $3}')"
fi

# Docker
if command_exists docker; then
    docker_version=$(docker --version | awk '{print $3}' | sed 's/,//')
    echo "✓ Docker: $docker_version"
fi

# Docker Compose
if command_exists docker-compose; then
    echo "✓ docker-compose: $(docker-compose --version | awk '{print $4}')"
elif docker compose version >/dev/null 2>&1; then
    echo "✓ Docker Compose (plugin): $(docker compose version --short)"
fi

# Podman
if command_exists podman; then
    echo "✓ Podman: $(podman --version | awk '{print $3}')"
fi

# Tailscale
if command_exists tailscale; then
    echo "✓ Tailscale: $(tailscale version | head -1)"
fi

echo ""
log "For Tailscale: run 'tailscale up' to authenticate"
log "Access Portainer at: http://localhost:9000"