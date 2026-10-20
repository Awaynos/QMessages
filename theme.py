from PySide6.QtGui import QColor, QPalette

METAL = {
    "bg": "#202020",
    "surface": "#2a2a2a",
    "surface_alt": "#333333",
    "border": "#3d3d3d",
    "border_light": "#4e4e4e",
    "divider": "#2c2c2c",
    "text": "#d4d4d4",
    "muted": "#909090",
    "accent": "#b6b6b6",
    "accent_hover": "#c6c6c6",
    "accent_text": "#1c1c1c",
    "danger": "#c06a62",
    "btn_top": "#3b3b3b",
    "btn_bottom": "#303030",
    "btn_hover_top": "#454545",
    "btn_hover_bottom": "#393939",
    "btn_pressed_top": "#292929",
    "btn_pressed_bottom": "#353535",
    "act_top": "#cccccc",
    "act_bottom": "#a6a6a6",
    "act_hover_top": "#dadada",
    "act_hover_bottom": "#b4b4b4",
    "act_pressed_top": "#9a9a9a",
    "act_pressed_bottom": "#b2b2b2",
    "act_text": "#1c1c1c",
    "header_top": "#2f2f2f",
    "header_bottom": "#242424",
    "seg_on_top": "#b6b6b6",
    "seg_on_bottom": "#9c9c9c",
    "focus": "#b6b6b6",
}

