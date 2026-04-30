import subprocess
import sys
from datetime import datetime
from pathlib import Path

import requests
import rumps

API_BASE = "http://127.0.0.1:8000/api"
SETTINGS_URL = "http://127.0.0.1:8000/#/settings"
REQUEST_TIMEOUT = 2
WINDOW_SCRIPT = Path(__file__).resolve().parent / "window.py"


class TimerkApp(rumps.App):
    def __init__(self) -> None:
        super().__init__("⏱", quit_button=None)
        self.active_started_at: datetime | None = None
        self.timer_unit: str = "min"
        self._stop_item: rumps.MenuItem | None = None
        self._settings_proc: subprocess.Popen | None = None

        self._refresh_state()
        self._build_menu()

        self._tick_timer = rumps.Timer(self._tick, 1)
        self._tick_timer.start()

    # --- Remote state ---

    def _refresh_state(self) -> None:
        try:
            settings = requests.get(f"{API_BASE}/settings", timeout=REQUEST_TIMEOUT).json()
            for s in settings:
                if s["key"] == "timer_unit":
                    self.timer_unit = s["value"]
        except Exception as e:
            rumps.notification("timerk", "設定の取得失敗", str(e))

        try:
            active = requests.get(
                f"{API_BASE}/time-entries/active", timeout=REQUEST_TIMEOUT
            ).json()
            self.active_started_at = (
                datetime.fromisoformat(active["started_at"]) if active else None
            )
        except Exception as e:
            rumps.notification("timerk", "タイマー状態取得失敗", str(e))

    def _fetch_projects(self) -> list[dict]:
        try:
            res = requests.get(f"{API_BASE}/projects", timeout=REQUEST_TIMEOUT)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            rumps.notification("timerk", "PJ 取得失敗", str(e))
            return []

    # --- Menu ---

    def _build_menu(self) -> None:
        self.menu.clear()

        projects = self._fetch_projects()

        if projects:
            for p in projects:
                self.menu.add(
                    rumps.MenuItem(
                        p["name"], callback=self._make_start_callback(p["id"])
                    )
                )
        else:
            placeholder = rumps.MenuItem("(プロジェクト未登録)")
            self.menu.add(placeholder)

        self.menu.add(rumps.separator)

        self._stop_item = rumps.MenuItem("⏹ 停止", callback=self._stop)
        self.menu.add(self._stop_item)

        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem("⚙️ 設定", callback=self._open_settings))
        self.menu.add(rumps.MenuItem("🔄 更新", callback=self._refresh))
        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem("終了", callback=rumps.quit_application))

    # --- Callbacks ---

    def _make_start_callback(self, project_id: int):
        def callback(_):
            self._start_timer(project_id)

        return callback

    def _start_timer(self, project_id: int) -> None:
        try:
            res = requests.post(
                f"{API_BASE}/time-entries/start",
                json={"project_id": project_id},
                timeout=REQUEST_TIMEOUT,
            )
            res.raise_for_status()
            data = res.json()
            self.active_started_at = datetime.fromisoformat(data["started_at"])
        except Exception as e:
            rumps.notification("timerk", "開始失敗", str(e))

    def _stop(self, _) -> None:
        if self.active_started_at is None:
            rumps.notification("timerk", "停止", "計測中のタイマーはありません")
            return
        try:
            res = requests.post(
                f"{API_BASE}/time-entries/stop", timeout=REQUEST_TIMEOUT
            )
            res.raise_for_status()
            self.active_started_at = None
        except Exception as e:
            rumps.notification("timerk", "停止失敗", str(e))

    def _refresh(self, _) -> None:
        self._refresh_state()
        self._build_menu()

    def _open_settings(self, _) -> None:
        if self._settings_proc is not None and self._settings_proc.poll() is None:
            return

        try:
            self._settings_proc = subprocess.Popen(
                [sys.executable, str(WINDOW_SCRIPT), SETTINGS_URL, "timerk - 設定"]
            )
        except Exception as e:
            rumps.notification("timerk", "設定画面の起動失敗", str(e))

    # --- Tick ---

    def _tick(self, _) -> None:
        if self._settings_proc is not None and self._settings_proc.poll() is not None:
            self._settings_proc = None
            self._refresh_state()
            self._build_menu()

        if self.active_started_at is None:
            self.title = "⏱"
            return

        elapsed = int((datetime.now() - self.active_started_at).total_seconds())

        if self.timer_unit == "sec":
            h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
            self.title = f"{h:02d}:{m:02d}:{s:02d}"
        else:
            m, s = elapsed // 60, elapsed % 60
            self.title = f"{m:02d}:{s:02d}"


if __name__ == "__main__":
    TimerkApp().run()
