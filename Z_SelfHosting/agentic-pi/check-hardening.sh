#!/bin/bash

# Read-only audit. Verifies that homelab-selfhosting.sh hardening was applied.
# No mutations. Exit code = number of failed checks.
#
# Usage: sudo ./check-hardening.sh
#        sudo ./check-hardening.sh --quiet   # only failures + summary
#
# Pairs with: ../../Z_RPi_Cam/homelab-selfhosting.sh

set -uo pipefail

QUIET=0
[ "${1:-}" = "--quiet" ] && QUIET=1

# Color codes (disabled if not a tty)
if [ -t 1 ]; then
    G='\033[32m'; R='\033[31m'; Y='\033[33m'; B='\033[1m'; N='\033[0m'
else
    G=''; R=''; Y=''; B=''; N=''
fi

PASS=0
FAIL=0
WARN=0
FAILED_ITEMS=()

ok()    { PASS=$((PASS+1)); [ "$QUIET" -eq 0 ] && printf "${G}✓${N} %s\n" "$1"; }
fail()  { FAIL=$((FAIL+1)); FAILED_ITEMS+=("$1"); printf "${R}✗${N} %s\n" "$1"; [ -n "${2:-}" ] && printf "  ${R}→${N} %s\n" "$2"; }
warn()  { WARN=$((WARN+1)); printf "${Y}!${N} %s\n" "$1"; [ -n "${2:-}" ] && printf "  ${Y}→${N} %s\n" "$2"; }
section() { [ "$QUIET" -eq 0 ] && printf "\n${B}== %s ==${N}\n" "$1"; }

require_root() {
    if [ "$(id -u)" != "0" ]; then
        echo "Some checks need root (reading sshd_config, fail2ban-client, etc.). Re-run with sudo." >&2
        exit 2
    fi
}

cmd_exists() { command -v "$1" >/dev/null 2>&1; }

# --- 1. unattended-upgrades ---
section "Auto-updates"
if dpkg -l 2>/dev/null | grep -q '^ii  unattended-upgrades'; then
    ok "unattended-upgrades installed"
else
    fail "unattended-upgrades NOT installed" "apt-get install unattended-upgrades"
fi

# --- 2. UFW ---
section "Firewall (UFW)"
if cmd_exists ufw; then
    if ufw status 2>/dev/null | grep -q 'Status: active'; then
        ok "UFW active"
        if ufw status 2>/dev/null | grep -qE '^22(/tcp)?\s+ALLOW'; then
            ok "UFW allows SSH (22/tcp)"
        else
            fail "UFW does not explicitly allow 22/tcp" "ufw allow 22/tcp"
        fi
        default_in=$(ufw status verbose 2>/dev/null | grep -i 'Default:' | head -1)
        if echo "$default_in" | grep -qi 'deny (incoming)'; then
            ok "UFW default-deny incoming"
        else
            fail "UFW default-deny incoming NOT set" "ufw default deny incoming"
        fi
    else
        fail "UFW installed but inactive" "ufw enable"
    fi
else
    fail "UFW not installed"
fi

# --- 3. fail2ban ---
section "fail2ban"
if cmd_exists fail2ban-client; then
    if systemctl is-active --quiet fail2ban; then
        ok "fail2ban service active"
        if fail2ban-client status sshd >/dev/null 2>&1; then
            ok "fail2ban sshd jail enabled"
        else
            fail "fail2ban sshd jail not enabled" "Check /etc/fail2ban/jail.d/sshd.local"
        fi
    else
        fail "fail2ban installed but not running" "systemctl enable --now fail2ban"
    fi
else
    fail "fail2ban not installed"
fi

