# Agentic Pi

Running agentic CLIs on a Raspberry Pi.

## Phase 1 — Verify hardening

Before installing agents, confirm the Pi is hardened.

Pairs with `../../Z_RPi_Cam/homelab-selfhosting.sh`.

```bash
#git clone https://github.com/JAlcocerT/RPi
sudo ./check-hardening.sh           # full report
sudo ./check-hardening.sh --quiet   # only failures + summary
```

Read-only audit. 

Exit code = number of failed checks (0 = all good).

Covers: unattended-upgrades, UFW, fail2ban, SSH config, kernel sysctl, /tmp opts, journald cap, logrotate, Docker daemon.json (logs + isolation flags), cron.allow, pwquality, auditd, Bluetooth overlay, Tailscale.

## Phase 2 — Agent install (planned)

- [ ] Codex CLI
- [ ] Other agentic CLIs (TBD)

Each agent install should be gated on `check-hardening.sh` passing.
