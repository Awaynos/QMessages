import ctypes
import math
import os
import sys
import traceback
from pathlib import Path

from PySide6.QtCore import QFileSystemWatcher, QObject, QPointF, Qt, QTimer
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from config import ConfigStore, app_dir, build_snippets, config_path
from hotkeys import HotkeyListener
from paste import paste_text
from settings import SettingsWindow
from wheel import RadialMenu
from theme import METAL, build_palette, tray_qss
from winapi import acquire_single_instance

MUTEX_NAME = "Local\\QMessages-7d2f4c1a"


def asset_path(name):
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", app_dir()))
    else:
        base = app_dir()
    return base / name


def make_icon(accent):
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setBrush(QColor(20, 23, 31, 245))
    painter.setPen(QPen(QColor(accent), 3))
    painter.drawEllipse(5, 5, 54, 54)
    painter.setPen(Qt.PenStyle.NoPen)
    for index in range(6):
        angle = math.radians(index * 60 - 90)
        x = 32 + math.cos(angle) * 17
        y = 32 + math.sin(angle) * 17
        painter.setBrush(QColor(accent))
        painter.drawEllipse(QPointF(x, y), 3.6, 3.6)
    painter.setBrush(QColor(246, 248, 252, 235))
    painter.drawEllipse(QPointF(32, 32), 4.0, 4.0)
    painter.end()
    return QIcon(pixmap)


class WheelApp(QObject):
    def __init__(self, app, dry_run=False):
        super().__init__()
        self._app = app
        self._dry_run = dry_run
        self._store = ConfigStore(config_path())
        self._config, self._config_error = self._store.load()
        self._items = build_snippets(self._config)
        self._listener = None
        self._tray = None
        self._settings = None
        self._hotkey_suspended = False

        self._menu = RadialMenu()
        self._menu.chosen.connect(self._on_chosen)
        self._menu.closed.connect(self._on_menu_closed)

        self._reload_timer = QTimer(self)
        self._reload_timer.setSingleShot(True)
        self._reload_timer.setInterval(350)
        self._reload_timer.timeout.connect(self._reload)

        self._watcher = QFileSystemWatcher(self)
        self._watcher.fileChanged.connect(self._on_file_changed)
        self._add_watch()

        self._build_tray()
        self._apply_hotkey()
        self._update_tray()

        if self._config_error:
            self._notify("config.json", self._config_error, warning=True)

    def _add_watch(self):
        path = str(self._store.path)
        if os.path.exists(path) and path not in self._watcher.files():
            self._watcher.addPath(path)

    def _on_file_changed(self, path):
        self._add_watch()
        self._reload_timer.start()

    def _build_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self._tray = QSystemTrayIcon(self)
        menu = QMenu()
        menu.setStyleSheet(tray_qss())
        show_action = QAction("Показать колесо", menu)
        show_action.triggered.connect(self._preview)
        clip_action = QAction("Сохранить из буфера", menu)
        clip_action.triggered.connect(lambda: self._open_settings(add_clipboard=True))
        settings_action = QAction("Настройки…", menu)
        settings_action.triggered.connect(lambda: self._open_settings())
        config_action = QAction("Открыть config.json", menu)
        config_action.triggered.connect(self._store.open_in_editor)
        reload_action = QAction("Перезагрузить настройки", menu)
        reload_action.triggered.connect(lambda: self._reload(notify=True))
        quit_action = QAction("Выход", menu)
        quit_action.triggered.connect(self._quit)
        menu.addAction(show_action)
        menu.addAction(clip_action)
        menu.addAction(settings_action)
        menu.addSeparator()
        menu.addAction(config_action)
        menu.addAction(reload_action)
        menu.addSeparator()
        menu.addAction(quit_action)
        self._tray.setContextMenu(menu)
        self._tray_menu = menu
        self._tray.setIcon(self._tray_icon())
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._open_settings()

    def _tray_icon(self):
        icon = QApplication.windowIcon()
        if icon.isNull():
            icon = make_icon(METAL["accent"])
        return icon

    def _update_tray(self):
        if not self._tray:
            return
        self._tray.setIcon(self._tray_icon())
        hotkey = self._listener.display if self._listener else "не задан"
        self._tray.setToolTip(f"QMessages — {hotkey}")

    def _notify(self, title, message, warning=False):
        if self._tray:
            icon = (
                QSystemTrayIcon.MessageIcon.Warning
                if warning
                else QSystemTrayIcon.MessageIcon.Information
            )
            self._tray.showMessage(title, message, icon, 4000)
        else:
            print(f"{title}: {message}", file=sys.stderr)

    def _apply_hotkey(self):
        if self._listener:
            self._listener.stop()
            self._listener.deleteLater()
            self._listener = None
        try:
            listener = HotkeyListener(
                self._config["hotkey"], self._config["hold_delay_ms"], self
            )
        except ValueError as error:
            self._notify("Бинд не применён", f"{error}. Использую CapsLock.", warning=True)
            listener = HotkeyListener("caps_lock", self._config["hold_delay_ms"], self)
        listener.activated.connect(
            self._on_activated, Qt.ConnectionType.QueuedConnection
        )
        listener.released.connect(
            self._on_released, Qt.ConnectionType.QueuedConnection
        )
        listener.cancelled.connect(
            self._on_cancelled, Qt.ConnectionType.QueuedConnection
        )
        listener.error.connect(self._on_hotkey_error)
        listener.start()
        self._listener = listener

    def _on_hotkey_error(self, message):
        self._notify("QMessages", message, warning=True)

    def _on_activated(self):
        if not self._items:
            return
        if self._listener:
            self._listener.menu_open = True
        self._menu.show_menu(self._items)

    def _on_released(self):
        if self._config["select_on_release"]:
            self._menu.commit()
        else:
            self._menu.dismiss()

    def _on_cancelled(self):
        self._menu.dismiss()

    def _on_chosen(self, text):
        if self._dry_run:
            self._notify("QMessages", text, warning=False)
            return
        paste_text(
            text,
            self._config["paste_method"],
            self._config["restore_clipboard"],
            self._config["restore_delay_ms"],
            self._config["press_enter"],
        )

    def _on_menu_closed(self):
        if self._listener:
            self._listener.menu_open = False

    def _preview(self):
        if not self._items:
            self._notify("QMessages", "В настройках нет заготовок", warning=True)
            return
        if self._listener:
            self._listener.menu_open = True
        self._menu.show_menu(self._items)

    def _open_settings(self, add_clipboard=False):
        if self._settings is not None:
            self._settings.show()
            self._settings.raise_()
            self._settings.activateWindow()
            if add_clipboard:
                self._settings.add_from_clipboard()
            return
        self._menu.dismiss()
        if self._listener:
            self._listener.stop()
        self._hotkey_suspended = True
        dialog = SettingsWindow(self._config, self._store)
        dialog.saved.connect(self._on_settings_saved)
        dialog.finished.connect(self._on_settings_closed)
        self._settings = dialog
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
        if add_clipboard:
            dialog.add_from_clipboard()

    def _on_settings_saved(self, config):
        self._config = config
        self._items = build_snippets(config)
        self._menu.dismiss()
        self._hotkey_suspended = False
        self._apply_hotkey()
        self._update_tray()
        self._notify("QMessages", "Настройки сохранены")

    def _on_settings_closed(self, result=0):
        dialog = self._settings
        self._settings = None
        if dialog is not None:
            dialog.deleteLater()
        if self._hotkey_suspended:
            self._hotkey_suspended = False
            self._apply_hotkey()
            self._update_tray()

    def _reload(self, notify=False):
        if self._settings is not None:
            if notify:
                self._notify("QMessages", "Сначала закройте окно настроек")
            return
        config, error = self._store.load()
        if error:
            self._notify("config.json", error, warning=True)
            return
        self._config = config
        self._items = build_snippets(config)
        self._menu.dismiss()
        self._apply_hotkey()
        self._update_tray()
        self._add_watch()
        if notify:
            self._notify("QMessages", "Настройки обновлены")

    def _quit(self):
        self._hotkey_suspended = False
        if self._settings is not None:
            self._settings.blockSignals(True)
            self._settings.close()
            self._settings = None
        if self._listener:
            self._listener.stop()
        if self._tray:
            self._tray.hide()
        self._app.quit()


