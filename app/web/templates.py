from __future__ import annotations

import json


def render_screen_html(screen: dict) -> str:
    payload = screen["payload"]
    blocks = payload.get("blocks", [])
    actions = payload.get("actions", [])

    block_html = "\n".join(
        f"""
        <section class="block">
            <h2>{escape_html(block.get("title", ""))}</h2>
            <p>{escape_html(block.get("body", ""))}</p>
        </section>
        """
        for block in blocks
    )
    action_html = "\n".join(
        f"""<button type="button" data-action="{escape_html(action.get("type", ""))}">{escape_html(action.get("label", ""))}</button>"""
        for action in actions
    )
    answer_json = json.dumps(payload.get("answer", ""), ensure_ascii=False).replace("</", "<\\/")

    return f"""
    <!doctype html>
    <html lang="ru">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{escape_html(screen["title"])}</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            :root {{
                color-scheme: light dark;
                --bg: var(--tg-theme-bg-color, #f7f5ef);
                --text: var(--tg-theme-text-color, #1d1d1f);
                --muted: var(--tg-theme-hint-color, #667085);
                --button: var(--tg-theme-button-color, #246bfe);
                --button-text: var(--tg-theme-button-text-color, #ffffff);
                --surface: var(--tg-theme-secondary-bg-color, #ffffff);
                font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }}
            * {{
                box-sizing: border-box;
            }}
            body {{
                margin: 0;
                background: var(--bg);
                color: var(--text);
            }}
            main {{
                width: min(100%, 760px);
                margin: 0 auto;
                padding: 20px;
            }}
            header {{
                padding: 8px 0 18px;
            }}
            h1 {{
                margin: 0;
                font-size: 28px;
                line-height: 1.15;
                letter-spacing: 0;
            }}
            .question {{
                margin: 12px 0 0;
                color: var(--muted);
                line-height: 1.5;
            }}
            .block {{
                background: var(--surface);
                border: 1px solid rgba(128, 128, 128, 0.18);
                border-radius: 8px;
                padding: 16px;
                margin: 12px 0;
            }}
            h2 {{
                margin: 0 0 8px;
                font-size: 16px;
                letter-spacing: 0;
            }}
            p {{
                margin: 0;
                white-space: pre-wrap;
                line-height: 1.55;
            }}
            .actions {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 10px;
                margin-top: 16px;
            }}
            button {{
                min-height: 44px;
                border: 0;
                border-radius: 8px;
                background: var(--button);
                color: var(--button-text);
                font-size: 15px;
                font-weight: 600;
                cursor: pointer;
            }}
        </style>
    </head>
    <body>
        <main>
            <header>
                <h1>{escape_html(screen["title"])}</h1>
                <p class="question">{escape_html(payload.get("question", ""))}</p>
            </header>
            {block_html}
            <div class="actions">{action_html}</div>
        </main>
        <script>
            const tg = window.Telegram?.WebApp;
            tg?.ready();
            tg?.expand();

            document.querySelectorAll("button").forEach((button) => {{
                button.addEventListener("click", () => {{
                    const action = button.dataset.action;
                    if (action === "copy") {{
                        navigator.clipboard.writeText({answer_json});
                    }}
                    if (action === "reply") {{
                        tg?.sendData(JSON.stringify({{ action: "reply", screenId: "{screen["id"]}" }}));
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    """


def escape_html(value: object) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )
