import copy

from PySide6.QtCore import QRectF, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QKeySequence, QPainter, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QStyle,
    QStyledItemDelegate,
    QVBoxLayout,
)

from config import make_label
from hotkeys import parse_hotkey
from theme import METAL, settings_qss
from ui_icons import apply_icon
from winapi import enable_dark_titlebar


def _card():
    frame = QFrame()
    frame.setObjectName("card")
    return frame


def _icon_only(button, name, color=None):
    if apply_icon(button, name, color):
        button.setText("")


class SnippetDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._label_font = QFont("Segoe UI")
        self._label_font.setPixelSize(13)
        self._label_font.setWeight(QFont.Weight.DemiBold)
        self._preview_font = QFont("Segoe UI")
        self._preview_font.setPixelSize(11)

    def sizeHint(self, option, index):
        return QSize(option.rect.width(), 56)

    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = option.rect.adjusted(3, 2, -3, -2)
        selected = bool(option.state & QStyle.StateFlag.State_Selected)
        hovered = bool(option.state & QStyle.StateFlag.State_MouseOver)

        if selected:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(METAL["accent"]))
            painter.drawRoundedRect(rect, 9, 9)
        elif hovered:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(METAL["surface_alt"]))
            painter.drawRoundedRect(rect, 9, 9)

        label = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
        preview = str(index.data(Qt.ItemDataRole.UserRole) or "")
        preview = " ".join(preview.split()) or "Пусто"

        text_rect = QRectF(rect.left() + 12, rect.top() + 8, rect.width() - 24, 18)
        painter.setFont(self._label_font)
        metrics = QFontMetrics(self._label_font)
        label_text = metrics.elidedText(
            label or "Без названия", Qt.TextElideMode.ElideRight, int(text_rect.width())
        )
        painter.setPen(QColor(METAL["accent_text"]) if selected else QColor(METAL["text"]))
        painter.drawText(text_rect, int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter), label_text)

        preview_rect = QRectF(rect.left() + 12, rect.top() + 28, rect.width() - 24, 16)
        painter.setFont(self._preview_font)
        metrics = QFontMetrics(self._preview_font)
        preview_text = metrics.elidedText(
            preview, Qt.TextElideMode.ElideRight, int(preview_rect.width())
        )
        painter.setPen(QColor(METAL["accent_text"]) if selected else QColor(METAL["muted"]))
        painter.drawText(
            preview_rect,
            int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
            preview_text,
        )
        painter.restore()


