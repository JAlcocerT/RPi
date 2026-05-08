#!/bin/bash

# Install agentic CLIs on Raspberry Pi.
# Phase 2 of agentic-pi setup. Run check-hardening.sh first.
#
# Usage: sudo ./install-agents.sh
#        sudo ./install-agents.sh --skip-check   # skip hardening pre-check

set -euo pipefail

if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root (apt + npm -g need it)." >&2
    exit 1
fi


### Responsibility warning ###

cat <<'WARNING'

================================================================================
  WARNING — AGENTIC CLI INSTALL
================================================================================

You are about to install AI coding agents that can:

  - Read, modify, create, and DELETE files on this system
  - Execute shell commands (some agents auto-run commands without confirmation)
  - Send code, prompts, and file contents to third-party APIs
  - Incur API charges based on token usage

By proceeding, you acknowledge:

  1. You have read each agent's documentation and security model.
  2. You will use these tools ONLY in environments you own or are
     authorized to operate in.
  3. You accept full responsibility for any damage, data loss, leaked
     secrets, unwanted API charges, or other consequences resulting
     from agent actions.
  4. You will not run agents with elevated privileges (root) unless
     strictly necessary, and never against production systems without
     explicit approval.
  5. Neither this script nor its author provide any warranty.

================================================================================

WARNING

printf "Do you understand and agree? (yes/no): "
read -r consent
case $consent in
    [yY]|[yY][eE][sS])
        echo "Consent recorded. Proceeding..."
        ;;
    *)
        echo "Consent not given. Aborting."
        exit 1
        ;;
esac
echo ""


log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

prompt_yn() {
    # prompt_yn "question" -> returns 0 if yes
    local q="$1" ans
    while true; do
        printf "%s (yes/no): " "$q"
        read -r ans
        case $ans in
            [yY]|[yY][eE][sS]) return 0 ;;
            [nN]|[nN][oO])     return 1 ;;
            *) echo "Please answer yes or no." ;;
        esac
    done
}


### Pre-check: hardening ###

SKIP_CHECK=0
[ "${1:-}" = "--skip-check" ] && SKIP_CHECK=1

if [ "$SKIP_CHECK" -eq 0 ]; then
    if [ -x "$(dirname "$0")/check-hardening.sh" ]; then
        log "Running hardening pre-check..."
        if "$(dirname "$0")/check-hardening.sh" --quiet; then
            log "Hardening check passed."
        else
            log "Hardening check failed. Fix or re-run with --skip-check to bypass."
            exit 1
        fi
    else
        log "Warning: check-hardening.sh not found or not executable, skipping pre-check."
    fi
fi


### Node.js ###

NODE_MAJOR_REQUIRED=20  # most agents need >=20

install_node() {
    log "Installing Node.js via NodeSource (setup_22.x)..."
    apt-get update -qq
    apt-get install -y curl ca-certificates gnupg

    local max_retries=3
    local retry=0
    while [ "$retry" -lt "$max_retries" ]; do
        if curl -fsSL https://deb.nodesource.com/setup_22.x | bash -; then
            break
        fi
        retry=$((retry + 1))
        log "NodeSource setup attempt $retry/$max_retries failed, retrying..."
        sleep 5
    done

    apt-get install -y nodejs

    if ! command_exists node; then
        log "Error: Node.js installation failed"
        return 1
    fi
}

