# Крупье: Telegram Group Assistant

Telegram-ассистент для групп и личных чатов с дополнительными экранами
Telegram Web App. Он отвечает на вопросы, показывает каталог функций и создаёт
расширенные карточки для ответов, которые неудобно читать в одном сообщении.

## Текущий статус

- Продакшен: [bot.n7k.ru](https://bot.n7k.ru)
- Бот и Web App работают на одном Ubuntu VPS.
- HTTPS и обратный прокси обеспечивает Caddy.
- LLM подключена через OpenRouter с маршрутом `openrouter/free`.
- Данные экранов хранятся в SQLite.

## Возможности

- `/start` - краткое приветствие.
- `/ask вопрос` - ответ ассистента.
- `/functions` - список доступных команд.
- `/screen тема` - Web App-экран с развёрнутым ответом. В личном чате он
  открывается как Telegram Web App, в группе - по обычной HTTPS-ссылке.
- Обычное сообщение обрабатывается в личном чате, при упоминании бота в группе
  или в ответ на сообщение бота.

## Устройство

```text
Telegram <- aiogram bot + FastAPI <- Caddy <- HTTPS
                    |       |
                    |       +-- Web App screens
                    +-- OpenRouter / LLM
                    +-- SQLite
```

Основные модули:

- `app/bot/telegram.py` - Telegram-команды и обработка сообщений.
- `app/assistant/llm.py` - единственная точка вызова LLM.
- `app/assistant/functions.py` - реестр пользовательских функций.
- `app/web/` - FastAPI-маршруты и HTML Web App.
- `app/storage/` - SQLite и хранение экранов.
- `deploy/` - systemd, Caddy и сценарии установки и диагностики.

## Локальный запуск

1. Создайте `.env` по примеру `.env.example`.
2. Укажите `BOT_TOKEN` и публичный HTTPS-адрес в `PUBLIC_BASE_URL`.
3. Установите зависимости и запустите приложение:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.main
```

Для Telegram Web App `PUBLIC_BASE_URL` должен быть доступен из интернета по
HTTPS. При локальной разработке используйте туннель.

## Подключение LLM

По умолчанию проект совместим с OpenAI API. Для текущей конфигурации
OpenRouter добавьте в `.env`:

```env
OPENAI_API_KEY=your-openrouter-key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
ASSISTANT_MODEL=openrouter/free
```

`openrouter/free` выбирает доступную бесплатную модель. У бесплатного пула
могут быть очереди и временные ограничения; для стабильной нагрузки укажите
конкретную платную модель OpenRouter.

Ключи, токены и пароли не хранятся в репозитории и не должны попадать в чаты,
логи или Markdown-файлы.

## Развёртывание

Продакшен-инструкции, команды проверки и схема портов находятся в
[deploy/README.md](deploy/README.md).

После изменения Python-кода выполните быструю проверку:

```powershell
.\.venv\Scripts\python.exe -m compileall app
```
