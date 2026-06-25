from __future__ import annotations

import json
import sqlite3
import uuid
from typing import Any


def create_web_screen(database_path: str, title: str, payload: dict[str, Any]) -> str:
    screen_id = uuid.uuid4().hex
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            "INSERT INTO web_screens (id, title, payload_json) VALUES (?, ?, ?)",
            (screen_id, title, json.dumps(payload, ensure_ascii=False)),
        )
        connection.commit()
    return screen_id


def get_web_screen(database_path: str, screen_id: str) -> dict[str, Any] | None:
    with sqlite3.connect(database_path) as connection:
        row = connection.execute(
            "SELECT id, title, payload_json, created_at FROM web_screens WHERE id = ?",
            (screen_id,),
        ).fetchone()

    if not row:
        return None

    return {
        "id": row[0],
        "title": row[1],
        "payload": json.loads(row[2]),
        "created_at": row[3],
    }
