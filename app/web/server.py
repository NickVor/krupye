from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response

from app.config import Settings
from app.storage.screens import get_web_screen
from app.web.templates import render_screen_html


def build_web_app(settings: Settings) -> FastAPI:
    app = FastAPI(title="Telegram Group Assistant Web App")

    @app.get("/", response_class=HTMLResponse)
    async def index() -> str:
        return render_placeholder_html(settings)

    @app.head("/")
    async def index_head() -> Response:
        return Response(status_code=200)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/screens/{screen_id}")
    async def screen_data(screen_id: str) -> dict:
        screen = get_web_screen(settings.database_path, screen_id)
        if not screen:
            raise HTTPException(status_code=404, detail="Screen not found")
        return screen

    @app.get("/webapp/screens/{screen_id}", response_class=HTMLResponse)
    async def webapp_screen(screen_id: str) -> str:
        screen = get_web_screen(settings.database_path, screen_id)
        if not screen:
            raise HTTPException(status_code=404, detail="Screen not found")
        return render_screen_html(screen)

    return app


def render_placeholder_html(settings: Settings) -> str:
    return f"""
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Telegram Group Assistant</title>
        <style>
            :root {{
                --bg: #f6f7f9;
                --text: #1f2937;
                --muted: #667085;
                --surface: #ffffff;
                --line: #d0d5dd;
                --accent: #246bfe;
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
                width: min(100%, 820px);
                margin: 0 auto;
                padding: 32px 20px;
            }}
            header {{
                padding: 16px 0 24px;
            }}
            h1 {{
                margin: 0 0 10px;
                font-size: 32px;
                line-height: 1.15;
                letter-spacing: 0;
            }}
            p {{
                margin: 0;
                color: var(--muted);
                line-height: 1.55;
            }}
            .status {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 18px;
                color: #067647;
                font-weight: 700;
            }}
            .dot {{
                width: 10px;
                height: 10px;
                border-radius: 999px;
                background: #12b76a;
            }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
                gap: 14px;
                margin-top: 22px;
            }}
            section {{
                background: var(--surface);
                border: 1px solid var(--line);
                border-radius: 8px;
                padding: 16px;
            }}
            h2 {{
                margin: 0 0 10px;
                font-size: 17px;
                letter-spacing: 0;
            }}
            code {{
                display: inline-block;
                margin: 4px 4px 4px 0;
                padding: 5px 8px;
                border-radius: 6px;
                background: #eef2ff;
                color: #1d4ed8;
                font-size: 14px;
            }}
            a {{
                color: var(--accent);
                font-weight: 700;
                text-decoration: none;
            }}
            .small {{
                margin-top: 12px;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <main>
            <header>
                <div class="status"><span class="dot"></span>Server is running</div>
                <h1>Telegram Group Assistant</h1>
                <p>This is the service page. The bot answers in Telegram, and Web App screens open from bot messages.</p>
            </header>

            <div class="grid">
                <section>
                    <h2>Bot commands</h2>
                    <code>/start</code>
                    <code>/functions</code>
                    <code>/ask question</code>
                    <code>/screen topic</code>
                </section>

                <section>
                    <h2>Server check</h2>
                    <p><a href="/health">/health</a></p>
                    <p class="small">If it shows <code>{{"status":"ok"}}</code>, the web app is responding.</p>
                </section>

                <section>
                    <h2>Web App</h2>
                    <p>Rich screens are created with the <code>/screen</code> Telegram command.</p>
                    <p class="small">Current public URL: <code>{settings.public_base_url}</code></p>
                </section>
            </div>
        </main>
    </body>
    </html>
    """
