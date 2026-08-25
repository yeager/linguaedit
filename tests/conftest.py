"""Shared fixtures for LinguaEdit tests."""
import sys
from pathlib import Path

import pytest

# Ensure src is on path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir():
    return FIXTURES


@pytest.fixture
def tmp_out(tmp_path):
    """Temp directory for output files."""
    return tmp_path


@pytest.fixture(scope="session")
def qapp():
    """Headless Qt application for GUI regression tests."""
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    return app


# Patch QCoreApplication.translate to avoid needing Qt runtime
@pytest.fixture(autouse=True)
def patch_qt_translate(monkeypatch):
    """Replace QCoreApplication.translate with a no-op for linter tests."""
    try:
        from PySide6.QtCore import QCoreApplication
        monkeypatch.setattr(
            QCoreApplication, "translate",
            staticmethod(lambda ctx, text, *args: text),
        )
    except Exception:
        pass
