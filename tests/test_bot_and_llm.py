import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.assistant.llm import AssistantBrain
from app.bot.telegram import send_screen_button
from app.config import Settings


def settings() -> Settings:
    return Settings(
        bot_token="test-token",
        public_base_url="https://bot.example",
        openai_api_key="test-key",
        openai_base_url="https://api.example",
        assistant_model="test-model",
        database_path=":memory:",
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )


class ScreenButtonTests(unittest.IsolatedAsyncioTestCase):
    async def test_group_screen_uses_regular_url_button(self) -> None:
        message = SimpleNamespace(
            chat=SimpleNamespace(type="group"),
            answer=AsyncMock(),
        )

        await send_screen_button(message, "https://bot.example/webapp/screens/abc")

        _, kwargs = message.answer.call_args
        button = kwargs["reply_markup"].inline_keyboard[0][0]
        self.assertEqual(button.url, "https://bot.example/webapp/screens/abc")
        self.assertIsNone(button.web_app)

    async def test_private_screen_uses_web_app_button(self) -> None:
        message = SimpleNamespace(
            chat=SimpleNamespace(type="private"),
            answer=AsyncMock(),
        )

        await send_screen_button(message, "https://bot.example/webapp/screens/abc")

        _, kwargs = message.answer.call_args
        button = kwargs["reply_markup"].inline_keyboard[0][0]
        self.assertIsNone(button.url)
        self.assertEqual(button.web_app.url, "https://bot.example/webapp/screens/abc")


class AssistantBrainTests(unittest.IsolatedAsyncioTestCase):
    def test_creates_openai_compatible_client(self) -> None:
        brain = AssistantBrain(settings())

        self.assertIsNotNone(brain.client)

    async def test_returns_fallback_when_llm_fails(self) -> None:
        brain = object.__new__(AssistantBrain)
        brain.settings = settings()
        brain.client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=AsyncMock(side_effect=RuntimeError("offline")))
            )
        )

        answer = await brain.answer("test")

        self.assertIn("временно недоступен", answer)