class HotkeyButton(QPushButton):
    spec_changed = Signal(str)
    capture_started = Signal()
    capture_finished = Signal()

    MODIFIER_KEYS = (
        Qt.Key.Key_Control,
        Qt.Key.Key_Shift,
        Qt.Key.Key_Alt,
        Qt.Key.Key_Meta,
    )

    KEY_NAMES = {
        Qt.Key.Key_Space: "space",
        Qt.Key.Key_Tab: "tab",
        Qt.Key.Key_Backtab: "tab",
        Qt.Key.Key_CapsLock: "caps_lock",
        Qt.Key.Key_Escape: "esc",
        Qt.Key.Key_Return: "enter",
        Qt.Key.Key_Enter: "enter",
        Qt.Key.Key_Backspace: "backspace",
        Qt.Key.Key_Delete: "delete",
        Qt.Key.Key_Insert: "insert",
        Qt.Key.Key_Home: "home",
        Qt.Key.Key_End: "end",
        Qt.Key.Key_PageUp: "page_up",
        Qt.Key.Key_PageDown: "page_down",
        Qt.Key.Key_Left: "left",
        Qt.Key.Key_Up: "up",
        Qt.Key.Key_Right: "right",
        Qt.Key.Key_Down: "down",
        Qt.Key.Key_Print: "print_screen",
        Qt.Key.Key_NumLock: "num_lock",
        Qt.Key.Key_ScrollLock: "scroll_lock",
        Qt.Key.Key_Menu: "menu",
        Qt.Key.Key_QuoteLeft: "`",
        Qt.Key.Key_AsciiTilde: "`",
        Qt.Key.Key_Minus: "-",
        Qt.Key.Key_Underscore: "-",
        Qt.Key.Key_Equal: "=",
        Qt.Key.Key_Plus: "=",
        Qt.Key.Key_BracketLeft: "[",
        Qt.Key.Key_BraceLeft: "[",
        Qt.Key.Key_BracketRight: "]",
        Qt.Key.Key_BraceRight: "]",
        Qt.Key.Key_Backslash: "\\",
        Qt.Key.Key_Bar: "\\",
        Qt.Key.Key_Semicolon: ";",
        Qt.Key.Key_Colon: ";",
        Qt.Key.Key_Apostrophe: "'",
        Qt.Key.Key_QuoteDbl: "'",
        Qt.Key.Key_Comma: ",",
        Qt.Key.Key_Less: ",",
        Qt.Key.Key_Period: ".",
        Qt.Key.Key_Greater: ".",
        Qt.Key.Key_Slash: "/",
        Qt.Key.Key_Question: "/",
        Qt.Key.Key_Exclam: "1",
        Qt.Key.Key_At: "2",
        Qt.Key.Key_NumberSign: "3",
        Qt.Key.Key_Dollar: "4",
        Qt.Key.Key_Percent: "5",
        Qt.Key.Key_AsciiCircum: "6",
        Qt.Key.Key_Ampersand: "7",
        Qt.Key.Key_Asterisk: "8",
        Qt.Key.Key_ParenLeft: "9",
        Qt.Key.Key_ParenRight: "0",
    }

    def __init__(self, spec, parent=None):
        super().__init__(parent)
        self.setObjectName("keycap")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setToolTip("Нажмите и введите комбинацию")
        self._spec = "caps_lock"
        self._capturing = False
        self._old_text = ""
        self.set_spec(spec)

    def spec(self):
        return self._spec

    def set_spec(self, spec):
        try:
            display = parse_hotkey(spec)[4]
        except ValueError:
            display = str(spec)
        self._spec = spec
        self.setText(display)

    def start_capture(self):
        if self._capturing:
            return
        self._capturing = True
        self._old_text = self.text()
        self.setText("Нажмите комбинацию…")
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        self.capture_started.emit()

    def cancel_capture(self):
        if not self._capturing:
            return
        self._capturing = False
        self.setText(self._old_text)
        self.capture_finished.emit()

    def _finish(self, key_name, modifiers):
        names = []
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            names.append("ctrl")
        if modifiers & Qt.KeyboardModifier.AltModifier:
            names.append("alt")
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            names.append("shift")
        if modifiers & Qt.KeyboardModifier.MetaModifier:
            names.append("win")
        spec = "+".join(names + [key_name])
        try:
            display = parse_hotkey(spec)[4]
        except ValueError:
            self._show_unsupported()
            return
        self._spec = spec
        self._capturing = False
        self.setText(display)
        self.spec_changed.emit(spec)
        self.capture_finished.emit()

    def _show_unsupported(self):
        self.setText("Не поддерживается")
        QTimer.singleShot(900, self._restore_capture_text)

    def _restore_capture_text(self):
        if self._capturing:
            self.setText("Нажмите комбинацию…")

    def _modifier_hint(self, modifiers):
        names = []
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            names.append("Ctrl")
        if modifiers & Qt.KeyboardModifier.AltModifier:
            names.append("Alt")
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            names.append("Shift")
        if modifiers & Qt.KeyboardModifier.MetaModifier:
            names.append("Win")
        return " + ".join(names + ["…"]) if names else "Нажмите комбинацию…"

    def _key_name(self, key):
        if Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
            return chr(key).lower()
        if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
            return chr(key)
        if Qt.Key.Key_F1 <= key <= Qt.Key.Key_F24:
            return f"f{key - Qt.Key.Key_F1 + 1}"
        return self.KEY_NAMES.get(key)

    def keyPressEvent(self, event):
        if not self._capturing:
            super().keyPressEvent(event)
            return
        key = event.key()
        if key == Qt.Key.Key_Escape:
            self.cancel_capture()
            event.accept()
            return
        if key in self.MODIFIER_KEYS:
            self.setText(self._modifier_hint(event.modifiers()))
            event.accept()
            return
        name = self._key_name(key)
        if not name:
            self._show_unsupported()
            event.accept()
            return
        self._finish(name, event.modifiers())
        event.accept()

    def mousePressEvent(self, event):
        if self._capturing:
            if event.button() == Qt.MouseButton.RightButton:
                self.cancel_capture()
                event.accept()
                return
            if event.button() == Qt.MouseButton.MiddleButton:
                self._finish("middle", QApplication.keyboardModifiers())
                event.accept()
                return
            if event.button() == Qt.MouseButton.BackButton:
                self._finish("mouse4", QApplication.keyboardModifiers())
                event.accept()
                return
            if event.button() == Qt.MouseButton.ForwardButton:
                self._finish("mouse5", QApplication.keyboardModifiers())
                event.accept()
                return
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_capture()
            event.accept()
            return
        super().mousePressEvent(event)

    def focusOutEvent(self, event):
        if self._capturing:
            self.cancel_capture()
        super().focusOutEvent(event)


