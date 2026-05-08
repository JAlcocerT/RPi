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
