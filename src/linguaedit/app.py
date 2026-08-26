"""LinguaEdit PySide6 application entry point."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from PySide6.QtCore import QLibraryInfo, QLocale, QTranslator
from PySide6.QtWidgets import QApplication

from linguaedit import APP_ID
from linguaedit.services.settings import Settings


def _match_supported_language(tag: str, available: set[str]) -> str | None:
    """Map an OS locale tag to an available LinguaEdit catalog."""
    normalized = tag.strip().replace("_", "-").lower()
    if not normalized or normalized in {"c", "posix"}:
        return None
    if normalized.startswith("zh"):
        candidates = ("zh_CN", "zh")
    elif normalized.startswith("pt-br"):
        candidates = ("pt_BR", "pt")
    elif normalized.startswith(("no", "nb", "nn")):
        candidates = ("nb",)
    else:
        candidates = (normalized.split("-", 1)[0],)
    return next((code for code in candidates if code in available), None)


def _system_ui_language(translations_dir: Path) -> str:
    """Return the preferred available UI language, including macOS app bundles."""
    available = {"en"}
    available.update(
        qm.stem.removeprefix("linguaedit_")
        for qm in translations_dir.glob("linguaedit_*.qm")
        if qm.stat().st_size >= 100
    )
    candidates: list[str] = []

    # NSLocale respects the user's ordered language list in a macOS .app bundle.
    if sys.platform == "darwin":
        try:
            from Foundation import NSLocale
            candidates.extend(str(value) for value in NSLocale.preferredLanguages())
        except (ImportError, AttributeError):
            pass

    system_locale = QLocale.system()
    candidates.extend(system_locale.uiLanguages())
    candidates.append(system_locale.name())

    if sys.platform == "darwin":
        try:
            import subprocess
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleLanguages"],
                capture_output=True, text=True, timeout=2, check=False,
            )
            candidates.extend(re.findall(r'"?([A-Za-z]{2,3}(?:[-_][A-Za-z0-9]+)*)"?', result.stdout))
        except (OSError, subprocess.SubprocessError):
            pass

    for candidate in candidates:
        matched = _match_supported_language(candidate, available)
        if matched:
            return matched
    return "en"


def _find_translations_dir() -> Path:
    """Find the translations directory, checking multiple locations."""
    candidates = [
        Path(__file__).parent / "translations",                 # installed (inside package) & dev
    ]
    # PyInstaller frozen bundle: files are in sys._MEIPASS
    if getattr(sys, 'frozen', False):
        meipass = Path(sys._MEIPASS)  # type: ignore[attr-defined]
        candidates.insert(0, meipass / "linguaedit" / "translations")
    # Also check relative to the package install location via importlib
    try:
        import importlib.resources as _res
        pkg_dir = Path(_res.files("linguaedit").__fspath__())  # type: ignore[union-attr]
        candidates.append(pkg_dir / "translations")
    except Exception:
        pass
    candidates += [
        Path(sys.prefix) / "share" / "linguaedit" / "translations",
        Path(sys.prefix) / "Lib" / "site-packages" / "linguaedit" / "translations",  # Windows pip
    ]
    for d in candidates:
        if d.is_dir():
            return d
    return candidates[0]


class LinguaEditApp:
    """Main application wrapper."""

    def __init__(self, argv: list[str]):
        self._argv = argv

        # Fix macOS menu bar app name (must be before QApplication)
        if sys.platform == 'darwin':
            try:
                from Foundation import NSBundle
                bundle = NSBundle.mainBundle()
                info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
                info['CFBundleName'] = 'LinguaEdit'
            except ImportError:
                pass
            # Also patch argv[0] – Qt uses this for the menu title on macOS
            if argv:
                argv[0] = 'LinguaEdit'

        # Work around SIGSEGV in libqcocoa.dylib accessibility bridge (Qt 6 bug):
        # macOS accessibility daemon queries widgets during creation/destruction,
        # hitting dangling pointers in the Cocoa platform plugin.
        # Users who need accessibility can set QT_ACCESSIBILITY=1 to re-enable.
        if sys.platform == 'darwin':
            import os
            os.environ.setdefault("QT_ACCESSIBILITY", "0")

        self._qt_app = QApplication(argv)
        self._qt_app.setApplicationName("LinguaEdit")
        self._qt_app.setApplicationDisplayName("LinguaEdit")
        self._qt_app.setOrganizationName("danielnylander")
        self._qt_app.setOrganizationDomain("danielnylander.se")
        self._qt_app.setDesktopFileName(APP_ID)

        # Load translations
        self._translator = QTranslator()
        self._qt_translator = QTranslator()
        self._load_translations()

    def _load_translations(self):
        """Load Qt and app translations for current locale."""
        import logging
        log = logging.getLogger("linguaedit.i18n")

        settings = Settings.get()
        lang = settings["language"]
        log.info("Settings language: %s", lang)

        if lang == "auto":
            lang = _system_ui_language(_find_translations_dir())
            log.info("Auto-detected UI language: %s", lang)

        qt_locale = QLocale(lang)

        # Load Qt's own translations (buttons, dialogs, etc.)
        qt_translations_path = QLibraryInfo.path(QLibraryInfo.TranslationsPath)
        if self._qt_translator.load(qt_locale, "qtbase", "_", qt_translations_path):
            self._qt_app.installTranslator(self._qt_translator)
            log.info("Loaded Qt base translations for %s", lang)

        # Load LinguaEdit translations
        translations_dir = _find_translations_dir()
        log.info("Translations dir: %s (exists: %s)", translations_dir, translations_dir.is_dir())
        if translations_dir.is_dir():
            qm_files = list(translations_dir.glob("*.qm"))
            log.info("Available .qm files: %s", [f.name for f in qm_files])

        qm_file = translations_dir / f"linguaedit_{lang}.qm"
        log.info("Looking for: %s (exists: %s)", qm_file, qm_file.exists())
        # Use forward slashes for QTranslator.load() — Qt expects them on all platforms
        qm_path_str = str(qm_file).replace("\\", "/")
        if qm_file.exists() and self._translator.load(qm_path_str):
            self._qt_app.installTranslator(self._translator)
            log.info("✓ Loaded translations: %s", qm_file.name)
        elif qm_file.exists():
            log.warning("✗ .qm file exists but QTranslator.load() failed: %s", qm_file)
        else:
            log.warning("✗ Translation file not found: %s", qm_file)

    def run(self) -> int:
        settings = Settings.get()

        # Determine file to open from argv
        file_path = None
        if len(self._argv) > 1:
            file_path = self._argv[1]

        if not settings.first_run_complete:
            from linguaedit.ui.welcome_dialog import WelcomeDialog
            wizard = WelcomeDialog(on_finish=lambda: self._show_main_window(file_path))
            wizard.show()
        else:
            self._show_main_window(file_path)

        return self._qt_app.exec()

    def _show_main_window(self, file_path: str | None = None):
        from linguaedit.ui.window import LinguaEditWindow
        self._win = LinguaEditWindow()
        if file_path:
            self._win._load_file(file_path)
        self._win.show()


def main():
    import logging
    logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")
    app = LinguaEditApp(sys.argv)
    sys.exit(app.run())


if __name__ == "__main__":
    main()