SETTINGS_QSS = """
* {
    font-family: "Segoe UI", "Inter", "Noto Sans", sans-serif;
    outline: none;
}
QDialog {
    background: %(bg)s;
}
QLabel {
    color: %(text)s;
    background: transparent;
    font-size: 12px;
}
QLabel#title {
    color: %(text)s;
    font-size: 22px;
    font-weight: 700;
}
QLabel#subtitle {
    color: %(muted)s;
    font-size: 11px;
}
QLabel#section {
    color: %(muted)s;
    font-size: 10px;
    font-weight: 600;
}
QLabel#hint {
    color: %(muted)s;
    font-size: 11px;
}
QLabel#status {
    color: %(muted)s;
    font-size: 11px;
}
QLabel#count {
    color: %(muted)s;
    font-size: 10px;
}
QFrame#card {
    background: %(surface)s;
    border: 1px solid %(border)s;
    border-radius: 4px;
}
QLineEdit, QSpinBox {
    background: %(surface_alt)s;
    border: 1px solid %(border)s;
    border-radius: 3px;
    padding: 5px 8px;
    color: %(text)s;
    selection-background-color: %(accent)s;
    selection-color: %(accent_text)s;
}
QPlainTextEdit {
    background: %(surface)s;
    border: 1px solid %(border)s;
    border-radius: 3px;
    padding: 7px;
    color: %(text)s;
    selection-background-color: %(accent)s;
    selection-color: %(accent_text)s;
}
QLineEdit:focus, QSpinBox:focus, QPlainTextEdit:focus {
    border-color: %(focus)s;
}
QComboBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 %(btn_top)s, stop:1 %(btn_bottom)s);
    border: 1px solid %(border)s;
    border-top-color: %(border_light)s;
    border-radius: 3px;
    padding: 4px 24px 4px 8px;
    min-height: 18px;
    color: %(text)s;
}
QComboBox:hover {
    border-color: %(border_light)s;
}
QComboBox:focus {
    border-color: %(focus)s;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox::down-arrow {
    image: none;
    width: 0;
    height: 0;
    margin-right: 7px;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 4px solid %(muted)s;
}
QComboBox QAbstractItemView {
    background: %(surface)s;
    border: 1px solid %(border)s;
    selection-background-color: %(accent)s;
    selection-color: %(accent_text)s;
    padding: 2px;
    outline: none;
}
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 %(btn_top)s, stop:1 %(btn_bottom)s);
    border: 1px solid %(border)s;
    border-top-color: %(border_light)s;
    border-radius: 3px;
    padding: 5px 12px;
    color: %(text)s;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 %(btn_hover_top)s, stop:1 %(btn_hover_bottom)s);
    border-color: %(border_light)s;
}
QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 %(btn_pressed_top)s, stop:1 %(btn_pressed_bottom)s);
    padding-top: 6px;
    padding-bottom: 4px;
}
QPushButton:disabled {
    color: %(muted)s;
}
QPushButton#primary {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 %(act_top)s, stop:1 %(act_bottom)s);
    border: 1px solid %(act_bottom)s;
    border-top-color: %(act_hover_top)s;
    color: %(act_text)s;
    font-weight: 600;
    padding: 6px 18px;
}
QPushButton#primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 %(act_hover_top)s, stop:1 %(act_hover_bottom)s);
}
QPushButton#primary:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 %(act_pressed_top)s, stop:1 %(act_pressed_bottom)s);
    padding-top: 7px;
    padding-bottom: 5px;
}
QPushButton#primary:disabled {
    color: %(muted)s;
    border-color: %(border)s;
}
QPushButton#ghost {
    background: transparent;
    border: 1px solid transparent;
    padding: 5px 8px;
    font-size: 13px;
}
QPushButton#ghost:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 %(btn_hover_top)s, stop:1 %(btn_hover_bottom)s);
    border-color: %(border)s;
}
QPushButton#ghost:pressed {
    background: %(btn_pressed_top)s;
}
QPushButton#keycap {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 %(btn_top)s, stop:1 %(btn_bottom)s);
    border: 1px solid %(border)s;
    border-top-color: %(border_light)s;
    border-radius: 3px;
    padding: 7px 14px;
    color: %(text)s;
    font-size: 13px;
    font-weight: 600;
    min-width: 170px;
}
QPushButton#keycap:hover, QPushButton#keycap:focus {
    border-color: %(focus)s;
}
QListWidget {
    background: %(surface)s;
    border: 1px solid %(border)s;
    border-radius: 3px;
    padding: 3px;
    outline: none;
}
QListWidget::item {
    background: transparent;
}
QCheckBox {
    color: %(text)s;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 15px;
    height: 15px;
    border: 1px solid %(border)s;
    border-radius: 3px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 %(btn_top)s, stop:1 %(btn_bottom)s);
}
QCheckBox::indicator:checked {
    background: %(accent)s;
    border-color: %(accent)s;
}
QScrollBar:vertical {
    background: transparent;
    width: 9px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: %(border)s;
    border-radius: 2px;
    min-height: 28px;
}
QScrollBar::handle:vertical:hover {
    background: %(border_light)s;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}
QScrollBar:horizontal {
    height: 9px;
}
QScrollBar::handle:horizontal {
    background: %(border)s;
    border-radius: 2px;
}
QToolTip {
    background: %(surface)s;
    color: %(text)s;
    border: 1px solid %(border)s;
    padding: 3px;
}
"""

TRAY_QSS = """
QMenu {
    background: %(surface)s;
    color: %(text)s;
    border: 1px solid %(border)s;
    padding: 4px;
}
QMenu::item {
    padding: 5px 24px 5px 22px;
    border-radius: 3px;
}
QMenu::item:selected {
    background: %(accent)s;
    color: %(accent_text)s;
}
QMenu::separator {
    height: 1px;
    background: %(border)s;
    margin: 4px 6px;
}
"""


def settings_qss():
    return SETTINGS_QSS % METAL


def tray_qss():
    return TRAY_QSS % METAL


def build_palette():
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(METAL["bg"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(METAL["text"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(METAL["surface"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(METAL["surface_alt"]))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(METAL["surface"]))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(METAL["text"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(METAL["text"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(METAL["surface_alt"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(METAL["text"]))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(METAL["danger"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(METAL["accent"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(METAL["accent_text"]))
    palette.setColor(QPalette.ColorRole.Link, QColor(METAL["accent"]))
    palette.setColor(QPalette.ColorRole.LinkVisited, QColor(METAL["accent"]))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(METAL["muted"]))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(METAL["muted"]))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(METAL["muted"]))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(METAL["muted"]))
    return palette
