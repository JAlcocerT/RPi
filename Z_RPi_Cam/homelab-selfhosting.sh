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

retry_curl_sh() {
    # retry_curl_sh <url> [max_retries]
    local url="$1"
    local max="${2:-3}"
    local i=0
    while [ "$i" -lt "$max" ]; do
        if curl -fsSL "$url" | sh; then
            return 0
        fi
        i=$((i + 1))
        log "Attempt $i/$max for $url failed, retrying..."
        sleep 5
    done
    return 1
}

log "Adding automatic updates..."
apt-get update -qq
apt-get install -y unattended-upgrades
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
        log "Warning: could not determine active interface, skipping DNS configuration"
    fi
else
    log "Warning: resolvectl not found, skipping DNS configuration"
fi


### CONTAINERS SETUP ###



# Function to install Docker and Docker Compose
install_docker() {
    log "Downloading Docker installation script..."
    local max_retries=3
    local retry=0

    while [ "$retry" -lt "$max_retries" ]; do
        if curl -fsSL https://get.docker.com -o get-docker.sh 2>/dev/null \
           && head -1 get-docker.sh | grep -q '^#!/' \
           && sh get-docker.sh; then
            rm -f get-docker.sh
            break
        fi
        retry=$((retry + 1))
        log "Docker install attempt $retry/$max_retries failed, retrying..."
        sleep 5
    done
    rm -f get-docker.sh

    if ! command_exists docker; then
        log "Error: Docker installation failed"
        return 1
    fi

    log "Docker installed: $(docker --version)"

    if ! systemctl is-active --quiet docker; then
        log "Starting Docker service..."
        systemctl start docker
    fi

    # Compose plugin ships with get.docker.com — skip deprecated docker-compose package
    if docker compose version >/dev/null 2>&1; then
        log "Docker Compose plugin available: $(docker compose version --short)"
    else
        log "Warning: Docker Compose plugin not detected"
    fi

    log "Testing Docker with hello-world..."
    if ! timeout 30 docker run --rm hello-world >/dev/null 2>&1; then
        log "Warning: hello-world test failed (network?), continuing"
    else
        log "Docker test passed"
    fi

    log "Launching Portainer..."
    docker run -d -p 8000:8000 -p 9000:9000 \
        --name=portainer --restart=always \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v portainer_data:/data \
        portainer/portainer-ce || log "Warning: Portainer launch failed (already running?)"
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



# Ask user if they want to install Docker - https://jalcocert.github.io/RPi/posts/selfhosting-with-docker/#install-docker
log "Do you want to install Containers on your system? (yes/no)"
read -r install_docker_answer
case $install_docker_answer in
    [yY] | [yY][eE][sS])
        install_docker || { log "Error: Docker installation failed"; exit 1; }
        install_podman || log "Warning: Podman installation failed, continuing"
        ;;
    [nN] | [nN][oO])
        log "Container installation skipped."
        ;;
    *)
        log "Invalid response. Exiting."
        exit 1
        ;;
esac

### TAILSCALE VPN ###

# Function to install Tailscale VPN - https://jalcocert.github.io/Linux/docs/debian/linux_vpn_setup/#tailscale
install_tailscale() {
    log "Installing Tailscale VPN..."

    if ! retry_curl_sh "https://tailscale.com/install.sh" 3; then
        log "Error: Tailscale installation failed after retries"
        return 1
    fi

    if ! command_exists tailscale; then
        log "Error: tailscale not found after installation"
        return 1
    fi

    log "Bringing Tailscale up (auth in browser if prompted)..."
    tailscale up || log "Warning: 'tailscale up' returned non-zero (manual auth may be needed)"

    if tailscale status >/dev/null 2>&1; then
        ip_address=$(tailscale ip -4 2>/dev/null || echo "not assigned yet")
        log "Tailscale IP: $ip_address"
    fi
}


# Ask user if they want to install Tailscale VPN
log "Do you want to install Tailscale VPN on your system? (yes/no)"
read -r install_tailscale_answer
case $install_tailscale_answer in
    [yY] | [yY][eE][sS])
        install_tailscale || { log "Error: Tailscale installation failed"; exit 1; }
        ;;
    [nN] | [nN][oO])
        log "Tailscale VPN installation skipped."
        ;;
    *)
        log "Invalid response. Exiting."
        exit 1
        ;;
esac


### SECURITY HARDENING ###
# Based on security-audit.md (Debian 13 / RPi)

