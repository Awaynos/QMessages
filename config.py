import copy
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CONFIG = {
    "hotkey": "caps_lock",
    "hold_delay_ms": 90,
    "select_on_release": True,
    "press_enter": False,
    "paste_method": "clipboard",
    "restore_clipboard": True,
    "restore_delay_ms": 800,
    "snippets": [
        {"label": "ПРИВЕТ", "text": "Привет! Как дела?"},
        {"label": "СПС", "text": "Спасибо!"},
        {"label": "ОК", "text": "ок"},
        {"label": "1 МИН", "text": "секунду, я сейчас"},
        {"label": "ПОЗЖЕ", "text": "давай позже"},
        {"label": "СОЗВОН", "text": "можем созвониться?"},
        {"label": "ЖДУ", "text": "жду :)"},
        {"label": "ПОКА", "text": "до связи!"},
    ],
}

@dataclass
class Snippet:
    label: str
    text: str


def app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


APP_NAME = "QMessages"


def data_dir():
    base = os.getenv("APPDATA")
    if not base:
        base = Path.home() / "AppData" / "Roaming"
    return Path(base) / APP_NAME


def config_path():
    return data_dir() / "config.json"


def _merge(base, override):
    result = copy.deepcopy(base)
    if not isinstance(override, dict):
        return result
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
    return result


def make_label(text):
    line = text.strip().splitlines()[0] if text.strip() else ""
    line = " ".join(line.split())
    if len(line) > 18:
        line = line[:17].rstrip() + "…"
    return line or "…"


def _to_bool(value, fallback):
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on", "да")
    return fallback


def _clamp_int(value, low, high, fallback):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return fallback
    return max(low, min(high, number))


def normalize(raw):
    config = _merge(DEFAULT_CONFIG, raw)

    hotkey = config.get("hotkey")
    if not isinstance(hotkey, str) or not hotkey.strip():
        config["hotkey"] = DEFAULT_CONFIG["hotkey"]
    else:
        config["hotkey"] = hotkey.strip().lower()

    config["hold_delay_ms"] = _clamp_int(config.get("hold_delay_ms"), 0, 1000, 90)
    config["select_on_release"] = _to_bool(config.get("select_on_release"), True)
    config["press_enter"] = _to_bool(config.get("press_enter"), False)
    config["restore_clipboard"] = _to_bool(config.get("restore_clipboard"), True)
    config["restore_delay_ms"] = _clamp_int(config.get("restore_delay_ms"), 0, 5000, 800)

    if config.get("paste_method") not in ("clipboard", "type"):
        config["paste_method"] = "clipboard"

    config.pop("theme", None)

    snippets = config.get("snippets")
    if not isinstance(snippets, list):
        snippets = []
    cleaned = []
    for entry in snippets:
        if isinstance(entry, str):
            text = entry
            label = ""
        elif isinstance(entry, dict):
            text = entry.get("text", "")
            label = entry.get("label", "")
        else:
            continue
        if not isinstance(text, str) or not text.strip():
            continue
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        label = make_label(text) if not isinstance(label, str) or not label.strip() else label.strip()
        cleaned.append({"label": label, "text": text})
        if len(cleaned) >= 16:
            break
    config["snippets"] = cleaned
    return config


def build_snippets(config):
    return [Snippet(item["label"], item["text"]) for item in config["snippets"]]


class ConfigStore:
    def __init__(self, path):
        self.path = Path(path)

    def load(self):
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            return normalize(DEFAULT_CONFIG), None
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as error:
            return normalize(DEFAULT_CONFIG), f"config.json не прочитан: {error}"
        if not isinstance(raw, dict):
            return normalize(DEFAULT_CONFIG), "config.json должен содержать объект"
        return normalize(raw), None

    def save(self, config):
        normalized = normalize(config)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return normalized

    def open_in_editor(self):
        import os

        os.startfile(str(self.path))
