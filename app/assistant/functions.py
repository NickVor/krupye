from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable

from app.assistant.llm import AssistantBrain
from app.config import Settings
from app.storage.screens import create_web_screen


@dataclass(frozen=True)
class FunctionContext:
    settings: Settings
    brain: AssistantBrain
    chat_id: int
    user_id: int


FunctionHandler = Callable[[FunctionContext, str], Awaitable[str]]


@dataclass(frozen=True)
class AssistantFunction:
    name: str
    description: str
    handler: FunctionHandler
    creates_web_screen: bool = False


async def answer_question(context: FunctionContext, text: str) -> str:
    return await context.brain.answer(text)


async def create_rich_answer_screen(context: FunctionContext, text: str) -> str:
    answer = await context.brain.answer(text)
    screen_id = create_web_screen(
        database_path=context.settings.database_path,
        title=text[:80] or "Ответ ассистента",
        payload={
            "kind": "rich_answer",
            "question": text,
            "answer": answer,
            "blocks": [
                {"title": "Короткий ответ", "body": answer},
                {
                    "title": "Что можно сделать дальше",
                    "body": "Уточнить вопрос, открыть материалы или сохранить результат.",
                },
            ],
            "actions": [
                {"label": "Скопировать вывод", "type": "copy"},
                {"label": "Задать уточнение", "type": "reply"},
            ],
        },
    )
    return f"{context.settings.public_base_url}/webapp/screens/{screen_id}"


async def list_functions(context: FunctionContext, text: str) -> str:
    rows = [f"/{item.name} - {item.description}" for item in FUNCTION_REGISTRY.values()]
    return "Доступные функции:\n" + "\n".join(rows)


FUNCTION_REGISTRY: dict[str, AssistantFunction] = {
    "ask": AssistantFunction(
        name="ask",
        description="ответить на вопрос в чате",
        handler=answer_question,
    ),
    "screen": AssistantFunction(
        name="screen",
        description="создать Web App-экран с расширенным ответом",
        handler=create_rich_answer_screen,
        creates_web_screen=True,
    ),
    "functions": AssistantFunction(
        name="functions",
        description="показать список функций ассистента",
        handler=list_functions,
    ),
}