harden_firewall() {
    echo "Installing UFW..."
    apt-get install -y ufw
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow 22/tcp comment 'SSH'
    ufw --force enable
    ufw status verbose
}

harden_fail2ban() {
    echo "Installing fail2ban..."
    apt-get install -y fail2ban
    cat > /etc/fail2ban/jail.d/sshd.local <<'EOF'
[sshd]
enabled = true
port    = ssh
maxretry = 4
bantime  = 1h
findtime = 10m
EOF
    systemctl enable --now fail2ban
    systemctl restart fail2ban
}

harden_ssh() {
    echo "Hardening SSH config..."
    SSHD=/etc/ssh/sshd_config
    cp -n "$SSHD" "${SSHD}.bak.$(date +%s)"

    set_sshd() {
        key="$1"; val="$2"
        if grep -qE "^\s*#?\s*${key}\b" "$SSHD"; then
            sed -i -E "s|^\s*#?\s*${key}\b.*|${key} ${val}|" "$SSHD"
        else
            echo "${key} ${val}" >> "$SSHD"
        fi
    }

    set_sshd PermitRootLogin no
    set_sshd PubkeyAuthentication yes
    set_sshd X11Forwarding no
    set_sshd ChallengeResponseAuthentication no
    set_sshd KbdInteractiveAuthentication no

    # Only disable password auth if a key already exists for the invoking user
    target_user="${SUDO_USER:-jalcocert}"
    auth_keys="/home/${target_user}/.ssh/authorized_keys"
    if [ -s "$auth_keys" ]; then
        echo "Authorized key found for ${target_user}. Disabling password auth."
        set_sshd PasswordAuthentication no
    else
        echo "WARNING: no authorized_keys for ${target_user} at ${auth_keys}."
        echo "Leaving PasswordAuthentication enabled to prevent lockout."
        echo "Add a key, then re-run: sed -i 's/^PasswordAuthentication.*/PasswordAuthentication no/' ${SSHD} && systemctl reload ssh"
    fi

    sshd -t && systemctl reload ssh
}

harden_bluetooth() {
    echo "Disabling Bluetooth via boot overlay..."
    # Debian 13 on RPi uses /boot/firmware/config.txt; older images use /boot/config.txt
    for cfg in /boot/firmware/config.txt /boot/config.txt; do
        if [ -f "$cfg" ]; then
            grep -q '^dtoverlay=disable-bt' "$cfg" || echo 'dtoverlay=disable-bt' >> "$cfg"
            echo "Updated $cfg"
        fi
    done
    systemctl disable --now bluetooth.service hciuart.service 2>/dev/null || true
}

harden_sysctl() {
    echo "Applying kernel sysctl hardening..."
    cat > /etc/sysctl.d/99-hardening.conf <<'EOF'
# Network
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0
net.ipv4.conf.all.secure_redirects = 0
net.ipv4.conf.default.secure_redirects = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.tcp_syncookies = 1
# Kernel
kernel.kptr_restrict = 2
kernel.dmesg_restrict = 1
kernel.yama.ptrace_scope = 2
kernel.sysrq = 0
EOF
    sysctl --system
}

harden_tmp_noexec() {
    echo "Setting noexec on /tmp..."
    if grep -qE '^\s*tmpfs\s+/tmp\s' /etc/fstab; then
        sed -i -E 's|^(\s*tmpfs\s+/tmp\s+tmpfs\s+)([^[:space:]]+)|\1rw,nosuid,nodev,noexec|' /etc/fstab
    else
        echo 'tmpfs /tmp tmpfs rw,nosuid,nodev,noexec 0 0' >> /etc/fstab
    fi
    echo "Reboot or 'mount -o remount /tmp' to apply."
}

harden_journald() {
    echo "Limiting journald size..."
    sed -i -E 's|^#?SystemMaxUse=.*|SystemMaxUse=100M|' /etc/systemd/journald.conf
    grep -q '^SystemMaxUse=' /etc/systemd/journald.conf || echo 'SystemMaxUse=100M' >> /etc/systemd/journald.conf
    systemctl restart systemd-journald
}

harden_cron() {
    echo "Restricting cron..."
    target_user="${SUDO_USER:-jalcocert}"
    {
        echo "root"
        echo "$target_user"
    } > /etc/cron.allow
    chmod 644 /etc/cron.allow
}

