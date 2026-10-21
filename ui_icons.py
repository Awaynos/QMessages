import sys
from functools import lru_cache
from pathlib import Path

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap

from theme import METAL

ICON_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / "icons"
ICON_SIZE = 16

ALIASES = {
    "add": ("plus",),
    "delete": ("trash", "trash-2"),
    "reset": ("restore", "rotate-ccw", "undo", "reload"),
    "up": ("chevron-up", "arrow-up"),
    "down": ("chevron-down", "arrow-down"),
    "paste": ("clipboard", "clipboard-text"),
    "cancel": ("x", "close"),
    "save": ("check", "check-circle"),
}

_renderer_class = None


def _renderer(path):
    global _renderer_class
    if _renderer_class is None:
        try:
            from PySide6.QtSvg import QSvgRenderer
        except ImportError:
            _renderer_class = False
        else:
            _renderer_class = QSvgRenderer
    if not _renderer_class:
        return None
    renderer = _renderer_class(str(path))
    return renderer if renderer.isValid() else None


def _find(name):
    for candidate in (name, *ALIASES.get(name, ())):
        for suffix in (".svg", ".png"):
            path = ICON_DIR / f"{candidate}{suffix}"
            if path.is_file():
                return path
    return None


def _tinted(path, size, color):
    scale = 2
    pixmap = QPixmap(size * scale, size * scale)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

    if path.suffix.lower() == ".svg":
        renderer = _renderer(path)
        if renderer is None:
            painter.end()
            return None
        renderer.render(painter, QRectF(0, 0, size * scale, size * scale))
    else:
        source = QPixmap(str(path))
        if source.isNull():
            painter.end()
            return None
        painter.drawPixmap(
            QRectF(0, 0, size * scale, size * scale),
            source,
            QRectF(source.rect()),
        )

    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color))
    painter.end()
    pixmap.setDevicePixelRatio(scale)
    return pixmap


@lru_cache(maxsize=128)
def _icon(name, color, size):
    path = _find(name)
    if path is None:
        return None
    normal = _tinted(path, size, color)
    if normal is None:
        return None
    icon = QIcon()
    icon.addPixmap(normal, QIcon.Mode.Normal)
    icon.addPixmap(
        _tinted(path, size, QColor(color).lighter(118).name()), QIcon.Mode.Active
    )
    icon.addPixmap(_tinted(path, size, METAL["muted"]), QIcon.Mode.Disabled)
    return icon


def ui_icon(name, color=None, size=ICON_SIZE):
    return _icon(name, color or METAL["text"], size)


def apply_icon(button, name, color=None, size=ICON_SIZE):
    icon = ui_icon(name, color, size)
    if icon is None:
        return False
    button.setIcon(icon)
    button.setIconSize(QSize(size, size))
    return True
