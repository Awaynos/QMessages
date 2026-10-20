<div align="center">

<img src="docs/images/app-icon.png" alt="QMessages" width="128" height="128">

# QMessages

**Quick message snippets — a radial menu right at your cursor.**

Hold a hotkey → pick a message → release. The text is already in the chat.

[Русский](README.md) · **English**

![Version](https://img.shields.io/badge/version-1.0-9c9c9c?style=flat-square)
![License](https://img.shields.io/badge/license-PolyForm_Noncommercial-8f8f8f?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11-4b8bbe?style=flat-square&logo=python&logoColor=white)
![Qt](https://img.shields.io/badge/PySide6-Qt_6-41cd52?style=flat-square&logo=qt&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Windows-4a5057?style=flat-square&logo=windows&logoColor=white)

<br>

<img src="docs/images/wheel.png" alt="QMessages wheel" width="520">
<br><sub>The snippet wheel: hold the hotkey, aim at a message, release.</sub>

</div>

---

## How it started

Every day the same messages show up in chat: a greeting, a link, "one sec",
"thanks". Opening a notepad and hunting for a template every time gets old.

The idea was simple: one motion — hold a key, pick a message, release — and the
text is already in the input field. That became a wheel, like the ones in games,
but for everyday messaging.

QMessages grew from the same idea as QTranslate-R: a small local tool that solves
one problem and stays out of the way. No telemetry, no accounts, no cloud — just
snippets, a global hotkey and a clean **Metal** interface.

---

## What it can do

### The wheel

| | |
|---|---|
| **Hold to open** | Hold the hotkey — the wheel appears right under the cursor. |
| **Pick by movement** | Aim at a sector and release. Or left-click it. |
| **Cancel** | Right-click, Esc, release over the hub, or move far away. |
| **Smooth** | 60 fps animation, soft sector highlight and a text preview in the hub. |
| **Compact** | A 500 px window; label and preview text stay readable. |

### Snippets

| | |
|---|---|
| **Up to 16 messages** | A short label on the wheel and the full text to paste. |
| **Editor** | Add, delete, move up/down, edit the label and the text. |
| **Auto label** | If the label is empty, the beginning of the text is used. |
| **From clipboard** | "Paste from clipboard" in the editor and a separate tray action. |
| **Persistence** | Everything lives in `%APPDATA%\QMessages\config.json`. |

### Pasting

| | |
|---|---|
| **Clipboard** | Ctrl+V into the focused window. Best compatibility with chats and browsers. |
| **Type mode** | `type` — for apps that block clipboard pasting. |
| **Send immediately** | The "Send immediately (Enter)" option presses Enter after pasting. |
| **Restore clipboard** | The previous clipboard contents are restored after pasting. |
| **No Enter by default** | You can check the text before sending it. |

### Interface and system

- **Metal**: dark grey palette, beveled gradient buttons, tidy inputs and snippet list.
- **Tray**: "Show wheel", "Save from clipboard", "Settings…", open config, reload, exit.
- **Settings**: a separate window; the global hotkey is not captured while it is open.
- **Portable**: the exe and all libraries live in one folder; no installation needed.
- **Qm icon**: exe, tray, settings window, taskbar and Task Manager.

### What is remembered

Everything you change survives a restart: the hotkey, snippets, hold delay,
select-on-release, paste method, send-on-Enter and clipboard restore.

---

## Install and run

### Portable build

```bat
build.bat
```

The ready app appears in `dist\QMessages`. Move the whole folder to another PC or
drive — Python, Qt and the libraries are already inside. Nothing to install.

Settings live in `%APPDATA%\QMessages\config.json`, not next to the exe. On a new
device the app creates defaults; copy that file to bring your snippets along.

The `dist` folder is not committed to the repository, so there is no ready exe
in the source tree.

### From source

Requires **Python 3.11+**.

```powershell
git clone https://github.com/Awaynos/QMessages.git
cd QMessages
setup.bat
start.bat
```

`setup.bat` creates `.venv` and installs the dependencies. `start.bat` runs without
a console, `run.bat` runs with one for debugging.

---

## Default hotkeys

| Keys | Action |
|---|---|
| `CapsLock` | Open the wheel (hold) |
| `LMB` | Pick the sector under the cursor |
| `RMB` / `Esc` | Close without pasting |
| `Mouse4` / `Mouse5` | Can be assigned in settings |

All combinations are changed in **Settings → Hotkey**. You can record
`Ctrl+Alt+Space`, `Alt+\``, `Ctrl+Shift+S`, `F8` or a mouse side button.

The combination is global: while the app is running, that key does not reach other
programs. Do not bind `Ctrl+C`, `Ctrl+V` and other common shortcuts — they will
stop working.

---

## Settings

<div align="center">
<img src="docs/images/settings.png" alt="QMessages settings" width="820">
<br><sub>Settings: hotkey, snippets, behaviour and saving.</sub>
</div>

The interface is currently in Russian.

- **Hotkey** — click the field and press a combination; "Reset" returns CapsLock.
- **Snippets** — the list on the left, the editor on the right. Edit label and text.
- **Behaviour** — hold delay, select on release, send on Enter, paste method,
  clipboard restore.
- **Save** — the button at the bottom or `Ctrl+S`.

While the settings window is open, the global hotkey is not captured, so you can
type normally. It comes back when the window closes.

---

## Quick save

1. Copy the text.
2. Tray icon → **"Save from clipboard"**.
3. Adjust the wheel label — it is filled in automatically.
4. `Ctrl+S`.

You can also use the editor: "Add" → "Paste from clipboard" → "Save".

---

## Config

File: `%APPDATA%\QMessages\config.json`. Created automatically on first launch.

```json
{
  "hotkey": "caps_lock",
  "hold_delay_ms": 90,
  "select_on_release": true,
  "press_enter": false,
  "paste_method": "clipboard",
  "restore_clipboard": true,
  "restore_delay_ms": 800,
  "snippets": [
    {"label": "HELLO", "text": "Hello! How are you?"}
  ]
}
```

- `hold_delay_ms` — how long to hold before the wheel opens, 0–1000 ms.
- `select_on_release` — `true`: pick on release; `false`: click only.
- `press_enter` — press Enter after pasting.
- `paste_method` — `clipboard` (Ctrl+V) or `type` (character by character).
- `restore_clipboard` — restore the previous clipboard contents.
- `snippets` — up to 16; `label` is the wheel caption, `text` is what gets pasted.

The interface palette is fixed — **Metal** (dark grey); there are no themes.
The file is re-read as you save it. If you edit it by hand, use
"Reload settings" in the tray.

---

## Project structure

```
QMessages/
  main.py            app, tray, module wiring
  settings.py        settings window and snippet editor
  wheel.py           radial menu and animation
  hotkeys.py         global keyboard and mouse hook
  winapi.py          Win32: hooks, SendInput, overlay window
  paste.py           clipboard or character-by-character paste
  config.py          config.json in %APPDATA%\QMessages
  theme.py           Metal palette and styles
  icon.ico / icon.png
  VERSION.txt
  file_version_info.txt
  build.bat / setup.bat / start.bat / run.bat
  docs/images/       README screenshots
```

---

## Tech

| | |
|---|---|
| Language | Python 3.11 |
| UI | PySide6 / Qt 6 (Essentials: QtCore, QtGui, QtWidgets) |
| Windows | Win32 via `ctypes`: low-level hooks, SendInput, layered overlay |
| Build | PyInstaller, onedir — no installation on the target machine |
| Network | not used |

Snippets, hotkeys and the clipboard stay local. No account, cloud or telemetry.

---

## Roadmap

- [ ] Import and export snippets
- [ ] Profiles for different chats and apps
- [ ] Search through snippets
- [ ] Start with Windows
- [ ] A separate "save from clipboard" hotkey
- [ ] Configurable wheel size
- [ ] English UI localization
- [ ] Linux support
- [ ] macOS support

---

## Contributing

Bug reports, ideas and pull requests are welcome. See
[CONTRIBUTING.en.md](CONTRIBUTING.en.md) ([Русский](CONTRIBUTING.md)).

---

## ❤️ Support the project

Developing QMessages takes time — any support is appreciated 🫡

**Important:** send funds **only on the specified network** — a transfer on another network may be lost forever.

| Coin | Network | Address |
|---|---|---|
| **Bitcoin (BTC)** | Bitcoin (SegWit) | `bc1qfaylkgnwct052snamqmnxl3uk26xpt5jg344fs` |
| **Ethereum (ETH)** | ERC-20 | `0x44628629c1C6f8E8591d4f93735Ff6CD70DC8AfC` |
| **Tether (USDT)** | BEP-20 (BSC) | `0x44628629c1C6f8E8591d4f93735Ff6CD70DC8AfC` |
| **Solana (SOL / SPL)** | Solana | `3sTNRxJqATsJsKWyM5dxi4HHMLEKbp8f8dGU4wJ1xmE9` |

Support is completely voluntary. You can also help without money: report a bug,
suggest an idea, translate the interface or just star the project.

---

## Version and license

**1.0** — stable portable release. The version lives in [`VERSION.txt`](VERSION.txt)
and is edited with a plain text editor.

The project is distributed under the **[PolyForm Noncommercial 1.0.0](LICENSE)**
license ([Russian translation](LICENSE.ru.md)) — it is *source-available*, not
open source.

The license was chosen deliberately: it forbids making money from the project.
Anyone can fork, study and improve QMessages — but nobody can turn it into a paid
product. Commercial use is possible only with the author's explicit permission.