harden_pwquality() {
    echo "Installing libpam-pwquality..."
    apt-get install -y libpam-pwquality
    # Minimal sane defaults
    sed -i -E 's|^#?\s*minlen\s*=.*|minlen = 12|' /etc/security/pwquality.conf 2>/dev/null || true
    sed -i -E 's|^#?\s*retry\s*=.*|retry = 3|' /etc/security/pwquality.conf 2>/dev/null || true
}

harden_auditd() {
    echo "Installing auditd..."
    apt-get install -y auditd audispd-plugins
    systemctl enable --now auditd
}

harden_docker_logs() {
    # Cap Docker container logs so they don't fill the SD card.
    # Default json-file driver is unbounded.
    if ! command_exists docker; then
        log "Docker not installed, skipping log caps."
        return 0
    fi

    local daemon_json=/etc/docker/daemon.json
    mkdir -p /etc/docker

    if [ -f "$daemon_json" ]; then
        cp -n "$daemon_json" "${daemon_json}.bak.$(date +%s)"
        # Merge log-opts into existing file if jq available
        if command_exists jq; then
            log "Merging log caps into existing $daemon_json..."
            tmp=$(mktemp)
            jq '. + {
                "log-driver": "json-file",
                "log-opts": { "max-size": "10m", "max-file": "3" },
                "live-restore": true
            }' "$daemon_json" > "$tmp" && mv "$tmp" "$daemon_json"
        else
            log "Warning: jq not found. $daemon_json exists; skipping merge to avoid clobber."
            log "Install jq (apt-get install -y jq) and re-run, or edit manually."
            return 0
        fi
    else
        log "Writing fresh $daemon_json with log caps..."
        cat > "$daemon_json" <<'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true
}
EOF
    fi

    chmod 644 "$daemon_json"

    # Validate JSON
    if command_exists python3; then
        if ! python3 -c "import json; json.load(open('$daemon_json'))" 2>/dev/null; then
            log "Error: $daemon_json invalid JSON. Restoring backup."
            mv "${daemon_json}.bak."* "$daemon_json" 2>/dev/null || true
            return 1
        fi
    fi

    if systemctl is-active --quiet docker; then
        log "Restarting Docker to apply log caps..."
        systemctl restart docker
    fi

    log "Note: log caps apply to NEW containers. Recreate existing containers to take effect:"
    log "  docker ps -q | xargs -r docker restart   # not enough — must recreate"
    log "  cd <compose-dir> && docker compose up -d --force-recreate"
}

harden_docker_isolation() {
    # Container isolation flags merged into /etc/docker/daemon.json.
    # Each flag prompted individually because tradeoffs differ.
    # Run on FRESH installs; existing volumes may need chown after userns-remap.
    if ! command_exists docker; then
        log "Docker not installed, skipping isolation hardening."
        return 0
    fi

    apt-get install -y jq
    if ! command_exists jq; then
        log "Error: jq required for safe daemon.json merge. Aborting isolation step."
        return 1
    fi

    local daemon_json=/etc/docker/daemon.json
    mkdir -p /etc/docker
    [ -f "$daemon_json" ] || echo '{}' > "$daemon_json"
    cp -n "$daemon_json" "${daemon_json}.bak.$(date +%s)"

    apply_jq() {
        local expr="$1"
        local tmp
        tmp=$(mktemp)
        jq "$expr" "$daemon_json" > "$tmp" && mv "$tmp" "$daemon_json"
    }

    # --- Flag 1: no-new-privileges ---
    log "Enable 'no-new-privileges' (blocks setuid escalation in containers)?"
    log "  Risk: NONE for typical workloads. Recommended."
    log "  (yes/no)"
    read -r nnp_answer
    case $nnp_answer in
        [yY]|[yY][eE][sS])
            apply_jq '. + {"no-new-privileges": true}'
            log "no-new-privileges enabled."
            ;;
        *) log "no-new-privileges skipped." ;;
    esac

    # --- Flag 2: icc=false ---
    log "Disable inter-container communication on default bridge ('icc: false')?"
    log "  Risk: containers on default bridge stop talking to each other."
    log "  Mitigation: create explicit networks per stack ('docker network create')."
    log "  Recommended for fresh installs where you control compose files."
    log "  (yes/no)"
    read -r icc_answer
    case $icc_answer in
        [yY]|[yY][eE][sS])
            apply_jq '. + {"icc": false}'
            log "icc=false applied. Remember: per-stack networks required."
            ;;
        *) log "icc left at default (true)." ;;
    esac

    # --- Flag 3: userns-remap ---
    log "Enable userns-remap (container UID 0 != host UID 0)?"
    log "  Risk: HIGH on existing systems. Existing volumes need chown to remapped UID."
    log "  Recommended ONLY for fresh installs with no pre-existing volumes."
    log "  (yes/no)"
    read -r userns_answer
    case $userns_answer in
        [yY]|[yY][eE][sS])
            apply_jq '. + {"userns-remap": "default"}'
            log "userns-remap=default applied. Subuid/subgid range auto-created on docker restart."
            log "WARNING: existing volumes may be inaccessible until chowned to dockremap UID."
            ;;
        *) log "userns-remap skipped." ;;
    esac

    chmod 644 "$daemon_json"

    # Validate
    if command_exists python3; then
        if ! python3 -c "import json; json.load(open('$daemon_json'))" 2>/dev/null; then
            log "Error: $daemon_json invalid JSON. Restoring backup."
            mv "${daemon_json}.bak."* "$daemon_json" 2>/dev/null || true
            return 1
        fi
    fi

    if systemctl is-active --quiet docker; then
        log "Restarting Docker to apply isolation flags..."
        systemctl restart docker
    fi

    log "Final daemon.json:"
    cat "$daemon_json"
}