# --- 4. SSH hardening ---
section "SSH config"
SSHD=/etc/ssh/sshd_config
if [ -r "$SSHD" ]; then
    sshd_get() {
        # Effective config: last uncommented match wins; sshd -T is best
        if cmd_exists sshd; then
            sshd -T 2>/dev/null | awk -v k="$1" 'tolower($1)==tolower(k){print $2; exit}'
        else
            grep -iE "^\s*$1\s+" "$SSHD" | tail -1 | awk '{print $2}'
        fi
    }

    [ "$(sshd_get PermitRootLogin)" = "no" ] && ok "PermitRootLogin no" || fail "PermitRootLogin != no" "sshd_get returned: $(sshd_get PermitRootLogin)"
    [ "$(sshd_get PubkeyAuthentication)" = "yes" ] && ok "PubkeyAuthentication yes" || fail "PubkeyAuthentication != yes"
    [ "$(sshd_get X11Forwarding)" = "no" ] && ok "X11Forwarding no" || fail "X11Forwarding != no"

    pwauth=$(sshd_get PasswordAuthentication)
    if [ "$pwauth" = "no" ]; then
        ok "PasswordAuthentication no"
    else
        target_user="${SUDO_USER:-jalcocert}"
        if [ -s "/home/${target_user}/.ssh/authorized_keys" ]; then
            warn "PasswordAuthentication still 'yes' but keys exist for $target_user" "Safe to disable: edit $SSHD"
        else
            warn "PasswordAuthentication 'yes' (no keys yet for $target_user — lockout risk if disabled)"
        fi
    fi
else
    fail "Cannot read $SSHD (need root?)"
fi

# --- 5. Kernel sysctl ---
section "Kernel sysctl"
SYSCTL_FILE=/etc/sysctl.d/99-hardening.conf
if [ -f "$SYSCTL_FILE" ]; then
    ok "$SYSCTL_FILE exists"
else
    fail "$SYSCTL_FILE missing" "Re-run harden_sysctl"
fi

check_sysctl() {
    local key="$1" expected="$2"
    local actual
    actual=$(sysctl -n "$key" 2>/dev/null || echo "?")
    if [ "$actual" = "$expected" ]; then
        ok "$key = $expected"
    else
        fail "$key = $actual (expected $expected)"
    fi
}

check_sysctl net.ipv4.conf.all.send_redirects 0
check_sysctl net.ipv4.conf.all.secure_redirects 0
check_sysctl net.ipv4.conf.all.accept_redirects 0
check_sysctl net.ipv4.conf.all.rp_filter 1
check_sysctl net.ipv4.conf.all.accept_source_route 0
check_sysctl net.ipv4.tcp_syncookies 1
check_sysctl kernel.kptr_restrict 2
check_sysctl kernel.dmesg_restrict 1
check_sysctl kernel.yama.ptrace_scope 2
check_sysctl kernel.sysrq 0

# --- 6. /tmp hardening ---
section "/tmp mount options"
tmp_opts=$(findmnt -no OPTIONS /tmp 2>/dev/null || echo "")
if [ -n "$tmp_opts" ]; then
    for opt in nosuid nodev noexec; do
        if echo ",$tmp_opts," | grep -q ",$opt,"; then
            ok "/tmp has $opt"
        else
            fail "/tmp missing $opt" "Current: $tmp_opts"
        fi
    done
else
    fail "/tmp not a separate mount"
fi

# --- 7. journald size cap ---
section "journald"
if grep -qE '^\s*SystemMaxUse=' /etc/systemd/journald.conf 2>/dev/null; then
    val=$(grep -E '^\s*SystemMaxUse=' /etc/systemd/journald.conf | tail -1 | cut -d= -f2)
    ok "journald SystemMaxUse=$val"
else
    fail "journald SystemMaxUse not set" "Edit /etc/systemd/journald.conf"
fi

# --- 8. logrotate ---
section "logrotate"
if cmd_exists logrotate; then
    ok "logrotate installed"
else
    fail "logrotate not installed"
fi

