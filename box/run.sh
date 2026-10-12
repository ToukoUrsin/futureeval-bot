#!/usr/bin/env bash
# Run toukobot once on touko-agents (systemd user timer toukobot.timer).
# Models via the box CLIProxyAPI pool; Metaculus token from hsec. One process at
# a time (flock), hard 25 min cap, low priority. Logs: $LOG_DIR/<UTC stamp>-<mode>.log
set -euo pipefail
MODE="${1:-tournament}"
BOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="${LOG_DIR:-/data/tracks/metaculus-bot/live/logs}"
mkdir -p "$LOG_DIR"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
[ -e "$BOT_DIR/PAUSED" ] && { echo "PAUSED file present; skipping"; exit 0; }
LLM_PROXY_KEY="$(. "$HOME/cliproxy/keys.env"; printf %s "$CPA_API_KEY")"
export LLM_PROXY_KEY LLM_PROXY_BASE="http://127.0.0.1:8317"
find "$LOG_DIR" -name "*.log" -mtime +14 -delete
LOG="$LOG_DIR/$(date -u +%Y%m%dT%H%M%SZ)-$MODE.log"
cd "$BOT_DIR"
exec flock -n /tmp/toukobot.lock nice -n 10 timeout 25m \
  hsec exec --only METACULUS_TOKEN -- .venv/bin/python main.py --mode "$MODE" >"$LOG" 2>&1
