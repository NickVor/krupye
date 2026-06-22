# Развёртывание на VPS

## Текущая продакшен-схема

```text
bot.n7k.ru:443 -> Caddy -> 127.0.0.1:8000 -> FastAPI + Telegram bot
                                           -> OpenRouter
                                           -> SQLite
```

| Компонент | Значение |
| --- | --- |
| Публичный адрес | `https://bot.n7k.ru` |
| Каталог приложения | `/opt/telegram-group-assistant` |
| systemd-служба | `telegram-group-assistant` |
| Web App | `127.0.0.1:8000` |
| HTTPS | Caddy на портах `80` и `443` |
| VPN (3X-UI/Xray) | `8443` |

Порт `443` принадлежит Caddy. Не переназначайте на него VPN inbound, иначе
Web App и выпуск сертификата перестанут работать.

## Настройки окружения

Файл `/opt/telegram-group-assistant/.env` содержит секреты и имеет права
доступа только для владельца. Пример рабочей конфигурации:

```env
BOT_TOKEN=replace-with-telegram-token
PUBLIC_BASE_URL=https://bot.n7k.ru
OPENAI_API_KEY=your-openrouter-key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
ASSISTANT_MODEL=openrouter/free
DATABASE_PATH=/opt/telegram-group-assistant/data/assistant.sqlite3
HOST=127.0.0.1
PORT=8000
LOG_LEVEL=info
```

`openrouter/free` подходит для запуска и тестов. Для предсказуемого качества,
скорости и лимитов используйте конкретную модель вместо бесплатного маршрута.

## Первичная установка

На чистом Ubuntu VPS выполните из каталога проекта:

```bash
BOT_TOKEN="replace-with-telegram-token" \
OPENAI_API_KEY="your-openrouter-key" \
OPENAI_BASE_URL="https://openrouter.ai/api/v1" \
ASSISTANT_MODEL="openrouter/free" \
PUBLIC_BASE_URL="https://bot.n7k.ru" \
bash deploy/install-ubuntu.sh
```

Сценарий создаёт системного пользователя `assistant`, устанавливает
зависимости, создаёт systemd-службу и конфигурирует Caddy по имени из
`PUBLIC_BASE_URL`.

Перед запуском убедитесь, что DNS-запись `A` для домена уже указывает на VPS и
что порты `80` и `443` свободны. Caddy выпустит и будет продлевать сертификат
автоматически.

## Обновление приложения

1. Скопируйте изменённые исходники в `/opt/telegram-group-assistant`, не
   перезаписывая `.env` и каталог `data`.
2. Если менялся `requirements.txt`, обновите зависимости:

```bash
/opt/telegram-group-assistant/.venv/bin/pip install -r /opt/telegram-group-assistant/requirements.txt
```

3. Перезапустите службу:

```bash
systemctl restart telegram-group-assistant
systemctl is-active telegram-group-assistant
```

Версия `openai==1.35.7` в проекте требует `httpx<0.28`; ограничение закреплено
в `requirements.txt` и не должно удаляться без обновления SDK OpenAI.

## Проверка и диагностика

```bash
bash /opt/telegram-group-assistant/deploy/check-server.sh
systemctl status telegram-group-assistant --no-pager
journalctl -u telegram-group-assistant -n 100 --no-pager
curl -fsS https://bot.n7k.ru/health
```

Если Caddy отвечает `502`, обычно приложение не слушает `127.0.0.1:8000`.
Сначала проверьте журнал `telegram-group-assistant`, затем перезапустите
службу.

## Безопасность

- Не отправляйте ключи OpenRouter, Telegram-токены и root-пароли в репозиторий.
- Если секрет был отправлен в чат, отзовите его у провайдера и выпустите новый.
- Не публикуйте порт панели 3X-UI без необходимости и используйте надёжный
  пароль.
- Web App-экраны пока доступны всем, у кого есть ссылка с `screen_id`; не
  храните в них чувствительные данные до добавления проверки Telegram init data.
