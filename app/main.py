from __future__ import annotations

import asyncio

import uvicorn

from app.bot.telegram import build_bot_app
from app.config import get_settings
from app.storage.database import init_database
from app.web.server import build_web_app


async def main() -> None:
    settings = get_settings()
    init_database(settings.database_path)

    bot, dispatcher = build_bot_app(settings)
    web_app = build_web_app(settings)

    server = uvicorn.Server(
        uvicorn.Config(
            web_app,
            host=settings.host,
            port=settings.port,
            log_level=settings.log_level,
        )
    )

    polling_task = asyncio.create_task(
        dispatcher.start_polling(bot, handle_signals=False)
    )
    shutdown_task = asyncio.create_task(
        stop_polling_on_server_exit(server, dispatcher, polling_task)
    )

    try:
        await server.serve()
    finally:
        if not polling_task.done():
            await dispatcher.stop_polling()
        await polling_task
        shutdown_task.cancel()
        await asyncio.gather(shutdown_task, return_exceptions=True)
        await bot.session.close()


async def stop_polling_on_server_exit(
    server: uvicorn.Server,
    dispatcher,
    polling_task: asyncio.Task[None],
) -> None:
    while not server.should_exit:
        await asyncio.sleep(0.2)

    if not polling_task.done():
        await dispatcher.stop_polling()


if __name__ == "__main__":
    asyncio.run(main())
