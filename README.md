# Krupye: Telegram Group Assistant

Krupye is a small Telegram group assistant with a companion Telegram Web App for richer responses.

The assistant can answer questions, list available functions, and create Web App screens for structured content that does not fit well into a single Telegram message.

## Features

- `/start` - short greeting.
- `/ask question` - assistant response.
- `/functions` - list of available assistant functions.
- `/screen topic` - creates a Web App screen with a richer answer.
- Private chats can open Web App screens directly.
- Group chats receive a normal HTTPS link button to the generated screen.

## Architecture

```text
Telegram <- aiogram bot + FastAPI <- Caddy <- HTTPS
                    |       |
                    |       +-- Web App screens
                    +-- OpenAI-compatible LLM provider
                    +-- SQLite
```

Main modules:

- `app/bot/telegram.py` - Telegram commands and message handling.
- `app/assistant/llm.py` - the only LLM provider integration point.
- `app/assistant/functions.py` - user-facing assistant function registry.
- `app/web/` - FastAPI routes and Web App HTML.
- `app/storage/` - SQLite initialization and screen storage.
- `deploy/` - generic systemd, Caddy, installation, and diagnostics files.

## Local Run

1. Create `.env` from `.env.example`.
2. Set `BOT_TOKEN` and `PUBLIC_BASE_URL`.
3. Install dependencies and start the app:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.main
```

For Telegram Web Apps, `PUBLIC_BASE_URL` must be reachable from the internet over HTTPS. For local development, use a tunnel or test the generated local URL in a browser.

## LLM Provider

The project uses an OpenAI-compatible API wrapper. Configure the provider through `.env`:

```env
OPENAI_API_KEY=your-provider-key
OPENAI_BASE_URL=https://api.openai.com/v1
ASSISTANT_MODEL=gpt-4.1-mini
```

OpenRouter or another OpenAI-compatible provider can be used by changing `OPENAI_BASE_URL` and `ASSISTANT_MODEL`.

Do not commit API keys, bot tokens, passwords, `.env` files, private keys, production domains, server IPs, provider account names, or other infrastructure identifiers.

## Deployment

Generic VPS deployment notes are in [deploy/README.md](deploy/README.md).

After Python changes, run a quick syntax check:

```powershell
.\.venv\Scripts\python.exe -m compileall app
```
