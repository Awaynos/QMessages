import ctypes

from PySide6.QtCore import QObject, QTimer, Signal

from winapi import (
    HC_ACTION,
    HOOKPROC,
    KBDLLHOOKSTRUCT,
    MSLLHOOKSTRUCT,
    VK_ESCAPE,
    WH_KEYBOARD_LL,
    WH_MOUSE_LL,
    WM_KEYDOWN,
    WM_KEYUP,
    WM_MBUTTONDOWN,
    WM_MBUTTONUP,
    WM_SYSKEYDOWN,
    WM_SYSKEYUP,
    WM_XBUTTONDOWN,
    WM_XBUTTONUP,
    get_async_state,
    kernel32,
    user32,
)

MODIFIER_VKS = {
    "ctrl": (0x11, 0xA2, 0xA3),
    "shift": (0x10, 0xA0, 0xA1),
    "alt": (0x12, 0xA4, 0xA5),
    "win": (0x5B, 0x5C),
}

MODIFIER_ALIASES = {
    "ctrl": "ctrl",
    "control": "ctrl",
    "shift": "shift",
    "alt": "alt",
    "win": "win",
    "windows": "win",
}

VK_CODES = {
    "backspace": 0x08,
    "tab": 0x09,
    "enter": 0x0D,
    "return": 0x0D,
    "shift": 0x10,
    "ctrl": 0x11,
    "control": 0x11,
    "alt": 0x12,
    "pause": 0x13,
    "caps_lock": 0x14,
    "capslock": 0x14,
    "esc": 0x1B,
    "escape": 0x1B,
    "space": 0x20,
    "page_up": 0x21,
    "pageup": 0x21,
    "page_down": 0x22,
    "pagedown": 0x22,
    "end": 0x23,
    "home": 0x24,
    "left": 0x25,
    "up": 0x26,
    "right": 0x27,
    "down": 0x28,
    "insert": 0x2D,
    "ins": 0x2D,
    "delete": 0x2E,
    "del": 0x2E,
    "print_screen": 0x2C,
    "printscreen": 0x2C,
    "win": 0x5B,
    "windows": 0x5B,
    "menu": 0x5D,
    "apps": 0x5D,
    "num_lock": 0x90,
    "numlock": 0x90,
    "scroll_lock": 0x91,
    "scrolllock": 0x91,
    "`": 0xC0,
    "grave": 0xC0,
    "tilde": 0xC0,
    "minus": 0xBD,
    "-": 0xBD,
    "equals": 0xBB,
    "=": 0xBB,
    "plus": 0xBB,
    "bracket_left": 0xDB,
    "[": 0xDB,
    "bracket_right": 0xDD,
    "]": 0xDD,
    "backslash": 0xDC,
    "\\": 0xDC,
    "semicolon": 0xBA,
    ";": 0xBA,
    "quote": 0xDE,
    "'": 0xDE,
    "apostrophe": 0xDE,
    "comma": 0xBC,
    ",": 0xBC,
    "period": 0xBE,
    "dot": 0xBE,
    ".": 0xBE,
    "slash": 0xBF,
    "/": 0xBF,
}

MOUSE_ALIASES = {
    "mouse3": 3,
    "middle": 3,
    "mouse_middle": 3,
    "mouse4": 1,
    "mouse_back": 1,
    "xbutton1": 1,
    "mouse5": 2,
    "mouse_forward": 2,
    "xbutton2": 2,
}

DISPLAY_NAMES = {
    "caps_lock": "CapsLock",
    "page_up": "PageUp",
    "page_down": "PageDown",
    "print_screen": "PrintScreen",
    "num_lock": "NumLock",
    "scroll_lock": "ScrollLock",
    "mouse3": "Mouse3",
    "mouse4": "Mouse4",
    "mouse5": "Mouse5",
    "esc": "Esc",
    "space": "Space",
    "backspace": "Backspace",
    "delete": "Delete",
    "insert": "Insert",
    "enter": "Enter",
    "tab": "Tab",
    "home": "Home",
    "end": "End",
    "left": "Left",
    "right": "Right",
    "up": "Up",
    "down": "Down",
}

for _letter in "abcdefghijklmnopqrstuvwxyz":
    VK_CODES[_letter] = 0x41 + ord(_letter) - ord("a")
for _digit in "0123456789":
    VK_CODES[_digit] = 0x30 + int(_digit)
for _number in range(1, 25):
    VK_CODES[f"f{_number}"] = 0x6F + _number


def _display_key(name):
    if name in DISPLAY_NAMES:
        return DISPLAY_NAMES[name]
    if len(name) == 1:
        return name.upper()
    if name.startswith("f") and name[1:].isdigit():
        return name.upper()
    return name.replace("_", " ").title()


