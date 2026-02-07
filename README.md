# LexiLoom

A GTK4 translation file editor for **PO**, **TS**, and **JSON** i18n files.

![License](https://img.shields.io/badge/license-GPL--3.0--or--later-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)

## Features

- **Multi-format editing** — PO/POT (gettext), Qt TS (XML), JSON (flat & nested)
- **Linting & quality score** — format specifier checks, whitespace, length ratio, punctuation
- **Pre-translation** — Lingva and MyMemory (free), OpenAI and Anthropic (paid)
- **Spell checking** — via PyEnchant with configurable language
- **Metadata viewer** — Last-Translator, PO-Revision-Date, language, etc.
- **GitHub PR integration** — fetch POT, create branch, push translation, open PR
- **Platform integration** — Transifex, Weblate, Crowdin API support
- **In-app updates** — automatic update checking (macOS/Windows)
- **Internationalized** — uses gettext for its own UI

## Requirements

- Python 3.10+
- GTK4 and libadwaita
- PyGObject

### macOS

```bash
brew install gtk4 libadwaita pygobject3 enchant
```

### Linux

```bash
# Fedora
sudo dnf install gtk4-devel libadwaita-devel python3-gobject enchant2-devel

# Ubuntu/Debian
sudo apt install libgtk-4-dev libadwaita-1-dev python3-gi gir1.2-adw-1 libenchant-2-dev
```

## Installation

```bash
pip install -e .

# With AI translation support:
pip install -e ".[ai]"
```

## Usage

```bash
# Launch GUI
lexiloom

# Open a file directly
lexiloom path/to/file.po
```

## Project Structure

```
lexiloom/
├── src/lexiloom/
│   ├── app.py              # Application entry point
│   ├── ui/
│   │   └── window.py       # Main GTK4 window
│   ├── parsers/
│   │   ├── po_parser.py    # PO/POT parser (polib)
│   │   ├── ts_parser.py    # Qt TS parser (XML)
│   │   └── json_parser.py  # JSON i18n parser
│   └── services/
│       ├── linter.py       # Translation linting & quality score
│       ├── translator.py   # Pre-translation engines
│       ├── spellcheck.py   # Spell checking (enchant)
│       ├── github.py       # GitHub PR workflow
│       ├── platforms.py    # Transifex, Weblate, Crowdin
│       └── updater.py      # In-app update checker
├── po/                     # Translations for LexiLoom itself
├── docs/                   # Documentation
└── pyproject.toml
```

## License

GPL-3.0-or-later — see [LICENSE](LICENSE)

## Author

Daniel Nylander <po@danielnylander.se>
