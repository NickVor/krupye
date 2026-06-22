from __future__ import annotations

import asyncio
import logging

from openai import AsyncOpenAI

from app.config import Settings


SYSTEM_PROMPT = """
Ты полезный ассистент Telegram-группы. Отвечай кратко, по делу и на языке пользователя.
Если вопрос требует структурированного или визуально богатого ответа, предложи открыть Web App-экран.
"""

logger = logging.getLogger(__name__)
LLM_TIMEOUT_SECONDS = 45


class AssistantBrain:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = (
            AsyncOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
            )
            if settings.openai_api_key
            else None
        )

    async def answer(self, question: str) -> str:
        if not self.client:
            return (
                "Я получил вопрос, но LLM пока не подключена. "
                "Добавьте OPENAI_API_KEY в .env, и я начну отвечать полноценно.\n\n"
                f"Вопрос: {question}"
            )

        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.settings.assistant_model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT.strip()},
                        {"role": "user", "content": question},
                    ],
                ),
                timeout=LLM_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            logger.warning("LLM request timed out after %s seconds", LLM_TIMEOUT_SECONDS)
            return "Сервис ответов сейчас отвечает слишком долго. Попробуйте еще раз через минуту."
        except Exception:
            logger.exception("LLM request failed")
            return "Сервис ответов временно недоступен. Попробуйте еще раз чуть позже."

        content = response.choices[0].message.content
        return (content or "").strip() or "Не удалось получить содержательный ответ. Попробуйте переформулировать вопрос."
