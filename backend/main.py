from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.api import projects, reports, settings, time_entries
from backend.core.database import init_db

_DEFAULT_FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
FRONTEND_DIST = Path(os.environ.get("TIMERK_FRONTEND_DIST", str(_DEFAULT_FRONTEND_DIST)))


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(title="timerk", lifespan=lifespan)

app.include_router(projects.router, prefix="/api")
app.include_router(time_entries.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(reports.router, prefix="/api")

if FRONTEND_DIST.exists():
    # follow_symlink=True: py2app の alias モードでは frontend/dist 配下がシンボリックリンクになり、
    # デフォルトの realpath ベースの security check で「ディレクトリ外」と判定されて 404 になるため。
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True, follow_symlink=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
