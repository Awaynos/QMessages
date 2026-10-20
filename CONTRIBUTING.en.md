# How to help the project

[Русский](CONTRIBUTING.md) · **English**

Thanks for stopping by. QMessages is a small personal project, and any help is
welcome: a bug report, a one-line fix, a documentation improvement, an idea.

## What you can do

- **Report a bug** — [open an issue](https://github.com/Awaynos/QMessages/issues/new) and describe how to reproduce it: what you did, what you expected, what you got.
- **Fix a bug** — even if it is a single line.
- **Improve the documentation** — README, screenshots, this guide.
- **Suggest an idea** — short and to the point, in an issue.
- **Help with Linux/macOS** — it is on the roadmap; say if you want to take it on.

## Before you start

- A small fix (a typo, a bug in one function) can be sent right away.
- For a bigger change, open an issue first and describe the plan. That way nobody wastes time.
- Check whether an issue for it is already open.

## Running it locally

```powershell
git clone https://github.com/Awaynos/QMessages.git
cd QMessages

setup.bat
start.bat
```

`setup.bat` creates `.venv` and installs the dependencies. `start.bat` runs without
a console.

Or manually:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py --settings
```

You need **Python 3.11+**. Windows 10/11 is supported for now; Linux and macOS are
on the roadmap.

## Checks

There is no test framework — verify manually:

```powershell
.\.venv\Scripts\python.exe -m compileall -q .
.\.venv\Scripts\python.exe main.py --settings
.\.venv\Scripts\python.exe main.py --preview
```

Before a PR, check: launch, the settings window, the hotkey, selecting and pasting,
and saving snippets. If you changed dependencies, the icon or the build layout, run
`build.bat` and launch `dist\QMessages\QMessages.exe`.

If you add a feature, describe in the PR how to verify it.

## Code style

- Python 3.11, type annotations, 4-space indentation.
- Comments only where they explain **why**, not **what**. Do not comment the obvious.
- The interface is in Russian for now; new strings should be in Russian. Localization is planned.
- Do not mix the layers: `main.py` is wiring, `settings.py`/`wheel.py` are UI, `hotkeys.py`/`winapi.py` are platform code, `config.py` is data, `theme.py` is the palette.
- The palette is fixed — Metal. Do not add a theme switcher without discussion.
- Add a feature as a separate module or a small function; do not break existing signals.

## Commits

Conventional Commits, in English, imperative mood:

```
feat(wheel): add hover label animation
fix(paste): restore clipboard after Enter
docs: update README
```

The scope in brackets is the area: `ui`, `wheel`, `hotkeys`, `paste`, `config`, `build`, `docs`.

## Branches and pull requests

- Branch off `main`: `feature/short-name` or `fix/short-name`.
- In the PR description: what was done, why, and how to verify it.
- If you changed the interface, attach a screenshot.
- One PR — one task.

## Contribution license

The project is distributed under [PolyForm Noncommercial 1.0.0](LICENSE).

By submitting a pull request, you agree that your contribution is licensed under
the same terms — it may be freely used, modified and distributed for non-commercial
purposes.
