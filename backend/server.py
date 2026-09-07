"""ASGI entry untuk preview: Django dilayani di bawah prefix ASGI_ROOT_PATH (mis. /api)."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.asgi import get_asgi_application  # noqa: E402
from starlette.staticfiles import StaticFiles  # noqa: E402

django_app = get_asgi_application()
static_app = StaticFiles(directory=str(BASE_DIR / "static"))
PREFIX = os.environ.get("ASGI_ROOT_PATH", "").rstrip("/")
STATIC_PREFIX = f"{PREFIX}/static"


async def app(scope, receive, send):
    if scope["type"] == "lifespan":
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return
    if scope["type"] == "http" and PREFIX:
        path = scope["path"]
        if path.startswith(STATIC_PREFIX + "/"):
            scope = dict(scope, path=path[len(STATIC_PREFIX):], root_path="")
            return await static_app(scope, receive, send)
        if path == PREFIX or path.startswith(PREFIX + "/"):
            scope = dict(scope, root_path=PREFIX)
    await django_app(scope, receive, send)
