from PySide6.QtCore import QMimeData, QTimer
from PySide6.QtWidgets import QApplication

from winapi import send_ctrl_v, send_enter, send_unicode_text


def _snapshot_clipboard(clipboard):
    try:
        mime = clipboard.mimeData()
        if mime is None:
            return None
        saved = QMimeData()
        for fmt in mime.formats():
            data = mime.data(fmt)
            if data is not None:
                saved.setData(fmt, data)
        return saved
    except Exception:
        return None


def paste_text(text, method="clipboard", restore=True, restore_delay_ms=800, press_enter=False):
    if not text:
        return
    if method == "type":
        def type_text():
            send_unicode_text(text)
            if press_enter:
                send_enter()

        QTimer.singleShot(120, type_text)
        return

    clipboard = QApplication.clipboard()
    saved = _snapshot_clipboard(clipboard) if restore else None
    clipboard.setText(text)
    QTimer.singleShot(120, send_ctrl_v)
    if press_enter:
        QTimer.singleShot(280, send_enter)

    if restore:
        def restore_previous():
            if clipboard.text() == text:
                if saved is None:
                    clipboard.clear()
                else:
                    clipboard.setMimeData(saved)

        QTimer.singleShot(120 + max(0, int(restore_delay_ms)), restore_previous)
