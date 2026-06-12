# Deployment Guide

## Architecture

```
Developer pushes to main
        │
        ▼
┌───────────────────┐
│  GitHub Actions   │  CI: pytest → CD: rsync + deploy.sh
└────────┬──────────┘
         │ SSH / rsync
         ▼
┌───────────────────┐
│   AWS EC2 (Ubuntu)│
│                   │
│  Nginx :80        │  Reverse proxy
│    └─► Uvicorn    │  FastAPI app on port 8000
│         └─► app   │  /opt/ecommerce-poc/current/
└───────────────────┘
```

**Release directory layout on EC2:**

```
/opt/ecommerce-poc/
├── releases/
│   ├── 20240612_120000_abc123ef/   ← older release
│   └── 20240612_130000_def456gh/   ← newest release
├── current -> releases/20240612_130000_def456gh   (symlink)
├── scripts/
│   ├── deploy.sh    (copy of latest; stable path for rollback workflow)
│   └── rollback.sh
├── shared/
│   └── .env         (environment variables, never committed to git)
└── .previous_release  (path of the release before current; used for rollback)
```

---

## Required GitHub Secrets

Navigate to **GitHub repo → Settings → Secrets and variables → Actions → New repository secret**
and add each of the following:

| Secret name            | Description                                                   | Example value              |
|------------------------|---------------------------------------------------------------|----------------------------|
| `EC2_HOST`             | Public IPv4 address or domain name of your EC2 instance       | `54.123.45.67`             |
| `EC2_USERNAME`         | SSH login user on EC2 (Ubuntu AMI default is `ubuntu`)        | `ubuntu`                   |
| `EC2_SSH_PRIVATE_KEY`  | Full content of the `.pem` key file used to SSH into EC2      | *(see note below)*         |

### How to get `EC2_SSH_PRIVATE_KEY`

On your local machine, open the `.pem` file you downloaded when creating the EC2 key pair and paste the **entire contents** (including the header and footer lines) into the secret value field:

```
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA...
...
-----END RSA PRIVATE KEY-----
```

---

## GitHub Environment Setup

Create a **production** environment to gate deployments:

1. Go to **Settings → Environments → New environment**
2. Name it `production`
3. (Optional) Add **Required reviewers** to enforce manual approval before deploys
4. (Optional) Add a **Deployment branch rule** to allow only `main`

---

## One-Time EC2 Server Setup

SSH into your EC2 instance and run the following commands once before the first deployment.

### 1. System packages

```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y nginx rsync curl

# Python 3.12 (not available in Ubuntu 22.04 default repos)
sudo add-apt-repository ppa:deadsnakes/python -y
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev
```

### 2. Application directories

```bash
sudo mkdir -p /opt/ecommerce-poc/{releases,shared,scripts}
sudo chown -R ubuntu:ubuntu /opt/ecommerce-poc
```

### 3. Shared environment file

Create the `.env` file that will be copied into every release:

```bash
cat > /opt/ecommerce-poc/shared/.env << 'EOF'
# Add any environment-specific config here.
# This file is never committed to git.
# LOG_LEVEL=INFO
EOF
```

### 4. Systemd service

```bash
# Copy the service file from the project (or create it manually)
sudo cp /opt/ecommerce-poc/releases/<first_release>/config/ecommerce-poc.service \
        /etc/systemd/system/ecommerce-poc.service

sudo systemctl daemon-reload
sudo systemctl enable ecommerce-poc
```

> **Note:** The first release must be deployed manually (or via CI) before this step.
> Alternatively, create the service file manually from `config/ecommerce-poc.service` in this repo.

### 5. Passwordless sudo for systemctl (required by deploy/rollback scripts)

```bash
sudo visudo -f /etc/sudoers.d/ecommerce-poc
```

Add these lines:

```
ubuntu ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart ecommerce-poc
ubuntu ALL=(ALL) NOPASSWD: /usr/bin/systemctl start ecommerce-poc
ubuntu ALL=(ALL) NOPASSWD: /usr/bin/systemctl stop ecommerce-poc
```

### 6. Nginx

```bash
# Copy the Nginx config from the project
sudo cp /opt/ecommerce-poc/releases/<first_release>/config/nginx.conf \
        /etc/nginx/sites-available/ecommerce-poc

# (Optional) Edit server_name if you have a domain
sudo nano /etc/nginx/sites-available/ecommerce-poc

# Enable the site
sudo ln -s /etc/nginx/sites-available/ecommerce-poc \
           /etc/nginx/sites-enabled/ecommerce-poc

# Remove the default Nginx site if present
sudo rm -f /etc/nginx/sites-enabled/default

# Validate and reload
sudo nginx -t && sudo systemctl reload nginx
```

### 7. EC2 Security Group rules

In the AWS Console, ensure the EC2 instance's Security Group allows:

| Type  | Protocol | Port | Source    |
|-------|----------|------|-----------|
| SSH   | TCP      | 22   | Your IP   |
| HTTP  | TCP      | 80   | 0.0.0.0/0 |
| HTTPS | TCP      | 443  | 0.0.0.0/0 |

Port `8000` does **not** need to be open externally — Nginx proxies traffic from port 80.

---

## First Deployment

The easiest way to do the first deployment is to push a commit to `main` after adding the
GitHub Secrets. GitHub Actions will handle the rest. The `ecommerce-poc.service` systemd unit
and Nginx site need to exist before the first deploy, so either:

**Option A — install service file before first deploy (recommended):**