def _install_excepthook():
    def handler(exc_type, exc_value, exc_tb):
        try:
            with open(app_dir() / "error.log", "a", encoding="utf-8") as log:
                traceback.print_exception(exc_type, exc_value, exc_tb, file=log)
        except OSError:
            pass
        sys.__excepthook__(exc_type, exc_value, exc_tb)

    sys.excepthook = handler


def _apply_palette(app):
    app.setStyle("Fusion")
    app.setPalette(build_palette())


def _set_app_id():
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Awaynos.QMessages")
    except Exception:
        pass


def main():
    _install_excepthook()

    app = QApplication(sys.argv)
    _set_app_id()
    _apply_palette(app)
    app.setApplicationName("QMessages")
    app.setApplicationDisplayName("QMessages")
    app_icon = QIcon(str(asset_path("icon.ico")))
    if app_icon.isNull():
        app_icon = make_icon(METAL["accent"])
    app.setWindowIcon(app_icon)
    app.setQuitOnLastWindowClosed(False)

    mutex = acquire_single_instance(MUTEX_NAME)
    if mutex is None:
        return 0

    dry_run = "--preview" in sys.argv[1:]
    settings_mode = "--settings" in sys.argv[1:]
    wheel_app = WheelApp(app, dry_run=dry_run)
    app._wheel_app = wheel_app

    if dry_run:
        QTimer.singleShot(600, wheel_app._preview)
    if settings_mode:
        QTimer.singleShot(600, wheel_app._open_settings)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
