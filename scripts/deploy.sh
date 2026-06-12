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

# ── 0. Pre-flight: verify Python 3.12 ────────────────────────────────────────
# Must use Python 3.12 to match CI and ensure pydantic-core pre-built wheels
# are available. Python 3.14 (Ubuntu 26.04 default) has no pydantic-core wheel
# and source compilation requires Rust which is not installed on the server.
PYTHON=$(command -v python3.12 2>/dev/null || true)
if [ -z "$PYTHON" ]; then
  log "ERROR: python3.12 not found."
  log "Bootstrap should have installed it via: apt-get install python3.12 python3.12-venv"
  exit 1
fi
log "Using Python: $($PYTHON --version)"

# ── 1. Python virtual environment and dependencies ───────────────────────────
log "Creating virtual environment..."
"$PYTHON" -m venv "$RELEASE_DIR/.venv"

log "Installing dependencies..."
"$RELEASE_DIR/.venv/bin/pip" install --upgrade pip setuptools wheel --quiet
"$RELEASE_DIR/.venv/bin/pip" install --prefer-binary -r "$RELEASE_DIR/requirements.txt" --quiet

# ── 2. Shared configuration (.env) ───────────────────────────────────────────
SHARED_ENV="$APP_DIR/shared/.env"
if [ -f "$SHARED_ENV" ]; then
  cp "$SHARED_ENV" "$RELEASE_DIR/.env"
  log "Shared .env applied."
fi

# ── 3. Install / update systemd service ──────────────────────────────────────
log "Installing systemd service..."
sudo cp "$RELEASE_DIR/config/ecommerce-poc.service" /etc/systemd/system/ecommerce-poc.service
sudo systemctl daemon-reload
sudo systemctl enable ecommerce-poc --quiet
log "Service installed and enabled."

# ── 4. Install / update Nginx config ─────────────────────────────────────────
log "Configuring Nginx..."
sudo cp "$RELEASE_DIR/config/nginx.conf" /etc/nginx/sites-available/ecommerce-poc
sudo ln -sf /etc/nginx/sites-available/ecommerce-poc /etc/nginx/sites-enabled/ecommerce-poc
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable nginx --quiet
sudo systemctl reload nginx 2>/dev/null || sudo systemctl start nginx
log "Nginx configured."

# ── 5. Record current release as the rollback target ─────────────────────────
if [ -L "$CURRENT_LINK" ]; then
  PREVIOUS=$(readlink "$CURRENT_LINK")
  echo "$PREVIOUS" > "$APP_DIR/.previous_release"
  log "Previous release saved for rollback: $(basename "$PREVIOUS")"
fi

# ── 6. Promote new release (atomic symlink swap) ─────────────────────────────
log "Switching symlink to new release..."
ln -sfn "$RELEASE_DIR" "$CURRENT_LINK"

# ── 7. Publish scripts to stable path (required by rollback.yml workflow) ────
cp "$RELEASE_DIR/scripts/"*.sh "$APP_DIR/scripts/"
chmod +x "$APP_DIR/scripts/"*.sh

# ── 8. Restart application service ───────────────────────────────────────────
log "Restarting ecommerce-poc service..."
sudo systemctl restart ecommerce-poc

# ── 9. Confirm service is active ─────────────────────────────────────────────
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

# ── 10. Prune old releases (keep KEEP_RELEASES most recent) ──────────────────
log "Pruning old releases (keeping last $KEEP_RELEASES)..."
ls -dt "$RELEASES_DIR"/*/ 2>/dev/null \
  | tail -n "+$((KEEP_RELEASES + 1))" \
  | xargs -r rm -rf

log "=== Deployment complete: $RELEASE ==="
