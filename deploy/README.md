# VPS Deployment

This directory contains generic deployment files for running the Telegram assistant on an Ubuntu VPS.

Do not put real production domains, server IP addresses, provider names, account details, VPN panel details, tokens, passwords, or private keys in this public repository.

## Generic Production Shape

```text
your-domain.example:443 -> Caddy -> 127.0.0.1:8000 -> FastAPI + Telegram bot
                                                     -> LLM provider
                                                     -> SQLite
```

| Component | Example value |
| --- | --- |
| Public URL | `https://your-domain.example` |
| App directory | `/opt/telegram-group-assistant` |
| systemd service | `telegram-group-assistant` |
| Web App bind address | `127.0.0.1:8000` |
| HTTPS | Caddy on ports `80` and `443` |

Ports `80` and `443` must be available for Caddy. Telegram Web Apps require public HTTPS.

## Environment

The deployment creates an `.env` file on the server. That file contains secrets and must not be committed.

Example:

```env
BOT_TOKEN=replace-with-telegram-token
PUBLIC_BASE_URL=https://your-domain.example
OPENAI_API_KEY=your-provider-key
OPENAI_BASE_URL=https://api.openai.com/v1
ASSISTANT_MODEL=gpt-4.1-mini
DATABASE_PATH=/opt/telegram-group-assistant/data/assistant.sqlite3
HOST=127.0.0.1
PORT=8000
LOG_LEVEL=info
```

## Initial Install

Run from the project directory on a clean Ubuntu VPS:

```bash
BOT_TOKEN="replace-with-telegram-token" \
OPENAI_API_KEY="your-provider-key" \
OPENAI_BASE_URL="https://api.openai.com/v1" \
ASSISTANT_MODEL="gpt-4.1-mini" \
PUBLIC_BASE_URL="https://your-domain.example" \
bash deploy/install-ubuntu.sh
```

Before starting, make sure the domain points to the VPS and ports `80` and `443` are free.

## Updating

1. Copy changed source files into `/opt/telegram-group-assistant` without overwriting `.env` or `data`.
2. If `requirements.txt` changed, update dependencies:

```bash
/opt/telegram-group-assistant/.venv/bin/pip install -r /opt/telegram-group-assistant/requirements.txt
```

3. Restart the service:

```bash
systemctl restart telegram-group-assistant
systemctl is-active telegram-group-assistant
```

## Diagnostics

```bash
bash /opt/telegram-group-assistant/deploy/check-server.sh
systemctl status telegram-group-assistant --no-pager
journalctl -u telegram-group-assistant -n 100 --no-pager
curl -fsS https://your-domain.example/health
```

If Caddy returns `502`, the application usually is not listening on `127.0.0.1:8000`. Check the service journal first, then restart the service.

## Security

- Do not commit Telegram tokens, LLM API keys, root passwords, private keys, `.env` files, production domains, server IP addresses, provider names, or account details.
- If a secret was pasted into a chat or committed, rotate it before serious production use.
- Web App screen URLs are public to anyone who has the `screen_id` link until Telegram init data verification and access checks are added.
