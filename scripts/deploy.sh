#!/usr/bin/env bash
# Server-side deployment script.
# Called by GitHub Actions after rsyncing the release to the EC2 instance.
# Usage: deploy.sh <release_name>
set -euo pipefail

RELEASE=${1:?Usage: deploy.sh <release_name>}

APP_DIR=/opt/ecommerce-poc
RELEASES_DIR=$APP_DIR/releases
RELEASE_DIR=$RELEASES_DIR/$RELEASE
CURRENT_LINK=$APP_DIR/current
KEEP_RELEASES=5

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

log "=== Deploying release: $RELEASE ==="

# ── 0. Pre-flight checks ──────────────────────────────────────────────────────
PYTHON=$(command -v python3.12 2>/dev/null || true)
if [ -z "$PYTHON" ]; then
  log "ERROR: python3.12 not found. Run on EC2:"
  log "  sudo add-apt-repository ppa:deadsnakes/python -y"
  log "  sudo apt-get update && sudo apt-get install -y python3.12 python3.12-venv"
  exit 1
fi
log "Using Python: $($PYTHON --version)"

# ── 1. Python virtual environment and dependencies ───────────────────────────
log "Creating virtual environment..."
"$PYTHON" -m venv "$RELEASE_DIR/.venv"

log "Installing dependencies..."
"$RELEASE_DIR/.venv/bin/pip" install --upgrade pip --quiet
"$RELEASE_DIR/.venv/bin/pip" install -r "$RELEASE_DIR/requirements.txt" --quiet

# ── 2. Shared configuration (.env) ───────────────────────────────────────────
SHARED_ENV="$APP_DIR/shared/.env"
if [ -f "$SHARED_ENV" ]; then
  cp "$SHARED_ENV" "$RELEASE_DIR/.env"
  log "Shared .env applied from $SHARED_ENV"
else
  log "No shared .env found at $SHARED_ENV — skipping."
fi

# ── 3. Record current release as the rollback target ─────────────────────────
if [ -L "$CURRENT_LINK" ]; then
  PREVIOUS=$(readlink "$CURRENT_LINK")
  echo "$PREVIOUS" > "$APP_DIR/.previous_release"
  log "Previous release saved for rollback: $(basename "$PREVIOUS")"
fi

# ── 4. Promote new release (atomic symlink swap) ─────────────────────────────
log "Switching symlink to new release..."
ln -sfn "$RELEASE_DIR" "$CURRENT_LINK"

# ── 5. Publish scripts to stable path (required by rollback.yml workflow) ────
mkdir -p "$APP_DIR/scripts"
cp "$RELEASE_DIR/scripts/"*.sh "$APP_DIR/scripts/"
chmod +x "$APP_DIR/scripts/"*.sh

# ── 6. Restart application service ───────────────────────────────────────────
log "Restarting ecommerce-poc service..."
sudo systemctl restart ecommerce-poc

# ── 7. Confirm service is active ─────────────────────────────────────────────
RETRIES=0
until systemctl is-active --quiet ecommerce-poc || [ $RETRIES -ge 10 ]; do
  RETRIES=$((RETRIES + 1))
  log "Waiting for service to become active... ($RETRIES/10)"
  sleep 2
done

if ! systemctl is-active --quiet ecommerce-poc; then
  log "ERROR: Service did not start. Run: journalctl -u ecommerce-poc -n 50 --no-pager"
  exit 1
fi

# ── 8. Prune old releases (keep KEEP_RELEASES most recent) ───────────────────
log "Pruning old releases (keeping last $KEEP_RELEASES)..."
ls -dt "$RELEASES_DIR"/*/ 2>/dev/null \
  | tail -n "+$((KEEP_RELEASES + 1))" \
  | xargs -r rm -rf

log "=== Deployment complete: $RELEASE ==="
