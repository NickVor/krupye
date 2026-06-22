#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/telegram-group-assistant}"
SERVICE_NAME="${SERVICE_NAME:-telegram-group-assistant}"

if [ ! -f "$APP_DIR/.env" ]; then
  echo "Missing $APP_DIR/.env"
  exit 1
fi

set -a
. "$APP_DIR/.env"
set +a

echo "== service =="
systemctl is-active "$SERVICE_NAME" || true
systemctl is-active caddy || true

echo
echo "== local web =="
curl -fsS "http://127.0.0.1:${PORT:-8000}/health"
echo

echo
echo "== public web =="
curl -fsS --max-time 20 "${PUBLIC_BASE_URL}/health"
echo

echo
echo "== telegram api =="
curl -fsS --max-time 20 "https://api.telegram.org/bot${BOT_TOKEN}/getMe" | python3 -m json.tool

echo
echo "== recent bot logs =="
journalctl -u "$SERVICE_NAME" -n 40 --no-pager
