# Agentic Pi

Running agentic CLIs on a Raspberry Pi.

## Phase 1 — Verify hardening

Before installing agents, confirm the Pi is hardened.

Pairs with `../../Z_RPi_Cam/homelab-selfhosting.sh`.

```bash
#git clone https://github.com/JAlcocerT/RPi
#cd ./RPi/Z_SelfHosting/agentic-pi
#chmod +x check-hardening.sh install-agents.sh
#sudo ./check-hardening.sh                        
#Or run via interpreter without chmod:
sudo bash check-hardening.sh # full report
sudo ./check-hardening.sh --quiet   # only failures + summary
```

Read-only audit. 

Exit code = number of failed checks (0 = all good).

Covers: unattended-upgrades, UFW, fail2ban, SSH config, kernel sysctl, /tmp opts, journald cap, logrotate, Docker daemon.json (logs + isolation flags), cron.allow, pwquality, auditd, Bluetooth overlay, Tailscale.

## Phase 2 — Agent install

```bash
sudo ./install-agents.sh                # runs hardening check first
sudo ./install-agents.sh --skip-check   # bypass hardening pre-check
```

Flow:

1. Runs `check-hardening.sh --quiet` (gate). Bypass with `--skip-check`.
2. Shows responsibility warning. Requires explicit `yes` consent — anything else aborts.
3. Checks Node.js >= 20. Installs `setup_22.x` from NodeSource if missing/old.
4. Prompts yes/no for each agent:

   | Label | Source | Package / Image | Binary |
   |---|---|---|---|
   | OpenCode AI | npm | `opencode-ai` | `opencode` |
   | Google Gemini CLI | npm | `@google/gemini-cli` | `gemini` |
   | Claude Code | npm | `@anthropic-ai/claude-code` | `claude` |
   | OpenAI Codex | npm | `@openai/codex` | `codex` |
   | Hermes Agent | Docker | `nousresearch/hermes-agent` | container |

   Hermes requires Docker (install via `homelab-selfhosting.sh`).
   State persists in `~/.hermes` (mounted at `/opt/data` inside container).

5. Already-installed agents prompt before reinstalling.
6. Prints summary (installed / skipped / failed) + version dump.

Exit code = 0 if no failures.

### After install

Each CLI needs API keys via env vars:

```bash
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
export GEMINI_API_KEY=...
```

Add to `~/.bashrc` or use a secret manager (`pass`, `gopass`, `age`).