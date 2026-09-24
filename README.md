# LinguaEdit

![Version](https://img.shields.io/badge/version-1.8.19-blue)
![GitHub Release](https://img.shields.io/github/v/release/yeager/linguaedit)
![License](https://img.shields.io/badge/license-GPL--3.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![Qt](https://img.shields.io/badge/Qt-6-green)
![Platforms](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)
[![Translate on Transifex](https://img.shields.io/badge/translate-Transifex-blue)](https://app.transifex.com/danielnylander/linguaedit/)

LinguaEdit is a desktop editor for software localization files and subtitles. It runs on Linux, macOS, and Windows and is built with Python, PySide6, and Qt 6.

- Website: [linguaedit.org](https://www.linguaedit.org)
- Downloads: [GitHub Releases](https://github.com/yeager/linguaedit/releases)
- Changelog: [CHANGELOG.md](CHANGELOG.md)
- Bugs and feature requests: [GitHub Issues](https://github.com/yeager/linguaedit/issues)

## Screenshots

### Editor
![LinguaEdit editor](docs/screenshots/main-editor.png)

### Validation
![Validation results](docs/screenshots/validation.png)

### Subtitle editing
![Video subtitle editor](docs/screenshots/video-subtitles.png)

## Install

The latest release is [v1.8.19](https://github.com/yeager/linguaedit/releases/tag/v1.8.19). Download the file for your system:

| Platform | Download | Install |
|---|---|---|
| macOS, Apple Silicon | [ZIP](https://github.com/yeager/linguaedit/releases/download/v1.8.19/LinguaEdit-v1.8.19-macOS-arm64.zip) | Unzip and move LinguaEdit to Applications. |
| macOS, Intel | [ZIP](https://github.com/yeager/linguaedit/releases/download/v1.8.19/LinguaEdit-v1.8.19-macOS-x86_64.zip) | Unzip and move LinguaEdit to Applications. |
| Windows | [Installer](https://github.com/yeager/linguaedit/releases/download/v1.8.19/LinguaEdit-1.8.19-Setup.exe) | Run the installer. |
| Debian or Ubuntu | [DEB package](https://github.com/yeager/linguaedit/releases/download/v1.8.19/linguaedit_1.8.19_all.deb) | Install with APT or a package manager. |
| Python | [Wheel](https://github.com/yeager/linguaedit/releases/download/v1.8.19/linguaedit-1.8.19-py3-none-any.whl) | Install with pip; requires Python 3.10 or newer. |

The Python package published on PyPI may lag behind the GitHub release. For v1.8.19, download the wheel above, then run:

```bash
python -m pip install ./linguaedit-1.8.19-py3-none-any.whl
linguaedit-gui
```

The macOS app requires macOS 13 or newer. The Windows installer does not require a separate Python installation. The Debian package requires Python 3.10 or newer and installs its Python dependencies during setup.

Optional tools: `ffmpeg` for extracting subtitles from video, `hunspell` for spell checking, and `git` for version control features.

## Supported formats

LinguaEdit edits the following localization formats:

| Format | Extensions |
|---|---|
| GNU gettext | `.po`, `.pot` |
| Qt Linguist | `.ts` |
| XLIFF 1.2 and 2.0 | `.xliff`, `.xlf` |
| SDLXLIFF | `.sdlxliff` |
| memoQ XLIFF | `.mqxliff` |
| JSON localization files | `.json` |
| YAML | `.yml`, `.yaml` |
| Android resources | `.xml` |
| Flutter ARB | `.arb` |
| PHP arrays | `.php` |
| Java Properties | `.properties` |
| Apple Strings and Stringsdict | `.strings`, `.stringsdict` |
| Unity assets | `.asset` |
| .NET resources | `.resx` |
| Chrome extension messages | `messages.json` |
| Godot translations | `.csv`, `.tres` |
| SubRip and WebVTT subtitles | `.srt`, `.vtt` |

TMX is supported for translation-memory import and export. It is not an editable catalog format. See [Supported Formats](docs/formats.md) for details.

## Features

- Edit several files in tabs; open files by drag and drop.
- Find and replace text with regular expressions, case matching, or whole-word matching.
- Filter entries by translation status, warnings, bookmarks, and tags.
- Use translation memory with fuzzy matches, context weighting, and TMX import/export.
- Maintain glossaries with approved and forbidden terms, and check term consistency.
- Get suggestions from DeepL, OpenAI, Google, Lingva, MyMemory, Argos Translate, and OpenNMT-py. Hosted services may require API credentials. Argos and OpenNMT can run locally; OpenNMT also requires a compatible model and `onmt_translate` on `PATH`.
- Check placeholders, markup, plural forms, terminology, accessibility, and other translation issues before saving.
- Review changes with Git, monitor files for external edits, and recover unsaved work from local snapshots.
- Translate subtitle files and extract subtitles from video with FFmpeg.
- Use the dashboard, layout simulator, regex tester, OCR, text-to-speech, macros, and configurable QA profiles.

### Keyboard shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+O` | Open a file |
| `Ctrl+S` | Save |
| `Ctrl+H` | Find and replace |
| `Ctrl+U` | Toggle fuzzy status |
| `Alt+Enter` | Go to the next untranslated entry |
| `Ctrl+Enter` | Save and go to the next untranslated entry |
| `Ctrl+B` | Copy source text to translation |
| `Ctrl+D` | Open the project dashboard |
| `Ctrl+Shift+D` | Show Git diff |
| `Ctrl+Alt+T` | Open batch translation |
| `Ctrl+Shift+F` | Toggle focus mode |
| `Ctrl+Alt+Z` | Toggle Zen mode |
| `Ctrl+R` | Toggle review mode |
| `Ctrl+Shift+A` | Open AI review |
| `F11` | Toggle full screen |

## Translations

The project has 18 language catalogs with 1,612 messages. Catalog updates sync daily from [Transifex](https://app.transifex.com/danielnylander/linguaedit/) through GitHub Actions. Release builds include catalogs that are more than 20% translated.

To contribute a translation, join the project on Transifex.

## Build from source

```bash
git clone https://github.com/yeager/linguaedit.git
cd linguaedit
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]" build
linguaedit-gui
```

Build a wheel with:

```bash
python -m build --wheel
```

The build compiles `.ts` catalogs to `.qm` files inside the package when a catalog is more than 20% translated. Compiled `.qm` files are build artifacts and are not stored in the source tree. The release workflow builds the macOS apps, Windows installer, Debian package, and Python wheel; see [GitHub Actions](https://github.com/yeager/linguaedit/actions).

The automated suite contains 147 tests. To run it locally:

```bash
QT_QPA_PLATFORM=offscreen pytest -q
```

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).

## Author

Daniel Nylander — [danielnylander.se](https://www.danielnylander.se) · [GitHub](https://github.com/yeager)
