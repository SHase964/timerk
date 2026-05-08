from datetime import datetime
from pathlib import Path
import subprocess
import sys

from AppKit import NSColor, NSForegroundColorAttributeName
from Foundation import NSDate, NSMutableAttributedString, NSRunLoop, NSRunLoopCommonModes, NSTimer
import requests
import rumps

API_BASE = "http://127.0.0.1:8000/api"
SETTINGS_URL = "http://127.0.0.1:8000/#/settings"
REPORT_URL = "http://127.0.0.1:8000/#/report"
REQUEST_TIMEOUT = 2
WINDOW_SCRIPT = Path(__file__).resolve().parent / "window.py"

CIRCLE = "●"
DEFAULT_HEX = "#8E8E93"


def _hex_to_nscolor(hex_str: str) -> NSColor:
    h = hex_str.lstrip("#")
    if len(h) != 6:
        h = DEFAULT_HEX.lstrip("#")
    r = int(h[0:2], 16) / 255.0
    g = int(h[2:4], 16) / 255.0
    b = int(h[4:6], 16) / 255.0
    return NSColor.colorWithSRGBRed_green_blue_alpha_(r, g, b, 1.0)


def _colored_circle_attributed(text: str, color_hex: str) -> NSMutableAttributedString:
    """text の先頭 1 文字 (●) を color_hex で塗った NSAttributedString を返す。"""
    attr = NSMutableAttributedString.alloc().initWithString_(text)
    attr.addAttribute_value_range_(
        NSForegroundColorAttributeName,
        _hex_to_nscolor(color_hex),
        (0, 1),
    )
    return attr