```bash
# On EC2, create the service file manually from the repo contents
sudo nano /etc/systemd/system/ecommerce-poc.service
# Paste contents of config/ecommerce-poc.service, then:
sudo systemctl daemon-reload
sudo systemctl enable ecommerce-poc
```

**Option B — manual first deploy:**

```bash
# From your local machine
rsync -az --exclude='.git/' --exclude='.venv/' --exclude='**/__pycache__/' \
  ./ ubuntu@<EC2_HOST>:/opt/ecommerce-poc/releases/initial/

ssh ubuntu@<EC2_HOST> "bash /opt/ecommerce-poc/releases/initial/scripts/deploy.sh initial"
```

---

## CI/CD Pipeline Overview

| Trigger            | Jobs that run         | Outcome                              |
|--------------------|-----------------------|--------------------------------------|
| Push to any branch | `test`                | Tests run; no deployment             |
| Open a PR          | `test`                | Tests run; blocks merge if failing   |
| Push to `main`     | `test` → `deploy`     | Deploy only if tests pass            |
| Workflow dispatch  | `rollback` (manual)   | Roll back production to prior release|

### Deploy job steps

1. Checkout code on the GitHub Actions runner
2. Set execute permissions on `scripts/*.sh`
3. Authenticate via SSH (ephemeral key, cleaned up after job)
4. Generate a unique release name: `YYYYMMDD_HHMMSS_<short-sha>`
5. `rsync` source files to `/opt/ecommerce-poc/releases/<release>/`
6. Call `scripts/deploy.sh <release>` over SSH which:
   - Creates a Python 3.12 venv and installs `requirements.txt`
   - Copies `shared/.env` into the release
   - Records the current release as the rollback target
   - Atomically swaps the `current` symlink to the new release
   - Copies `scripts/*.sh` to a stable `/opt/ecommerce-poc/scripts/` path
   - Restarts the `ecommerce-poc` systemd service
   - Waits up to 20 s for the service to become active
   - Prunes all but the 5 most recent releases
7. Polls `GET /health` (up to 6 times over 30 s) for HTTP 200
8. On any failure → automatically rolls back to the previous release

---

## Rollback Procedures

### Automatic rollback (CI/CD)

The deploy job rolls back automatically if the health check fails. No action required.

### Manual rollback via GitHub Actions (recommended for human-initiated rollback)

1. Go to **Actions → Manual Rollback → Run workflow**
2. Fill in a reason and click **Run workflow**
3. The workflow SSH-es into EC2 and runs `scripts/rollback.sh`, which:
   - Reads `/opt/ecommerce-poc/.previous_release`
   - Swaps the `current` symlink back to the previous release
   - Restarts the service
   - Exits non-zero if the service doesn't come back up

### Manual rollback via SSH

```bash
ssh ubuntu@<EC2_HOST> "bash /opt/ecommerce-poc/scripts/rollback.sh"
```

### Rollback to a specific release

```bash
ssh ubuntu@<EC2_HOST>
# List available releases
ls -lt /opt/ecommerce-poc/releases/

# Switch to a specific release
ln -sfn /opt/ecommerce-poc/releases/<release_name> /opt/ecommerce-poc/current
sudo systemctl restart ecommerce-poc
```

### Rollback limitations

- Only one level of automatic rollback is stored (the release immediately before `current`)
- Releases older than the last 5 are pruned by `deploy.sh`
- If the previous release directory was pruned, use **Rollback to a specific release** above

---

## Monitoring & Logs

### Application logs (via journald)

```bash
# Live tail
journalctl -u ecommerce-poc -f

# Last 100 lines
journalctl -u ecommerce-poc -n 100 --no-pager

# Logs since last boot
journalctl -u ecommerce-poc -b
```

### Nginx access and error logs

```bash
sudo tail -f /var/log/nginx/ecommerce-poc.access.log
sudo tail -f /var/log/nginx/ecommerce-poc.error.log
```

### Service status

```bash
systemctl status ecommerce-poc

# Quick active check
systemctl is-active ecommerce-poc
```

### Health endpoint

```bash
# From EC2 (local)
curl http://localhost:8000/health

# From outside (via Nginx)
curl http://<EC2_HOST>/health
```

### API docs

```
http://<EC2_HOST>/docs       ← Swagger UI
http://<EC2_HOST>/redoc      ← ReDoc
```

---

## Troubleshooting

### Service fails to start after deploy

```bash
journalctl -u ecommerce-poc -n 50 --no-pager
```

Common causes:
- Port 8000 already in use: `sudo lsof -i :8000`
- Missing Python 3.12: `python3.12 --version`
- Broken `requirements.txt` install: check deploy log output

### rsync permission denied

Ensure the deploy user owns the app directory:

```bash
sudo chown -R ubuntu:ubuntu /opt/ecommerce-poc
```

### sudo systemctl requires password

Verify the sudoers entry:

```bash
sudo visudo -f /etc/sudoers.d/ecommerce-poc
# Should contain the NOPASSWD lines from the setup section above
```

### SSH host key verification fails in CI

The `ssh-keyscan` step in the workflow populates `known_hosts` at run time.
If the EC2 instance was replaced (new host key), delete the `EC2_HOST` secret value
and re-add it — the next run will re-scan the new key.

### Health check passes locally but fails from CI

Ensure port 8000 is bound to `0.0.0.0` (not `127.0.0.1` only) in the service file,
**or** that the health check in the workflow SSHs in and queries `localhost` (which it does).

---

## Optional: HTTPS with Let's Encrypt

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
sudo systemctl reload nginx
```

Certbot will automatically modify `/etc/nginx/sites-available/ecommerce-poc` to add TLS
and set up auto-renewal via a systemd timer.
