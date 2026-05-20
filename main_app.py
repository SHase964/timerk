"""timerk アプリのエントリポイント（dispatch）。

引数によって3モードに分岐する:
  (引数なし)          backend を起動 → メニューバーを起動
  --backend           uvicorn を起動
  --window URL TITLE  pywebview ウィンドウを開く

py2app でバンドル化したとき、各サブプロセスもこのスクリプトを再起動して
適切なモードで動くため、全プロセスが timerk.app のインスタンスとして
macOS から認識される。
"""

import os

from bundle import resource_path, spawn_self

# backend.main は module load 時に TIMERK_FRONTEND_DIST を読んで StaticFiles を mount するので、
# import より前に環境変数をセットする。setdefault にしているのは、外部から指定された場合を尊重するため。
os.environ.setdefault("TIMERK_FRONTEND_DIST", str(resource_path("frontend", "dist")))

import atexit  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

import requests  # type: ignore[import-untyped]  # noqa: E402
import uvicorn  # noqa: E402
import webview  # noqa: E402

from backend.main import app  # noqa: E402
from menubar.app import TimerkApp  # noqa: E402

BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8000
BACKEND_HEALTH_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}/api/projects"
BACKEND_STARTUP_TIMEOUT = 10.0


def _wait_for_backend(timeout: float) -> bool:

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            requests.get(BACKEND_HEALTH_URL, timeout=0.5)
            return True
        except Exception:
            time.sleep(0.2)
    return False


def _run_backend() -> None:
    uvicorn.run(app, host=BACKEND_HOST, port=BACKEND_PORT, log_level="warning")


def _run_window(url: str, title: str) -> None:
    webview.create_window(title, url, width=640, height=780)
    webview.start()


def _run_menubar() -> None:
    backend_proc = spawn_self("--backend")
    atexit.register(backend_proc.terminate)

    if not _wait_for_backend(BACKEND_STARTUP_TIMEOUT):
        backend_proc.terminate()
        raise SystemExit("backend did not become ready in time")

    TimerkApp().run()


def main() -> None:
    args = sys.argv[1:]
    if not args:
        _run_menubar()
    elif args[0] == "--backend":
        _run_backend()
    elif args[0] == "--window":
        if len(args) < 3:
            raise SystemExit("usage: --window URL TITLE")
        _run_window(args[1], args[2])
    else:
        raise SystemExit(f"unknown mode: {args[0]}")


if __name__ == "__main__":
    main()
