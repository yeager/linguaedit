"""Tests for operating-system UI language selection."""

import sys
from types import SimpleNamespace

from linguaedit.app import _match_supported_language


def test_matches_common_system_locale_variants():
    available = {"en", "nb", "pt_BR", "zh_CN", "sv"}

    assert _match_supported_language("sv-SE", available) == "sv"
    assert _match_supported_language("nb_NO", available) == "nb"
    assert _match_supported_language("no-NO", available) == "nb"
    assert _match_supported_language("pt-BR", available) == "pt_BR"
    assert _match_supported_language("zh-Hans-SE", available) == "zh_CN"


def test_unsupported_or_neutral_locale_has_no_match():
    available = {"en", "sv"}

    assert _match_supported_language("C", available) is None
    assert _match_supported_language("eo-001", available) is None


def test_macos_prefers_ordered_system_language(tmp_path, monkeypatch):
    from linguaedit import app

    (tmp_path / "linguaedit_sv.qm").write_bytes(b"q" * 100)

    class FakeNSLocale:
        @staticmethod
        def preferredLanguages():
            return ["sv-SE", "en-SE"]

    monkeypatch.setattr(app.sys, "platform", "darwin")
    monkeypatch.setitem(sys.modules, "Foundation", SimpleNamespace(NSLocale=FakeNSLocale))

    assert app._system_ui_language(tmp_path) == "sv"


def test_macos_skips_unavailable_preferred_language(tmp_path, monkeypatch):
    from linguaedit import app

    (tmp_path / "linguaedit_de.qm").write_bytes(b"q" * 100)

    class FakeNSLocale:
        @staticmethod
        def preferredLanguages():
            return ["is-IS", "de-DE"]

    monkeypatch.setattr(app.sys, "platform", "darwin")
    monkeypatch.setitem(sys.modules, "Foundation", SimpleNamespace(NSLocale=FakeNSLocale))

    assert app._system_ui_language(tmp_path) == "de"