# --- 9. Docker logs cap ---
section "Docker daemon.json"
DAEMON_JSON=/etc/docker/daemon.json
if cmd_exists docker; then
    if [ -f "$DAEMON_JSON" ]; then
        ok "$DAEMON_JSON exists"

        check_json_key() {
            local key="$1" expected="$2"
            if cmd_exists jq; then
                actual=$(jq -r "$key // \"missing\"" "$DAEMON_JSON" 2>/dev/null)
                if [ "$actual" = "$expected" ]; then
                    ok "daemon.json $key = $expected"
                else
                    fail "daemon.json $key = $actual (expected $expected)"
                fi
            else
                grep -q "$expected" "$DAEMON_JSON" && ok "daemon.json contains $expected (no jq for precise check)" || fail "daemon.json missing $expected"
            fi
        }

        check_json_key '."log-driver"' "json-file"
        check_json_key '."log-opts"."max-size"' "10m"
        check_json_key '."log-opts"."max-file"' "3"
        check_json_key '."live-restore"' "true"
        check_json_key '."no-new-privileges"' "true"
        check_json_key '."icc"' "false"
        check_json_key '."userns-remap"' "default"
    else
        fail "$DAEMON_JSON missing" "Re-run harden_docker_logs / harden_docker_isolation"
    fi
else
    warn "Docker not installed — skipping daemon.json checks"
fi

# --- 10. cron restricted ---
section "cron"
if [ -f /etc/cron.allow ]; then
    ok "/etc/cron.allow exists ($(wc -l < /etc/cron.allow) entries)"
else
    fail "/etc/cron.allow missing"
fi

# --- 11. pwquality ---
section "Password quality"
if dpkg -l 2>/dev/null | grep -q '^ii  libpam-pwquality'; then
    ok "libpam-pwquality installed"
    if grep -qE '^\s*minlen\s*=\s*1[2-9]' /etc/security/pwquality.conf 2>/dev/null; then
        ok "pwquality minlen >= 12"
    else
        warn "pwquality minlen not set or < 12"
    fi
else
    fail "libpam-pwquality not installed"
fi

# --- 12. auditd ---
section "auditd"
if cmd_exists auditctl && systemctl is-active --quiet auditd; then
    ok "auditd active"
else
    fail "auditd not active" "apt-get install auditd && systemctl enable --now auditd"
fi

# --- 13. Bluetooth ---
section "Bluetooth (RPi)"
bt_disabled=0
for cfg in /boot/firmware/config.txt /boot/config.txt; do
    if [ -f "$cfg" ] && grep -q '^dtoverlay=disable-bt' "$cfg"; then
        ok "Bluetooth overlay disabled in $cfg"
        bt_disabled=1
        break
    fi
done
if [ "$bt_disabled" -eq 0 ]; then
    warn "Bluetooth overlay not disabled (optional)"
fi

if systemctl list-unit-files 2>/dev/null | grep -q '^bluetooth.service'; then
    if systemctl is-enabled bluetooth.service 2>/dev/null | grep -q 'disabled\|masked'; then
        ok "bluetooth.service disabled"
    else
        warn "bluetooth.service still enabled"
    fi
fi

# --- 14. Tailscale (optional) ---
section "Tailscale (optional)"
if cmd_exists tailscale; then
    ok "Tailscale installed"
    if tailscale status >/dev/null 2>&1; then
        ip=$(tailscale ip -4 2>/dev/null | head -1)
        ok "Tailscale up — IP: $ip"
    else
        warn "Tailscale installed but not connected" "Run: tailscale up"
    fi
else
    warn "Tailscale not installed (optional)"
fi

# --- Summary ---
printf "\n${B}== Summary ==${N}\n"
printf "${G}Pass:${N} %d   ${R}Fail:${N} %d   ${Y}Warn:${N} %d\n" "$PASS" "$FAIL" "$WARN"

if [ "$FAIL" -gt 0 ]; then
    printf "\n${R}Failed checks:${N}\n"
    for item in "${FAILED_ITEMS[@]}"; do
        printf "  - %s\n" "$item"
    done
    printf "\nRun ${B}homelab-selfhosting.sh${N} hardening section to fix.\n"
    exit "$FAIL"
fi

printf "\n${G}All hardening checks passed.${N}\n"
exit 0