check_node() {
    if command_exists node; then
        local ver major
        ver=$(node --version)            # e.g. v22.5.1
        major=${ver#v}                   # 22.5.1
        major=${major%%.*}               # 22
        log "Node.js detected: $ver"
        if [ "$major" -ge "$NODE_MAJOR_REQUIRED" ]; then
            log "Node major $major >= $NODE_MAJOR_REQUIRED, OK"
            return 0
        fi
        log "Node $ver too old (need >= $NODE_MAJOR_REQUIRED). Reinstalling..."
        return 1
    fi
    log "Node.js not found."
    return 1
}

if ! check_node; then
    install_node
    check_node || { log "Error: Node.js still not usable"; exit 1; }
fi

if ! command_exists npm; then
    log "Error: npm missing after Node install"
    exit 1
fi

log "npm: $(npm --version)"


### Agent install helper ###

install_npm_global() {
    # install_npm_global <package> <command-name>
    local pkg="$1" bin="$2"

    if command_exists "$bin"; then
        log "$bin already installed: $($bin --version 2>/dev/null | head -1 || echo 'unknown version')"
        if ! prompt_yn "Reinstall $pkg anyway?"; then
            return 0
        fi
    fi

    log "Installing $pkg..."
    if npm install -g "$pkg"; then
        log "$pkg installed."
    else
        log "Error: failed to install $pkg"
        return 1
    fi
}


### Agent menu ###

INSTALLED=()
SKIPPED=()
FAILED=()

run_agent() {
    # run_agent <label> <pkg> <bin>
    local label="$1" pkg="$2" bin="$3"
    if prompt_yn "Install $label ($pkg)?"; then
        if install_npm_global "$pkg" "$bin"; then
            INSTALLED+=("$label")
        else
            FAILED+=("$label")
        fi
    else
        SKIPPED+=("$label")
    fi
}

log "Select which agentic CLIs to install:"
echo ""

run_agent "OpenCode AI"      "opencode-ai"             "opencode"
run_agent "Google Gemini CLI" "@google/gemini-cli"      "gemini"
run_agent "Claude Code"       "@anthropic-ai/claude-code" "claude"
run_agent "OpenAI Codex"      "@openai/codex"           "codex"


### Hermes (Docker-based) ###

install_hermes() {
    if ! command_exists docker; then
        log "Error: Docker not installed. Install Docker first (run homelab-selfhosting.sh)."
        return 1
    fi

    local target_user="${SUDO_USER:-$USER}"
    local home_dir
    home_dir=$(getent passwd "$target_user" | cut -d: -f6)
    local hermes_dir="${home_dir}/.hermes"

    log "Creating $hermes_dir..."
    mkdir -p "$hermes_dir"
    chown "$target_user:$target_user" "$hermes_dir"

    log "Pulling and running hermes-agent setup..."
    log "Note: 'setup' is interactive — follow prompts."
    docker run -it --rm \
        -v "${hermes_dir}:/opt/data" \
        nousresearch/hermes-agent setup
}

if prompt_yn "Install Hermes Agent (Nous Research, Docker-based)?"; then
    if install_hermes; then
        INSTALLED+=("Hermes Agent")
    else
        FAILED+=("Hermes Agent")
    fi
else
    SKIPPED+=("Hermes Agent")
fi


### Summary ###

echo ""
log "Agent install complete."
echo ""
echo "Installed:"
if [ "${#INSTALLED[@]}" -gt 0 ]; then
    for a in "${INSTALLED[@]}"; do echo "  ✓ $a"; done
else
    echo "  (none)"
fi

echo "Skipped:"
if [ "${#SKIPPED[@]}" -gt 0 ]; then
    for a in "${SKIPPED[@]}"; do echo "  - $a"; done
else
    echo "  (none)"
fi

if [ "${#FAILED[@]}" -gt 0 ]; then
    echo "Failed:"
    for a in "${FAILED[@]}"; do echo "  ✗ $a"; done
fi

echo ""
log "Versions installed:"
for bin in opencode gemini claude codex; do
    if command_exists "$bin"; then
        echo "  $bin: $($bin --version 2>/dev/null | head -1 || echo 'installed')"
    fi
done

echo ""
log "Next steps:"
log "  - Run each CLI with --help to see auth/config commands"
log "  - Most agents need API keys: export ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY"
log "  - Add keys to ~/.bashrc or use a secret manager (pass, gopass, age)"

[ "${#FAILED[@]}" -eq 0 ]
