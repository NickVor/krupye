from __future__ import annotations

from urllib.parse import urlparse

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from app.assistant.functions import FUNCTION_REGISTRY, FunctionContext
from app.assistant.llm import AssistantBrain
from app.config import Settings


def build_bot_app(settings: Settings) -> tuple[Bot, Dispatcher]:
    bot = Bot(token=settings.bot_token)
    dispatcher = Dispatcher()
    router = Router()
    brain = AssistantBrain(settings)

    async def run_function(message: Message, function_name: str, text: str) -> None:
        if not message.from_user:
            return

        function = FUNCTION_REGISTRY[function_name]
        context = FunctionContext(
            settings=settings,
            brain=brain,
            chat_id=message.chat.id,
            user_id=message.from_user.id,
        )
        result = await function.handler(context, text.strip())

        if function.creates_web_screen:
            await send_screen_button(message, result)
            return

        await message.answer(result)

    @router.message(Command("start"))
    async def start(message: Message) -> None:
        await message.answer(
            "Я ассистент группы. Напишите /ask вопрос или /screen тема, чтобы открыть расширенный экран."
        )

    @router.message(Command("functions"))
    async def functions(message: Message) -> None:
        await run_function(message, "functions", "")

    @router.message(Command("ask"))
    async def ask(message: Message) -> None:
        await run_function(message, "ask", command_payload(message.text, "/ask"))

    @router.message(Command("screen"))
    async def screen(message: Message) -> None:
        await run_function(message, "screen", command_payload(message.text, "/screen"))

    @router.message(F.web_app_data)
    async def web_app_data(message: Message) -> None:
        await message.answer("Получил действие из расширенного экрана. Можно продолжить обсуждение здесь.")

    @router.message(F.text)
    async def group_text(message: Message) -> None:
        if not message.text:
            return

        me = await bot.get_me()
        mentioned = f"@{me.username}" in message.text if me.username else False
        reply_to_bot = bool(
            message.reply_to_message
            and message.reply_to_message.from_user
            and message.reply_to_message.from_user.id == me.id
        )

        if mentioned or reply_to_bot or message.chat.type == "private":
            clean_text = message.text.replace(f"@{me.username}", "").strip() if me.username else message.text
            await run_function(message, "ask", clean_text)

    dispatcher.include_router(router)
    return bot, dispatcher


async def send_screen_button(message: Message, url: str) -> None:
    parsed_url = urlparse(url)
    if parsed_url.hostname == "your-public-domain.example" or parsed_url.scheme != "https":
        local_url = f"http://localhost:8000{parsed_url.path}"
        await message.answer(
            "Расширенный экран создан, но публичный HTTPS-адрес еще не настроен.\n\n"
            f"Пока можно открыть локально: {local_url}\n\n"
            "Для открытия прямо внутри Telegram нужно заменить PUBLIC_BASE_URL в .env на публичный HTTPS-адрес."
        )
        return

    if message.chat.type == "private":
        button = InlineKeyboardButton(
            text="Открыть расширенный экран",
            web_app=WebAppInfo(url=url),
        )
        text = "Готово. Я собрал расширенный экран для этого ответа."
    else:
        button = InlineKeyboardButton(
            text="Открыть расширенный экран",
            url=url,
        )
        text = "Готово. Откройте расширенный экран по кнопке ниже."

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    await message.answer(text, reply_markup=keyboard)


def command_payload(text: str | None, command: str) -> str:
    if not text:
        return ""
    first, _, rest = text.partition(" ")
    if first.startswith(command):
        return rest.strip()
    return text.strip()
