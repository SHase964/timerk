"""py2app build configuration for timerk.

使い方:
    make app          # alias モード（開発用、高速）
    make app-release  # standalone モード（配布用、自己完結）

alias モードは .app の中身がソースへのシンボリックリンクなので、
ソースを編集してもリビルド不要で反映される。配布はできない。
"""

from collections.abc import Sequence
import os

from setuptools import setup
from setuptools.dist import Distribution


class _Py2AppDistribution(Distribution):
    """py2app は install_requires が非空だとエラーにするが、
    pyproject.toml の [project.dependencies] が setuptools により自動的に
    install_requires にマップされてしまう。py2app コマンド実行時には不要なので、
    pyproject.toml 読み込み後（parse_config_files の後）に空にする。
    """

    def parse_config_files(self, filenames=None, ignore_option_errors=False) -> None:  # type: ignore[no-untyped-def]
        super().parse_config_files(filenames, ignore_option_errors)
        self.install_requires = []

APP = ["main_app.py"]


def _collect_data_files(src_root: str, dst_root: str) -> list[tuple[str, Sequence[str]]]:
    """src_root 配下のファイルを再帰的に集めて DATA_FILES 形式に変換する。

    バンドル内では Contents/Resources/{dst_root}/... に配置される。
    """
    result: list[tuple[str, Sequence[str]]] = []
    for dirpath, _, filenames in os.walk(src_root):
        if not filenames:
            continue
        rel = os.path.relpath(dirpath, src_root)
        target = dst_root if rel == "." else os.path.join(dst_root, rel)
        files = [os.path.join(dirpath, f) for f in filenames]
        result.append((target, files))
    return result


DATA_FILES = _collect_data_files("frontend/dist", "frontend/dist")

OPTIONS = {
    "argv_emulation": False,
    "plist": {
        "CFBundleName": "timerk",
        "CFBundleDisplayName": "timerk",
        "CFBundleIdentifier": "app.timerk",
        "CFBundleShortVersionString": "0.1.0",
        "CFBundleVersion": "0.1.0",
        "LSUIElement": True,
    },
    "packages": [
        "fastapi",
        "starlette",
        "pydantic",
        "sqlmodel",
        "sqlalchemy",
        "uvicorn",
        "rumps",
        "webview",
        "requests",
    ],
    "includes": [
        "backend",
        "backend.api",
        "backend.api.projects",
        "backend.api.reports",
        "backend.api.settings",
        "backend.api.time_entries",
        "backend.core.database",
        "backend.main",
        "menubar.app",
        "bundle",
    ],
}


if __name__ == "__main__":
    setup(
        app=APP,
        data_files=DATA_FILES,
        options={"py2app": OPTIONS},
        distclass=_Py2AppDistribution,
    )
