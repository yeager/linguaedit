"""PEP 517 backend that compiles Qt translations for wheel artifacts."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

from setuptools import build_meta as _setuptools_backend

from translation_build import compile_translations

_TRANSLATIONS = Path(__file__).parent / "src" / "linguaedit" / "translations"


@contextmanager
def _compiled_translations():
    """Create .qm files for packaging and remove them from the source tree after."""
    try:
        compile_translations(_TRANSLATIONS)
        yield
    finally:
        for qm_file in _TRANSLATIONS.glob("*.qm"):
            qm_file.unlink(missing_ok=True)


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    with _compiled_translations():
        return _setuptools_backend.build_wheel(
            wheel_directory, config_settings, metadata_directory
        )


def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    with _compiled_translations():
        return _setuptools_backend.build_editable(
            wheel_directory, config_settings, metadata_directory
        )


build_sdist = _setuptools_backend.build_sdist
get_requires_for_build_wheel = _setuptools_backend.get_requires_for_build_wheel
get_requires_for_build_sdist = _setuptools_backend.get_requires_for_build_sdist
prepare_metadata_for_build_wheel = _setuptools_backend.prepare_metadata_for_build_wheel
