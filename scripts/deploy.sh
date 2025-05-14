#!/bin/bash
set -euo pipefail

APP_DIR="/opt/ekg-assistant"
REPO_URL="git@github.com:Rokossovskii/ekg-assistant.git"
CERT_PATH="$APP_DIR/certbot/conf/live/ekg-assistant.rokosz.win/fullchain.pem"

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
  echo ">>> Checking for uncommitted changes"
  git fetch origin
  git reset --hard origin/master
fi

echo ">>> Cleaning up Docker"
docker system prune -f || true

echo ">>> Stopping previous containers (if any)"
docker compose down || true

echo ">>> Building Docker images"
docker compose build --no-cache

if [ ! -f "$CERT_PATH" ]; then
  echo ">>> No SSL certificate found – bootstrapping HTTPS"

  echo ">>> Using HTTP-only Nginx config"
  cp ./nginx/conf/80-only.conf ./nginx/conf/default.conf

  echo ">>> Starting Nginx only on HTTP"
  docker compose up -d nginx

  echo ">>> Waiting for Nginx to be ready..."
  sleep 5

  echo ">>> Requesting Let's Encrypt certificate"
  docker compose run --rm certbot

  echo ">>> Switching to HTTPS-enabled config"
  cp ./nginx/conf/80-and-443.conf ./nginx/conf/default.conf

  echo ">>> Restarting Nginx with full config"
  docker compose restart nginx
else
  echo ">>> SSL certificate found – using HTTPS config"
  cp ./nginx/conf/80-and-443.conf ./nginx/conf/default.conf
fi

echo ">>> Starting application"
docker compose up -d

echo "DEPLOY COMPLETED at $(date)"