class TimerkApp(rumps.App):
    def __init__(self) -> None:
        super().__init__("⏱", quit_button=None)
        self.active_started_at: datetime | None = None
        self.active_project_id: int | None = None
        self.show_seconds: bool = False
        self.show_hours: bool = False
        self._projects: list[dict] = []
        self._stop_item: rumps.MenuItem | None = None
        self._settings_proc: subprocess.Popen | None = None
        self._report_proc: subprocess.Popen | None = None

        self._refresh_state()
        self._build_menu()

        self._tick_timer = rumps.Timer(self._tick, 1)
        self._start_tick_timer_in_common_modes()

    def _start_tick_timer_in_common_modes(self) -> None:
        # rumps.Timer は NSDefaultRunLoopMode に登録するため、メニュー表示中
        # (NSEventTrackingRunLoopMode) は発火せず時間表示が止まって見える。
        # NSRunLoopCommonModes に登録してメニュー操作中も発火させる。
        timer = self._tick_timer
        timer._nsdate = NSDate.date()
        timer._nstimer = NSTimer.alloc().initWithFireDate_interval_target_selector_userInfo_repeats_(
            timer._nsdate,
            timer._interval,
            timer,
            "callback:",
            None,
            True,
        )
        NSRunLoop.currentRunLoop().addTimer_forMode_(timer._nstimer, NSRunLoopCommonModes)
        timer._status = True

    # --- Remote state ---

    def _refresh_state(self) -> None:
        try:
            res = requests.get(f"{API_BASE}/projects", timeout=REQUEST_TIMEOUT)
            res.raise_for_status()
            self._projects = res.json()
        except Exception as e:
            rumps.notification(title="timerk", subtitle="PJ 取得失敗", message=str(e))
            self._projects = []

        try:
            settings = requests.get(f"{API_BASE}/settings", timeout=REQUEST_TIMEOUT).json()
            for setting in settings:
                if setting["key"] == "show_seconds":
                    self.show_seconds = setting["value"] == "true"
                elif setting["key"] == "show_hours":
                    self.show_hours = setting["value"] == "true"
        except Exception as e:
            rumps.notification(title="timerk", subtitle="設定の取得失敗", message=str(e))

        try:
            active = requests.get(f"{API_BASE}/time-entries/active", timeout=REQUEST_TIMEOUT).json()
            if active:
                self.active_started_at = datetime.fromisoformat(active["started_at"])
                self.active_project_id = active["project_id"]
            else:
                self.active_started_at = None
                self.active_project_id = None
        except Exception as e:
            rumps.notification(title="timerk", subtitle="タイマー状態取得失敗", message=str(e))

    # --- Menu ---

    def _build_menu(self) -> None:
        self.menu.clear()

        if self._projects:
            for project in self._projects:
                title = f"{CIRCLE} {project['name']}"
                item = rumps.MenuItem(title, callback=self._make_start_callback(project["id"]))
                attr = _colored_circle_attributed(title, project.get("color", DEFAULT_HEX))
                item._menuitem.setAttributedTitle_(attr)
                self.menu.add(item)
        else:
            placeholder = rumps.MenuItem("(プロジェクト未登録)")
            self.menu.add(placeholder)

        self.menu.add(rumps.separator)

        self._stop_item = rumps.MenuItem("⏹ 停止", callback=self._stop)
        self.menu.add(self._stop_item)

        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem("📊 レポート", callback=self._open_report))
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
            self.active_project_id = data["project_id"]
        except Exception as e:
            rumps.notification("timerk", "開始失敗", str(e))

    def _stop(self, _) -> None:
        if self.active_started_at is None:
            rumps.notification("timerk", "停止", "計測中のタイマーはありません")
            return
        try:
            res = requests.post(f"{API_BASE}/time-entries/stop", timeout=REQUEST_TIMEOUT)
            res.raise_for_status()
            self.active_started_at = None
            self.active_project_id = None
        except Exception as e:
            rumps.notification("timerk", "停止失敗", str(e))

    def _refresh(self, _) -> None:
        self._refresh_state()
        self._build_menu()

    def _open_settings(self, _) -> None:
        if self._settings_proc is not None and self._settings_proc.poll() is None:
            return

        try:
            self._settings_proc = subprocess.Popen([sys.executable, str(WINDOW_SCRIPT), SETTINGS_URL, "timerk - 設定"])
        except Exception as e:
            rumps.notification("timerk", "設定画面の起動失敗", str(e))

    def _open_report(self, _) -> None:
        if self._report_proc is not None and self._report_proc.poll() is None:
            return

        try:
            self._report_proc = subprocess.Popen([sys.executable, str(WINDOW_SCRIPT), REPORT_URL, "timerk - レポート"])
        except Exception as e:
            rumps.notification("timerk", "レポート画面の起動失敗", str(e))

    # --- Tick ---

    def _tick(self, _) -> None:
        if self._settings_proc is not None and self._settings_proc.poll() is not None:
            self._settings_proc = None
            self._refresh_state()
            self._build_menu()

        if self._report_proc is not None and self._report_proc.poll() is not None:
            self._report_proc = None

        button = self._nsapp.nsstatusitem.button()

        if self.active_started_at is None:
            button.setAttributedTitle_(NSMutableAttributedString.alloc().initWithString_("⏱"))
            return

        elapsed = int((datetime.now() - self.active_started_at).total_seconds())

        if self.show_hours:
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            if self.show_seconds:
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                time_str = f"{hours:02d}:{minutes:02d}"
        else:
            minutes = elapsed // 60
            seconds = elapsed % 60
            if self.show_seconds:
                time_str = f"{minutes:02d}:{seconds:02d}"
            else:
                time_str = f"{minutes:02d}"

        color_hex = DEFAULT_HEX
        if self.active_project_id is not None:
            proj = next(
                (project for project in self._projects if project["id"] == self.active_project_id),
                None,
            )
            if proj is not None:
                color_hex = proj.get("color", DEFAULT_HEX)

        title = f"{CIRCLE} {time_str}"
        attr = _colored_circle_attributed(title, color_hex)
        button.setAttributedTitle_(attr)


if __name__ == "__main__":
    TimerkApp().run()
