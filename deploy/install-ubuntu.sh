#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/telegram-group-assistant"
APP_USER="assistant"
SERVICE_NAME="telegram-group-assistant"
PUBLIC_BASE_URL="${PUBLIC_BASE_URL:-}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root"
  exit 1
fi

if [ -z "${BOT_TOKEN:-}" ]; then
  echo "BOT_TOKEN is required"
  exit 1
fi

if [ -z "$PUBLIC_BASE_URL" ]; then
  echo "PUBLIC_BASE_URL is required"
  exit 1
fi

PUBLIC_HOST="$(printf '%s' "$PUBLIC_BASE_URL" | sed -E 's#^https?://##; s#/.*$##')"
if [ -z "$PUBLIC_HOST" ]; then
  echo "Cannot infer public host from PUBLIC_BASE_URL=${PUBLIC_BASE_URL}"
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt update
apt install -y python3 python3-venv python3-pip caddy rsync curl iproute2

if ! id "$APP_USER" >/dev/null 2>&1; then
  useradd --system --home "$APP_DIR" --shell /usr/sbin/nologin "$APP_USER"
fi

mkdir -p "$APP_DIR"
rsync -a --delete \
  --exclude ".git" \
  --exclude ".venv" \
  --exclude "__pycache__" \
  --exclude "*.pyc" \
  --exclude "*.sqlite3" \
  ./ "$APP_DIR/"
mkdir -p "$APP_DIR/data"

cat > "$APP_DIR/.env" <<EOF
BOT_TOKEN=${BOT_TOKEN}
PUBLIC_BASE_URL=${PUBLIC_BASE_URL}
OPENAI_API_KEY=${OPENAI_API_KEY:-}
OPENAI_BASE_URL=${OPENAI_BASE_URL:-}
ASSISTANT_MODEL=${ASSISTANT_MODEL:-gpt-4.1-mini}
DATABASE_PATH=${APP_DIR}/data/assistant.sqlite3
HOST=127.0.0.1
PORT=8000
LOG_LEVEL=info
EOF

python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/python" -m pip install --upgrade pip
"$APP_DIR/.venv/bin/python" -m pip install -r "$APP_DIR/requirements.txt"

cp "$APP_DIR/deploy/assistant.service" "/etc/systemd/system/${SERVICE_NAME}.service"

echo "Checking web ports before Caddy start..."
if ss -ltnp | grep -E ':(80|443)\s' | grep -v caddy; then
  echo
  echo "Port 80 or 443 is already occupied. Telegram Web Apps need public HTTPS."
  echo "Stop or reconfigure the service above, then rerun this installer."
  exit 1
fi

cat > /etc/caddy/Caddyfile <<EOF
${PUBLIC_HOST} {
    reverse_proxy 127.0.0.1:8000
}
EOF

chown -R "$APP_USER:$APP_USER" "$APP_DIR"
caddy fmt --overwrite /etc/caddy/Caddyfile

systemctl daemon-reload
systemctl enable --now "$SERVICE_NAME"
systemctl enable --now caddy
systemctl reload caddy

echo "Done"
echo "Web: ${PUBLIC_BASE_URL}"
echo "Status: systemctl status ${SERVICE_NAME}"
