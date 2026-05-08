# Homelab Hardening — Future Ideas

Backlog of features worth adding to `homelab-selfhosting.sh` beyond current scope (security-audit.md baseline + retry/logging merge).

## Container Isolation (Not Yet Implemented)

Current script runs containers as root-on-host. Docker root = host root if escape.

### Option A — userns-remap (recommended for fresh installs)

```bash
cat > /etc/docker/daemon.json <<'EOF'
{
  "userns-remap": "default",
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" },
  "live-restore": true,
  "no-new-privileges": true,
  "icc": false
}
EOF
systemctl restart docker
```

- Adds `dockremap` subuid/subgid mapping. Container UID 0 = unprivileged on host.
- **Caveat:** existing volumes need `chown` to remapped UID. Run on fresh setup only.
- `icc: false` disables inter-container communication on default bridge — force explicit `docker network create` per stack.
- `no-new-privileges` blocks setuid escalation inside containers.

### Option B — Docker rootless mode

- Per-user Docker daemon, no root at all.
- Limitations: no host network, no privileged ports without `setcap`, no AppArmor.
- Better for single-user homelab where containers don't need <1024 ports.

## Top 3 Quick Wins

1. **`daemon.json` log limits + flags**
   - Prevents SD card kill from runaway logs.
   - `live-restore` keeps containers up across Docker daemon restart.
   - Low risk, big win.

2. **`etckeeper`**
   ```bash
   apt-get install -y etckeeper
   ```
   - Auto git-tracks `/etc`. Every config change committed.
   - Diff-on-demand when something breaks.

3. **`chrony` (NTP)**
   ```bash
   apt-get install -y chrony
   systemctl enable --now chrony
   ```
   - RPi has no RTC. Clock drifts on reboot.
   - Wrong clock = broken TLS, expired tokens, jwt issues.

## Operations / Observability

| Feature | Why |
|---|---|
| Watchtower or Diun | Auto image updates / notifications |
| Node exporter + Prometheus + Grafana | Temp / load / disk monitoring (RPi throttles silently) |
| Loki + Promtail | Centralized log aggregation |
| `journalctl --vacuum-size=200M` cron | Log volume cap before SD fills |
| Smartmontools / `lm-sensors` | SD card health + thermal alerts |
| `iotop` / `iftop` / `ctop` | Live debugging when CPU pegs |
| `needrestart` | Flags services needing restart after upgrades |

## Backups

- `borg` or `restic` + `rclone` to B2 / S3 / WebDAV.
- Targets: `/var/lib/docker/volumes`, `/etc`, compose files, `/home`.
- Schedule via systemd timer, not cron.
- Test restore quarterly.

## Network Hardening

| Feature | Why |
|---|---|
| `docker network create` per stack | Lateral movement reduction |
| Caddy / Traefik bound to Tailscale iface only | TLS without LAN/WAN exposure |
| `tailscale serve` / `tailscale funnel` | HTTPS without reverse proxy boilerplate |
| MagicDNS only, no public DNS | Services discoverable inside tailnet only |

## Skipped From security-audit.md (Reason)

- **Reverse proxy / TLS** — service-specific, not script-friendly.
- **Read-only filesystem** — too disruptive for self-hosting box.
- **WiFi disable** — user may need it.
- **Investigate ports 111 / 8654** — runtime check, not install-time.

## Already Done

- zram swap (encrypted in-memory) — see audit.
- Sudoers NOPASSWD audit — clean.
- `/tmp` nosuid + nodev (script adds noexec).