harden_logrotate() {
    # Ensure /var/log doesn't grow unbounded. Debian ships logrotate by default;
    # this just verifies + tightens rsyslog rotation if present.
    apt-get install -y logrotate

    # Tighten rsyslog rotation if config present
    if [ -f /etc/logrotate.d/rsyslog ]; then
        log "logrotate rsyslog config present (defaults are sane)."
    fi

    # Force a run to clean any oversize files
    logrotate -f /etc/logrotate.conf || log "Warning: logrotate run returned non-zero"
}

apply_hardening() {
    harden_firewall
    harden_fail2ban
    harden_ssh
    harden_sysctl
    harden_tmp_noexec
    harden_journald
    harden_logrotate
    harden_docker_logs
    harden_docker_isolation
    harden_cron
    harden_pwquality
    harden_auditd
    log "Hardening done. Reboot recommended."
}

log "Apply security hardening (UFW, fail2ban, SSH, sysctl, /tmp, journald, cron, pwquality, auditd)? (yes/no)"
read -r harden_answer
case $harden_answer in
    [yY] | [yY][eE][sS])
        apply_hardening
        ;;
    [nN] | [nN][oO])
        log "Security hardening skipped."
        ;;
    *)
        log "Invalid response. Exiting."
        exit 1
        ;;
esac


### DISABLE BLUETOOTH (RPi) ###

# Standalone prompt: touches /boot/firmware/config.txt and requires reboot.
# Available regardless of hardening choice.
log "Disable Bluetooth (RPi only, edits boot overlay, requires reboot)? (yes/no)"
read -r bt_answer
case $bt_answer in
    [yY] | [yY][eE][sS])
        harden_bluetooth
        log "Bluetooth disabled. Reboot to take effect."
        ;;
    [nN] | [nN][oO])
        log "Bluetooth left untouched."
        ;;
    *)
        log "Invalid response. Exiting."
        exit 1
        ;;
esac


### INSTALLATION SUMMARY ###

log "Homelab setup complete! Installed versions:"
echo ""

if command_exists unattended-upgrade; then
    echo "✓ unattended-upgrades: $(dpkg -l | awk '/^ii  unattended-upgrades/ {print $3}')"
fi

if command_exists docker; then
    echo "✓ Docker: $(docker --version | awk '{print $3}' | sed 's/,//')"
fi

if docker compose version >/dev/null 2>&1; then
    echo "✓ Docker Compose (plugin): $(docker compose version --short)"
fi

if command_exists podman; then
    echo "✓ Podman: $(podman --version | awk '{print $3}')"
fi

if command_exists tailscale; then
    echo "✓ Tailscale: $(tailscale version | head -1)"
fi

if command_exists ufw; then
    echo "✓ UFW: $(ufw status | head -1)"
fi

if command_exists fail2ban-client; then
    echo "✓ fail2ban: $(fail2ban-client --version 2>/dev/null | head -1)"
fi

echo ""
log "Tailscale: run 'tailscale up' to authenticate if not already"
log "Portainer: http://localhost:9000"
log "Reboot recommended to apply hardening (Bluetooth/sysctl/tmpfs)"