#!/usr/bin/env bash
# Roll back the application to the previously recorded release.
# Called by the Manual Rollback GitHub Actions workflow, or directly via SSH.
# Usage: rollback.sh
set -euo pipefail

APP_DIR=/opt/ecommerce-poc
CURRENT_LINK=$APP_DIR/current
PREV_FILE=$APP_DIR/.previous_release

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

log "=== Starting rollback ==="

if [ ! -f "$PREV_FILE" ]; then
  log "ERROR: No rollback target found ($PREV_FILE does not exist)."
  log "This means either the application was never deployed, or a previous"
  log "rollback already consumed the only saved release pointer."
  exit 1
fi

PREV=$(cat "$PREV_FILE")

if [ ! -d "$PREV" ]; then
  log "ERROR: Previous release directory no longer exists: $PREV"
  log "It may have been pruned. List available releases:"
  ls "$APP_DIR/releases/" 2>/dev/null || echo "  (no releases found)"
  exit 1
fi

CURRENT=$(readlink -f "$CURRENT_LINK" 2>/dev/null || echo "none")
log "Active release   : $(basename "$CURRENT")"
log "Rolling back to  : $(basename "$PREV")"

# Swap symlink and restart
ln -sfn "$PREV" "$CURRENT_LINK"
sudo systemctl restart ecommerce-poc

sleep 3
if systemctl is-active --quiet ecommerce-poc; then
  log "=== Rollback successful. Service is running. ==="
else
  log "ERROR: Service did not start after rollback."
  log "Check logs: journalctl -u ecommerce-poc -n 50 --no-pager"
  exit 1
fi