def parse_hotkey(spec):
    parts = [part.strip().lower() for part in str(spec).split("+") if part.strip()]
    if not parts:
        raise ValueError("Пустой бинд")
    modifiers = []
    main = None
    for part in parts:
        if part in MODIFIER_ALIASES:
            name = MODIFIER_ALIASES[part]
            if name not in modifiers:
                modifiers.append(name)
            continue
        if main is not None:
            raise ValueError("В бинде должна быть одна основная клавиша")
        main = part
    if main is None:
        raise ValueError("В бинде нет основной клавиши")

    mouse_button = MOUSE_ALIASES.get(main)
    main_vk = None
    if mouse_button is None:
        main_vk = VK_CODES.get(main)
        if main_vk is None:
            raise ValueError(f"Неизвестная клавиша: {main}")
        if main in MODIFIER_VKS:
            raise ValueError("Модификатор не может быть основной клавишей")

    ordered = [name for name in ("ctrl", "alt", "shift", "win") if name in modifiers]
    display = "+".join([_display_key(name) for name in ordered] + [_display_key(main)])
    return frozenset(ordered), main, main_vk, mouse_button, display


class HotkeyListener(QObject):
    activated = Signal()
    released = Signal()
    cancelled = Signal()
    error = Signal(str)

    def __init__(self, spec, hold_delay_ms=90, parent=None):
        super().__init__(parent)
        self._mods, self._main, self._main_vk, self._mouse_button, self.display = parse_hotkey(spec)
        self._hold_delay = max(0, int(hold_delay_ms))
        self._armed = False
        self._shown = False
        self._suppress = False
        self._menu_open = False
        self._kb_hook = None
        self._mouse_hook = None
        self._kb_hook_proc = None
        self._mouse_hook_proc = None

        self._hold_timer = QTimer(self)
        self._hold_timer.setSingleShot(True)
        self._hold_timer.timeout.connect(self._on_hold)

    @property
    def menu_open(self):
        return self._menu_open

    @menu_open.setter
    def menu_open(self, value):
        self._menu_open = bool(value)
        if not self._menu_open:
            self._shown = False
            self._armed = False
            self._hold_timer.stop()

    def start(self):
        self._kb_hook_proc = HOOKPROC(self._keyboard_proc)
        self._mouse_hook_proc = HOOKPROC(self._mouse_proc)
        module = kernel32.GetModuleHandleW(None)
        self._kb_hook = user32.SetWindowsHookExW(WH_KEYBOARD_LL, self._kb_hook_proc, module, 0)
        if not self._kb_hook:
            self._kb_hook_proc = None
            self.error.emit("Не удалось установить перехват клавиатуры")
            return
        self._mouse_hook = user32.SetWindowsHookExW(WH_MOUSE_LL, self._mouse_hook_proc, module, 0)
        if not self._mouse_hook:
            user32.UnhookWindowsHookEx(self._kb_hook)
            self._kb_hook = None
            self._mouse_hook_proc = None
            self._kb_hook_proc = None
            self.error.emit("Не удалось установить перехват мыши")

    def stop(self):
        self._hold_timer.stop()
        if self._kb_hook:
            user32.UnhookWindowsHookEx(self._kb_hook)
            self._kb_hook = None
        if self._mouse_hook:
            user32.UnhookWindowsHookEx(self._mouse_hook)
            self._mouse_hook = None
        self._kb_hook_proc = None
        self._mouse_hook_proc = None

    def _mods_ok(self):
        for mod in self._mods:
            if not any(get_async_state(vk) for vk in MODIFIER_VKS[mod]):
                return False
        return True

    def _on_hold(self):
        if self._armed:
            self._shown = True
            self.activated.emit()

    def _press(self):
        if self._suppress:
            return True
        if not self._mods_ok():
            return False
        self._suppress = True
        self._armed = True
        self._hold_timer.start(self._hold_delay)
        return True

    def _release(self):
        if not self._suppress:
            return False
        self._suppress = False
        self._armed = False
        self._hold_timer.stop()
        if self._shown:
            self._shown = False
            self.released.emit()
        return True

    def _keyboard_proc(self, n_code, w_param, l_param):
        try:
            if n_code == HC_ACTION:
                info = ctypes.cast(l_param, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                if not (int(info.flags) & 0x10):
                    message = int(w_param)
                    vk = int(info.vkCode)
                    if message in (WM_KEYDOWN, WM_SYSKEYDOWN):
                        if vk == VK_ESCAPE and self._shown:
                            self._shown = False
                            self._armed = False
                            self._hold_timer.stop()
                            self.cancelled.emit()
                            return 1
                        if self._main_vk is not None and vk == self._main_vk:
                            if self._press():
                                return 1
                    elif message in (WM_KEYUP, WM_SYSKEYUP):
                        if self._main_vk is not None and vk == self._main_vk:
                            if self._release():
                                return 1
        except Exception:
            pass
        return user32.CallNextHookEx(self._kb_hook, n_code, w_param, l_param)

    def _mouse_proc(self, n_code, w_param, l_param):
        try:
            if n_code == HC_ACTION:
                info = ctypes.cast(l_param, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
                message = int(w_param)
                button = 0
                if message in (WM_XBUTTONDOWN, WM_XBUTTONUP):
                    button = (int(info.mouseData) >> 16) & 0xFFFF
                elif message in (WM_MBUTTONDOWN, WM_MBUTTONUP):
                    button = 3

                if self._mouse_button and button == self._mouse_button:
                    if message in (WM_XBUTTONDOWN, WM_MBUTTONDOWN):
                        if self._press():
                            return 1
                    elif message in (WM_XBUTTONUP, WM_MBUTTONUP):
                        if self._release():
                            return 1
        except Exception:
            pass
        return user32.CallNextHookEx(self._mouse_hook, n_code, w_param, l_param)
