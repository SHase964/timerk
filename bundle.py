"""自分自身を別プロセスとして再起動するためのユーティリティ。

py2app でバンドル化したとき、サブプロセスも .app のランチャ経由で
起動することで、macOS から timerk.app のインスタンスとして認識される
（python3 表示にならない）。開発時は main_app.py を Python で再実行する。
"""

from pathlib import Path
import subprocess
import sys

from Foundation import NSBundle

BUNDLE_IDENTIFIER = "app.timerk"

_BUNDLE = NSBundle.mainBundle()
IS_BUNDLED = _BUNDLE is not None and _BUNDLE.bundleIdentifier() == BUNDLE_IDENTIFIER

_PROJECT_ROOT = Path(__file__).resolve().parent
MAIN_APP_PATH = _PROJECT_ROOT / "main_app.py"


def spawn_self(*args: str) -> subprocess.Popen:
    """自分自身を別プロセスとして起動する。

    バンドル時は .app のランチャを、開発時は main_app.py を Python で再実行する。
    """
    if IS_BUNDLED:
        launcher = str(_BUNDLE.executablePath())
        return subprocess.Popen([launcher, *args])
    return subprocess.Popen([sys.executable, str(MAIN_APP_PATH), *args])


def resource_path(*parts: str) -> Path:
    """同梱リソース（frontend/dist 等）の絶対パスを返す。

    バンドル時は Contents/Resources/ 配下、開発時はプロジェクトルート起点。
    """
    if IS_BUNDLED:
        return Path(str(_BUNDLE.resourcePath())).joinpath(*parts)
    return _PROJECT_ROOT.joinpath(*parts)
