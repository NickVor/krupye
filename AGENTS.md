# Project Instructions

## Project

This repository contains the Krupye project: a Telegram group assistant with a companion Telegram Web App.

The assistant should:

- answer questions in a Telegram group or private chat;
- expose a small catalog of explicit functions;
- create Telegram Web App screens for rich content that does not fit well into a plain Telegram message;
- stay simple enough for fast iterative development;
- deploy on a small VPS.

Keep the project practical. Prefer a working narrow feature over a broad abstract platform.

## Current Stack

- Python
- aiogram for Telegram bot polling
- FastAPI and uvicorn for the Web App/API server
- SQLite for MVP storage
- OpenAI-compatible API behind a replaceable assistant layer; production uses OpenRouter
- systemd and Caddy for VPS deployment

## Important Files

- `app/main.py` starts both the Telegram bot and the FastAPI server.
- `app/config.py` loads environment configuration.
- `app/bot/telegram.py` handles Telegram commands and messages.
- `app/assistant/functions.py` is the function registry. Add user-facing assistant capabilities here.
- `app/assistant/llm.py` wraps the LLM provider.
- `app/storage/database.py` initializes SQLite.
- `app/storage/screens.py` stores and loads Web App screens.
- `app/web/server.py` exposes health, API, and Web App routes.
- `app/web/templates.py` renders Web App HTML.
- `deploy/install-ubuntu.sh` installs the app on Ubuntu.
- `deploy/check-server.sh` verifies service, web, and Telegram API access.
- `deploy/assistant.service` is the systemd service.
- `deploy/Caddyfile` is the reverse-proxy template.

## MVP Definition

MVP is complete when:

1. The bot runs on a non-Russian VPS and can reach Telegram API reliably.
2. `/start` responds.
3. `/functions` lists available functions.
4. `/ask question` returns an assistant response.
5. `/screen topic` creates a Web App screen and sends an open button.
6. The Web App opens over public HTTPS.
7. New assistant functions can be added through `app/assistant/functions.py` without rewriting the bot.

## Architecture Rules

- Keep bot and Web App in one Python process for now.
- Keep SQLite until there is a concrete reason to move to PostgreSQL.
- Keep LLM calls inside `app/assistant/llm.py` or a successor provider interface.
- Do not spread OpenAI calls across the codebase.
- Add assistant capabilities through the function registry.
- Use Web App screens only for rich/structured content, not for short plain answers.
- Keep secrets in `.env`; never put them in source files or deploy archives.
- Do not add SaaS accounts, billing, CRM, admin panels, microservices, queues, or container orchestration until the MVP is stable and there is a clear need.

## Web App Guidance

Use a Web App screen when the response needs:

- tables;
- structured cards;
- actions;
- forms;
- longer explanations;
- a persistent link back to the result.

Do not use a Web App screen for a short answer that reads naturally inside Telegram.

## Deployment Guidance

Production needs:

- Ubuntu 24.04 VPS;
- 1 CPU and 1 GB RAM minimum;
- ports `22`, `80`, and `443` available;
- outbound access to `api.telegram.org`;
- public HTTPS URL.

The current production domain is `https://bot.n7k.ru`. Caddy owns ports `80` and
`443`; the 3X-UI/Xray inbound was moved to `8443`. Keep this separation when
changing either service. Telegram Web Apps require public HTTPS.

After deployment, verify with:

```bash
bash /opt/telegram-group-assistant/deploy/check-server.sh
```

## Development Workflow

- Before editing, inspect the relevant existing files.
- Keep changes scoped to the requested behavior.
- Prefer existing patterns over new abstractions.
- Use `apply_patch` for manual edits.
- Do not commit secrets.
- Do not rely on local `.env` values in explanations.
- After Python edits, run:

```powershell
.\.venv\Scripts\python.exe -m compileall app
```

If dependencies are missing, install them in `.venv` from `requirements.txt`.

## Current Priorities

1. Verify `/start`, `/functions`, `/ask`, and `/screen` from Telegram.
2. Confirm the Web App opens inside Telegram on mobile and desktop.
3. Add the first real domain-specific assistant function.
4. Add basic tests for screen creation and function registry behavior.
5. Add Telegram Web App init data verification before handling sensitive data.

## Security Notes

- Telegram bot token is sensitive.
- If a bot token was pasted into chat, rotate it before serious production use.
- Root passwords must not be stored in this repository.
- `.env` must stay ignored.
- Current Web App screen URLs are public to anyone with the `screen_id` link.
- Add Telegram Web App init data verification before storing or displaying sensitive data.

## For New Codex Sessions

Read this file first. Treat it as the project-level instruction source.

The canonical project instruction file is `AGENTS.md`.

If the user asks for project direction, architecture, or next steps, align the answer with this file.
