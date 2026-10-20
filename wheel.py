import math

from PySide6.QtCore import QElapsedTimer, QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import (
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontMetrics,
    QGuiApplication,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import QWidget

from theme import METAL
from winapi import VK_LBUTTON, get_async_state, prepare_overlay

NOMINAL = 500.0
R_OUT = 218.0
R_IN = 86.0
HUB = 76.0
START = -90.0


def _ease_out_cubic(value):
    return 1.0 - (1.0 - value) ** 3


def _ease_out_back(value):
    c1 = 1.70158
    c3 = c1 + 1.0
    return 1.0 + c3 * (value - 1.0) ** 3 + c1 * (value - 1.0) ** 2


class RadialMenu(QWidget):
    chosen = Signal(str)
    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(None)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.NoDropShadowWindowHint
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setWindowTitle("QMessages")

        self._items = []
        self._hover = []
        self._hover_target = -1
        self._open_t = 0.0
        self._closing = False
        self._visible = False
        self._size = int(NOMINAL)
        self._k = 1.0
        self._idle = 0.0
        self._left_down = False
        self._accent = QColor(METAL["accent"])
        self._accent_secondary = QColor(METAL["accent_hover"])

        self._clock = QElapsedTimer()
        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._tick)

    def show_menu(self, items):
        if not items:
            return
        self._items = list(items)
        count = len(self._items)
        self._hover = [0.0] * count
        self._hover_target = -1
        self._open_t = 0.0
        self._closing = False
        self._visible = True
        self._left_down = get_async_state(VK_LBUTTON)

        screen = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
        if screen is None:
            return
        area = screen.geometry()

        size = int(min(NOMINAL, area.width() * 0.86, area.height() * 0.86))
        size = max(320, size)
        self._size = size
        self._k = size / NOMINAL

        half = size / 2.0
        cursor = self._cursor_pos()
        left = area.left() + half
        right = area.left() + area.width() - half
        top = area.top() + half
        bottom = area.top() + area.height() - half
        cx = min(max(cursor.x(), left), right)
        cy = min(max(cursor.y(), top), bottom)

        self.setGeometry(int(round(cx - half)), int(round(cy - half)), size, size)
        self.show()
        self.raise_()
        prepare_overlay(int(self.winId()))

        self._idle = 0.0
        self._clock.restart()
        self._timer.start()
        self._update_hover()
        self.update()

    def commit(self):
        if not self._visible or self._closing:
            return
        if self._hover_target >= 0:
            self._choose(self._hover_target)
        else:
            self.dismiss()

    def dismiss(self):
        if not self._visible or self._closing:
            return
        self._closing = True
        self._timer.start()
        if not self._clock.isValid():
            self._clock.start()

    def _cursor_pos(self):
        return QCursor.pos()

    def _tick(self):
        if not self._visible:
            self._timer.stop()
            return
        elapsed = self._clock.restart() / 1000.0
        dt = min(0.05, max(0.001, elapsed))
        self._idle = (self._idle + dt * 24.0) % 360.0

        if self._closing:
            self._open_t -= dt * 7.5
            if self._open_t <= 0.0:
                self._open_t = 0.0
                self._visible = False
                self._closing = False
                self._timer.stop()
                self.hide()
                self.closed.emit()
                return
        else:
            self._open_t = min(1.0, self._open_t + dt * 6.5)
            self._update_hover()

        count = len(self._items)
        if count:
            target = self._hover_target
            for index in range(count):
                goal = 1.0 if index == target else 0.0
                rate = 1.0 - math.exp(-dt * 18.0)
                self._hover[index] += (goal - self._hover[index]) * rate
        self.update()

    def _update_hover(self):
        if not self._items or self._closing:
            return
        geometry = self.geometry()
        cursor = self._cursor_pos()
        dx = cursor.x() - geometry.left() - self._size / 2.0
        dy = cursor.y() - geometry.top() - self._size / 2.0
        distance = math.hypot(dx, dy)
        k = self._k

        if distance < (R_IN + 2.0) * k or distance > (R_OUT + 120.0) * k:
            target = -1
        else:
            angle = math.degrees(math.atan2(dy, dx))
            relative = (angle - START) % 360.0
            step = 360.0 / len(self._items)
            target = int(relative // step) % len(self._items)
        self._hover_target = target

    def _choose(self, index):
        if not self._visible or self._closing:
            return
        if index < 0 or index >= len(self._items):
            return
        self._hover_target = index
        self.chosen.emit(self._items[index].text)
        self.dismiss()

    def mousePressEvent(self, event):
        if not self._visible or self._closing:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self._update_hover()
            if self._hover_target >= 0:
                self._choose(self._hover_target)
            else:
                self.dismiss()
        elif event.button() == Qt.MouseButton.RightButton:
            self.dismiss()

    def paintEvent(self, event):
        if not self._items or self._open_t <= 0.0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.setOpacity(min(1.0, self._open_t * 1.5))

        k = self._k
        center = QPointF(self._size / 2.0, self._size / 2.0)
        eased = _ease_out_cubic(self._open_t)
        scale = 0.9 + 0.1 * _ease_out_back(eased)
        painter.translate(center)
        painter.scale(scale, scale)
        painter.translate(-center)

        self._draw_backdrop(painter, center, k)
        self._draw_sectors(painter, center, k)
        self._draw_hub(painter, center, k)

    def _draw_backdrop(self, painter, center, k):
        radius = (R_OUT + 26.0) * k

        glow = QRadialGradient(center, radius)
        accent = self._accent
        glow.setColorAt(0.0, QColor(accent.red(), accent.green(), accent.blue(), 30))
        glow.setColorAt(0.55, QColor(accent.red(), accent.green(), accent.blue(), 12))
        glow.setColorAt(1.0, QColor(accent.red(), accent.green(), accent.blue(), 0))
        painter.setBrush(glow)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, radius, radius)

        disc = QRadialGradient(center, (R_OUT + 6.0) * k)
        disc.setColorAt(0.0, QColor(32, 32, 32, 246))
        disc.setColorAt(0.62, QColor(42, 42, 42, 242))
        disc.setColorAt(0.88, QColor(42, 42, 42, 232))
        disc.setColorAt(0.97, QColor(42, 42, 42, 190))
        disc.setColorAt(1.0, QColor(42, 42, 42, 0))
        painter.setBrush(disc)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, (R_OUT + 8.0) * k, (R_OUT + 8.0) * k)

        ring = QConicalGradient(center, self._idle)
        accent = self._accent
        secondary = self._accent_secondary
        ring.setColorAt(0.0, QColor(accent.red(), accent.green(), accent.blue(), 0))
        ring.setColorAt(0.16, QColor(accent.red(), accent.green(), accent.blue(), 130))
        ring.setColorAt(0.28, QColor(secondary.red(), secondary.green(), secondary.blue(), 40))
        ring.setColorAt(0.44, QColor(accent.red(), accent.green(), accent.blue(), 0))
        ring.setColorAt(0.70, QColor(secondary.red(), secondary.green(), secondary.blue(), 90))
        ring.setColorAt(0.84, QColor(accent.red(), accent.green(), accent.blue(), 0))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(ring, max(1.0, 1.6 * k)))
        painter.drawEllipse(center, (R_OUT + 4.0) * k, (R_OUT + 4.0) * k)

    def _sector_path(self, center, inner, outer, start, end):
        rect_outer = QRectF(center.x() - outer, center.y() - outer, outer * 2.0, outer * 2.0)
        rect_inner = QRectF(center.x() - inner, center.y() - inner, inner * 2.0, inner * 2.0)
        span = end - start
        path = QPainterPath()
        path.arcMoveTo(rect_outer, -start)
        path.arcTo(rect_outer, -start, -span)
        path.arcTo(rect_inner, -end, span)
        path.closeSubpath()
        return path

    def _draw_sectors(self, painter, center, k):
        count = len(self._items)
        step = 360.0 / count
        gap = min(4.2, max(1.8, step * 0.07))
        font = QFont("Segoe UI")
        font.setWeight(QFont.Weight.DemiBold)
        label_font_size = 12 if count <= 6 else 11 if count <= 10 else 10

        for index, item in enumerate(self._items):
            hover = self._hover[index]
            start = START + index * step + gap / 2.0
            end = START + (index + 1) * step - gap / 2.0
            inner = (R_IN + 2.0 * hover) * k
            outer = (R_OUT - 8.0 + 8.0 * hover) * k
            path = self._sector_path(center, inner, outer, start, end)

            accent = self._accent
            if hover > 0.004:
                fill = QColor(accent)
                fill.setAlpha(int(16 + 70 * hover))
            else:
                fill = QColor(255, 255, 255, 22 if index % 2 == 0 else 14)

            gradient = QRadialGradient(center, max(1.0, outer))
            gradient.setColorAt(0.0, QColor(fill.red(), fill.green(), fill.blue(), int(fill.alpha() * 0.35)))
            gradient.setColorAt(0.55, QColor(fill.red(), fill.green(), fill.blue(), int(fill.alpha() * 0.75)))
            gradient.setColorAt(1.0, fill)
            painter.setBrush(gradient)

            if hover > 0.004:
                stroke = QColor(accent)
                stroke.setAlpha(int(40 + 165 * hover))
                width = 1.0 + 1.2 * hover
            else:
                stroke = QColor(255, 255, 255, 26)
                width = 1.0
            painter.setPen(QPen(stroke, max(0.8, width * k)))
            painter.drawPath(path)

            middle = math.radians((start + end) / 2.0)
            label_radius = (inner + outer) / 2.0
            pos = QPointF(
                center.x() + math.cos(middle) * label_radius,
                center.y() + math.sin(middle) * label_radius,
            )
            available = max(
                30.0 * k,
                2.0 * label_radius * math.sin(math.radians(step / 2.0)) - 22.0 * k,
            )
            size = int((label_font_size + 1.0 * hover) * k)
            font.setPixelSize(max(8, size))
            painter.setFont(font)
            metrics = QFontMetrics(font)
            text = metrics.elidedText(item.label, Qt.TextElideMode.ElideRight, int(available))
            rect = QRectF(pos.x() - available / 2.0, pos.y() - 12.0 * k, available, 24.0 * k)

            painter.setPen(QColor(0, 0, 0, 120))
            painter.drawText(rect.translated(0.0, 1.0 * k), int(Qt.AlignmentFlag.AlignCenter), text)
            painter.setPen(QColor(212, 212, 212, int(196 + 59 * hover)))
            painter.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), text)

            if hover > 0.05:
                dot_radius = outer + 7.0 * k
                dot = QPointF(
                    center.x() + math.cos(middle) * dot_radius,
                    center.y() + math.sin(middle) * dot_radius,
                )
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(accent.red(), accent.green(), accent.blue(), int(60 * hover)))
                painter.drawEllipse(dot, 7.0 * k, 7.0 * k)
                painter.setBrush(QColor(accent.red(), accent.green(), accent.blue(), int(235 * hover)))
                painter.drawEllipse(dot, 2.4 * k, 2.4 * k)

    def _draw_hub(self, painter, center, k):
        hub = HUB * k

        shadow = QRadialGradient(center, hub + 22.0 * k)
        shadow.setColorAt(0.74, QColor(0, 0, 0, 0))
        shadow.setColorAt(0.84, QColor(0, 0, 0, 110))
        shadow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(shadow)
        painter.drawEllipse(center, hub + 22.0 * k, hub + 22.0 * k)

        painter.setBrush(QColor(42, 42, 42, 238))
        painter.setPen(QPen(QColor(78, 78, 78, 200), max(1.0, 1.2 * k)))
        painter.drawEllipse(center, hub, hub)

        accent = self._accent
        arc_rect = QRectF(center.x() - hub, center.y() - hub, hub * 2.0, hub * 2.0)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(
            QPen(
                QColor(accent.red(), accent.green(), accent.blue(), 170),
                max(1.4, 2.0 * k),
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        painter.drawArc(arc_rect, 90 * 16, -54 * 16)

        clip = QPainterPath()
        clip.addEllipse(center, hub - 5.0 * k, hub - 5.0 * k)
        painter.save()
        painter.setClipPath(clip)

        index = self._hover_target
        if 0 <= index < len(self._items):
            item = self._items[index]
            label_font = QFont("Segoe UI")
            label_font.setPixelSize(max(8, int(9.0 * k)))
            label_font.setWeight(QFont.Weight.DemiBold)
            label_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.4 * k)
            painter.setFont(label_font)
            painter.setPen(QColor(accent.red(), accent.green(), accent.blue(), 235))
            label_rect = QRectF(
                center.x() - hub + 20.0 * k,
                center.y() - hub + 26.0 * k,
                hub * 2.0 - 40.0 * k,
                15.0 * k,
            )
            metrics = QFontMetrics(label_font)
            label = metrics.elidedText(
                item.label.upper(), Qt.TextElideMode.ElideRight, int(label_rect.width())
            )
            painter.drawText(label_rect, int(Qt.AlignmentFlag.AlignCenter), label)

            text = item.text.strip()
            if len(text) > 110:
                text = text[:109].rstrip() + "…"
            body_font = QFont("Segoe UI")
            length = len(text)
            size = 13 if length <= 22 else 12 if length <= 48 else 11 if length <= 78 else 10
            body_font.setPixelSize(max(8, int(size * k)))
            body_font.setWeight(QFont.Weight.Medium)
            painter.setFont(body_font)
            painter.setPen(QColor(212, 212, 212, 246))
            body_rect = QRectF(
                center.x() - hub + 18.0 * k,
                center.y() - hub + 46.0 * k,
                hub * 2.0 - 36.0 * k,
                hub * 2.0 - 70.0 * k,
            )
            painter.drawText(
                body_rect,
                int(Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap),
                text,
            )
        else:
            painter.setPen(Qt.PenStyle.NoPen)
            for dot_index in range(8):
                angle = math.radians(dot_index * 45.0 + self._idle * 0.8)
                x = center.x() + math.cos(angle) * 25.0 * k
                y = center.y() - 8.0 * k + math.sin(angle) * 25.0 * k
                painter.setBrush(QColor(accent.red(), accent.green(), accent.blue(), 130))
                painter.drawEllipse(QPointF(x, y), 2.2 * k, 2.2 * k)
            painter.setBrush(QColor(accent.red(), accent.green(), accent.blue(), 235))
            painter.drawEllipse(QPointF(center.x(), center.y() - 8.0 * k), 3.4 * k, 3.4 * k)

            caption_font = QFont("Segoe UI")
            caption_font.setPixelSize(max(8, int(9.0 * k)))
            caption_font.setWeight(QFont.Weight.DemiBold)
            caption_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2.0 * k)
            painter.setFont(caption_font)
            painter.setPen(QColor(144, 144, 144, 165))
            caption_rect = QRectF(
                center.x() - hub + 16.0 * k,
                center.y() + 34.0 * k,
                hub * 2.0 - 32.0 * k,
                18.0 * k,
            )
            painter.drawText(caption_rect, int(Qt.AlignmentFlag.AlignCenter), "ВЫБЕРИ")

        painter.restore()

    def hideEvent(self, event):
        self._timer.stop()
        super().hideEvent(event)