class SettingsWindow(QDialog):
    saved = Signal(dict)

    def __init__(self, config, store, parent=None):
        super().__init__(parent)
        self._store = store
        self._config = copy.deepcopy(config)
        try:
            parse_hotkey(self._config["hotkey"])
        except (KeyError, ValueError):
            self._config["hotkey"] = "caps_lock"

        self._snippets = [dict(item) for item in self._config.get("snippets", [])]
        if not self._snippets:
            self._snippets.append({"label": "", "text": ""})
        self._current = -1
        self._loading = False
        self._dirty = False
        self._titlebar_done = False

        self.setWindowTitle("Настройки")
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.resize(1000, 700)
        self.setMinimumSize(880, 620)

        self.setStyleSheet(settings_qss())
        self.setWindowIcon(QApplication.windowIcon())

        self._build()
        self._reload_list(0)
        self._set_dirty(False)

        self._shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self._shortcut.activated.connect(self._save)
        self.hotkey_button.capture_started.connect(
            lambda: self._shortcut.setEnabled(False)
        )
        self.hotkey_button.capture_finished.connect(
            lambda: self._shortcut.setEnabled(True)
        )

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 18)
        root.setSpacing(14)

        header = QHBoxLayout()
        titles = QVBoxLayout()
        titles.setSpacing(2)
        title = QLabel("QMessages")
        title.setObjectName("title")
        subtitle = QLabel("Заготовки и быстрый доступ")
        subtitle.setObjectName("subtitle")
        titles.addWidget(title)
        titles.addWidget(subtitle)
        header.addLayout(titles)
        header.addStretch()
        root.addLayout(header)

        root.addWidget(self._build_settings_card())
        root.addLayout(self._build_body(), 1)
        root.addLayout(self._build_footer())

    def _build_settings_card(self):
        card = _card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        top = QHBoxLayout()
        top.setSpacing(10)
        label = QLabel("Горячая клавиша")
        label.setObjectName("section")
        top.addWidget(label)
        self.hotkey_button = HotkeyButton(self._config["hotkey"])
        self.hotkey_button.spec_changed.connect(lambda _spec: self._set_dirty(True))
        top.addWidget(self.hotkey_button)
        reset = QPushButton("Сброс")
        reset.setObjectName("ghost")
        reset.setToolTip("Вернуть CapsLock")
        apply_icon(reset, "reset")
        reset.clicked.connect(self._reset_hotkey)
        top.addWidget(reset)
        hint = QLabel("Нажмите на клавишу и введите комбинацию. Она работает глобально.")
        hint.setObjectName("hint")
        top.addWidget(hint, 1)
        layout.addLayout(top)

        options = QGridLayout()
        options.setHorizontalSpacing(14)
        options.setVerticalSpacing(8)

        delay_label = QLabel("Задержка")
        delay_label.setObjectName("hint")
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 1000)
        self.delay_spin.setSingleStep(10)
        self.delay_spin.setSuffix(" мс")
        self.delay_spin.setFixedWidth(96)
        self.delay_spin.setToolTip("Сколько держать бинд до появления колеса")
        options.addWidget(delay_label, 0, 0)
        options.addWidget(self.delay_spin, 0, 1)

        self.release_check = QCheckBox("Выбор при отпускании")
        options.addWidget(self.release_check, 0, 2)

        self.enter_check = QCheckBox("Отправлять сразу (Enter)")
        self.enter_check.setToolTip("После вставки нажать Enter")
        options.addWidget(self.enter_check, 0, 3)

        paste_label = QLabel("Вставка")
        paste_label.setObjectName("hint")
        self.paste_combo = QComboBox()
        self.paste_combo.addItem("Буфер обмена (Ctrl+V)", "clipboard")
        self.paste_combo.addItem("Посимвольный ввод", "type")
        self.paste_combo.setFixedWidth(210)
        options.addWidget(paste_label, 1, 0)
        options.addWidget(self.paste_combo, 1, 1, 1, 2)

        self.restore_check = QCheckBox("Возвращать прежний буфер обмена")
        options.addWidget(self.restore_check, 1, 3)

        options.setColumnStretch(4, 1)
        layout.addLayout(options)

        self.delay_spin.setValue(self._config["hold_delay_ms"])
        self.release_check.setChecked(self._config["select_on_release"])
        self.enter_check.setChecked(self._config["press_enter"])
        self.restore_check.setChecked(self._config["restore_clipboard"])
        paste_index = self.paste_combo.findData(self._config["paste_method"])
        self.paste_combo.setCurrentIndex(max(0, paste_index))

        self.delay_spin.valueChanged.connect(lambda _value: self._set_dirty(True))
        self.release_check.toggled.connect(lambda _value: self._set_dirty(True))
        self.enter_check.toggled.connect(lambda _value: self._set_dirty(True))
        self.restore_check.toggled.connect(lambda _value: self._set_dirty(True))
        self.paste_combo.currentIndexChanged.connect(lambda _value: self._set_dirty(True))
        return card

    def _build_body(self):
        body = QHBoxLayout()
        body.setSpacing(14)

        left = _card()
        left.setFixedWidth(330)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(14, 14, 14, 12)
        left_layout.setSpacing(8)

        head = QHBoxLayout()
        title = QLabel("Заготовки")
        title.setObjectName("section")
        self.count_label = QLabel("")
        self.count_label.setObjectName("count")
        head.addWidget(title)
        head.addStretch()
        head.addWidget(self.count_label)
        left_layout.addLayout(head)

        self.list = QListWidget()
        self.list.setItemDelegate(SnippetDelegate(self.list))
        self.list.setMouseTracking(True)
        self.list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list.currentRowChanged.connect(self._on_row_changed)
        left_layout.addWidget(self.list, 1)

        tools = QHBoxLayout()
        tools.setSpacing(6)
        add_button = QPushButton("Добавить")
        apply_icon(add_button, "add")
        add_button.clicked.connect(self._add)
        delete_button = QPushButton("Удалить")
        apply_icon(delete_button, "delete")
        delete_button.clicked.connect(self._delete)
        up_button = QPushButton("↑")
        up_button.setToolTip("Выше")
        _icon_only(up_button, "up")
        up_button.clicked.connect(lambda: self._move(-1))
        down_button = QPushButton("↓")
        down_button.setToolTip("Ниже")
        _icon_only(down_button, "down")
        down_button.clicked.connect(lambda: self._move(1))
        tools.addWidget(add_button)
        tools.addWidget(delete_button)
        tools.addStretch()
        tools.addWidget(up_button)
        tools.addWidget(down_button)
        left_layout.addLayout(tools)

        right = _card()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(18, 14, 18, 16)
        right_layout.setSpacing(8)

        label_title = QLabel("Название на колесе")
        label_title.setObjectName("section")
        right_layout.addWidget(label_title)

        self.label_edit = QLineEdit()
        self.label_edit.setPlaceholderText("Например: Привет")
        self.label_edit.setMaxLength(40)
        right_layout.addWidget(self.label_edit)

        text_head = QHBoxLayout()
        text_title = QLabel("Текст сообщения")
        text_title.setObjectName("section")
        self.chars_label = QLabel("0 симв.")
        self.chars_label.setObjectName("count")
        text_head.addWidget(text_title)
        text_head.addStretch()
        text_head.addWidget(self.chars_label)
        right_layout.addLayout(text_head)

        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText("Текст, который вставится в чат…")
        self.text_edit.setTabChangesFocus(True)
        right_layout.addWidget(self.text_edit, 1)

        editor_tools = QHBoxLayout()
        from_clipboard = QPushButton("Вставить из буфера")
        from_clipboard.setObjectName("ghost")
        apply_icon(from_clipboard, "paste")
        from_clipboard.clicked.connect(self._paste_from_clipboard)
        editor_tools.addWidget(from_clipboard)
        editor_tools.addStretch()
        right_layout.addLayout(editor_tools)

        self.label_edit.textEdited.connect(self._store_current)
        self.text_edit.textChanged.connect(self._store_current)

        body.addWidget(left)
        body.addWidget(right, 1)
        return body

    def _build_footer(self):
        footer = QHBoxLayout()
        footer.setSpacing(10)
        self.status_label = QLabel("")
        self.status_label.setObjectName("status")
        footer.addWidget(self.status_label, 1)
        cancel_button = QPushButton("Отмена")
        apply_icon(cancel_button, "cancel")
        cancel_button.clicked.connect(self.reject)
        save_button = QPushButton("Сохранить")
        save_button.setObjectName("primary")
        apply_icon(save_button, "save", METAL["act_text"])
        save_button.clicked.connect(self._save)
        footer.addWidget(cancel_button)
        footer.addWidget(save_button)
        return footer

    def _reset_hotkey(self):
        self.hotkey_button.cancel_capture()
        self.hotkey_button.set_spec("caps_lock")
        self._set_dirty(True)

    def _set_dirty(self, dirty):
        self._dirty = bool(dirty)
        self.status_label.setText(
            "Есть несохранённые изменения" if self._dirty else "Готово"
        )

    def _reload_list(self, select):
        self.list.blockSignals(True)
        self.list.clear()
        for snippet in self._snippets:
            preview = " ".join(snippet["text"].split())
            item = QListWidgetItem(snippet["label"] or "Без названия")
            item.setData(Qt.ItemDataRole.UserRole, preview)
            item.setSizeHint(QSize(0, 56))
            self.list.addItem(item)
        self.list.blockSignals(False)
        self.count_label.setText(f"{len(self._snippets)} / 16")
        index = max(0, min(select, len(self._snippets) - 1))
        self.list.setCurrentRow(index)
        self._current = index
        self._load(index)

    def _load(self, index):
        if not (0 <= index < len(self._snippets)):
            self._loading = True
            self.label_edit.clear()
            self.text_edit.clear()
            self._loading = False
            return
        snippet = self._snippets[index]
        self._loading = True
        self.label_edit.setText(snippet["label"])
        self.text_edit.setPlainText(snippet["text"])
        self.chars_label.setText(f"{len(snippet['text'])} симв.")
        self._loading = False

    def _on_row_changed(self, row):
        if row < 0:
            return
        self._store_current()
        self._current = row
        self._load(row)

    def _store_current(self):
        if self._loading or not (0 <= self._current < len(self._snippets)):
            return
        snippet = self._snippets[self._current]
        label = self.label_edit.text().strip()
        text = self.text_edit.toPlainText()
        self.chars_label.setText(f"{len(text)} симв.")
        if snippet["label"] == label and snippet["text"] == text:
            return
        snippet["label"] = label
        snippet["text"] = text
        item = self.list.item(self._current)
        if item is not None:
            item.setData(Qt.ItemDataRole.DisplayRole, label or "Без названия")
            item.setData(Qt.ItemDataRole.UserRole, " ".join(text.split()))
        self._set_dirty(True)

    def _add(self, text=""):
        if len(self._snippets) >= 16:
            QMessageBox.information(
                self, "QMessages", "Можно сохранить не больше 16 заготовок."
            )
            return False
        self._store_current()
        text = text or ""
        label = make_label(text) if text.strip() else ""
        if text.strip() and len(self._snippets) == 1 and not self._snippets[0]["text"].strip():
            self._snippets[0] = {"label": label, "text": text}
            self._reload_list(0)
            self._set_dirty(True)
            self.text_edit.setFocus()
            return True
        self._snippets.append({"label": label, "text": text})
        self._reload_list(len(self._snippets) - 1)
        self._set_dirty(True)
        self.text_edit.setFocus()
        return True

    def add_from_clipboard(self):
        text = QApplication.clipboard().text().strip()
        if not text:
            QMessageBox.information(self, "QMessages", "Буфер обмена пуст.")
            return False
        return self._add(text)

    def _delete(self):
        if not (0 <= self._current < len(self._snippets)):
            return
        self._snippets.pop(self._current)
        if not self._snippets:
            self._snippets.append({"label": "", "text": ""})
        self._reload_list(min(self._current, len(self._snippets) - 1))
        self._set_dirty(True)

    def _move(self, delta):
        index = self._current
        other = index + delta
        if not (0 <= index < len(self._snippets) and 0 <= other < len(self._snippets)):
            return
        self._store_current()
        self._snippets[index], self._snippets[other] = self._snippets[other], self._snippets[index]
        self._reload_list(other)
        self._set_dirty(True)

    def _paste_from_clipboard(self):
        text = QApplication.clipboard().text()
        if not text:
            return
        self.text_edit.setPlainText(text)
        self.text_edit.setFocus()
        self._store_current()

    def _save(self):
        self._store_current()
        for index, snippet in enumerate(self._snippets):
            if not snippet["text"].strip():
                QMessageBox.warning(
                    self,
                    "QMessages",
                    "У этой заготовки нет текста. Заполните его или удалите заготовку.",
                )
                self.list.setCurrentRow(index)
                self._current = index
                self._load(index)
                self.text_edit.setFocus()
                return
            if not snippet["label"].strip():
                snippet["label"] = make_label(snippet["text"])

        spec = self.hotkey_button.spec()
        try:
            parse_hotkey(spec)
        except ValueError as error:
            QMessageBox.warning(
                self, "QMessages", f"Некорректная горячая клавиша: {error}"
            )
            self.hotkey_button.start_capture()
            return

        config = copy.deepcopy(self._config)
        config["snippets"] = [
            {"label": snippet["label"].strip(), "text": snippet["text"]}
            for snippet in self._snippets
        ]
        config["hotkey"] = spec
        config["hold_delay_ms"] = self.delay_spin.value()
        config["select_on_release"] = self.release_check.isChecked()
        config["press_enter"] = self.enter_check.isChecked()
        config["restore_clipboard"] = self.restore_check.isChecked()
        config["paste_method"] = self.paste_combo.currentData()

        try:
            config = self._store.save(config)
        except OSError as error:
            QMessageBox.warning(
                self,
                "QMessages",
                f"Не удалось сохранить config.json:\n{error}",
            )
            return

        self._dirty = False
        self.saved.emit(config)
        self.accept()

    def showEvent(self, event):
        super().showEvent(event)
        if not self._titlebar_done:
            self._titlebar_done = True
            enable_dark_titlebar(int(self.winId()))
