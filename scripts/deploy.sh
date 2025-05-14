#!/bin/bash
set -euo pipefail

APP_DIR="/opt/ekg-assistant"
REPO_URL="git@github.com:Rokossovskii/ekg-assistant.git"

echo ">>> DEPLOY STARTED at $(date)"

if ! command -v ufw >/dev/null 2>&1; then
  echo ">>> Installing ufw (firewall)"
  sudo apt-get update && sudo apt-get install -y ufw
fi

echo ">>> Ensuring firewall allows HTTP/HTTPS"
sudo ufw allow 80/tcp || true
sudo ufw allow 443/tcp || true
sudo ufw allow OpenSSH || true

if [[ "$(sudo ufw status | grep -c 'Status: active')" -eq 0 ]]; then
  echo ">>> Enabling firewall"
  sudo ufw --force enable
fi

if [ ! -d "$APP_DIR" ]; then
  echo ">>> Creating application directory"
  mkdir -p "$APP_DIR"
fi

cd "$APP_DIR"

if [ ! -d ".git" ]; then
  echo ">>> Cloning repository for the first time"
  git clone "$REPO_URL" .
else
  echo ">>> Pulling latest changes"
  git pull origin master
fi

echo ">>> Cleaning up Docker"
docker system prune -f || true

echo ">>> Stopping previous containers (if any)"
docker compose down || true

echo ">>> Building Docker images"
docker compose build --no-cache

echo ">>> Starting application"
docker compose up -d

echo "DEPLOY COMPLETED at $(date)"
