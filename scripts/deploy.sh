#!/bin/bash
set -euo pipefail

APP_DIR="/opt/ekg-assistant"
REPO_URL="git@github.com:Rokossovskii/ekg-assistant.git"

echo ">>> DEPLOY STARTED at $(date)"

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
  git pull origin main
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
