from pathlib import Path
from types import SimpleNamespace

import pytest

from linguaedit.services import translator


def test_opennmt_engine_is_registered():
    engine = translator.ENGINES["opennmt"]
    assert engine["free"] is True
    assert engine["fn"] is translator.translate_opennmt


def test_opennmt_requires_a_model(monkeypatch):
    monkeypatch.delenv("OPENNMT_MODEL", raising=False)
    with pytest.raises(translator.TranslationError, match="model not configured"):
        translator.translate_opennmt("Hello")


def test_opennmt_translates_via_local_cli(tmp_path, monkeypatch):
    model = tmp_path / "model.pt"
    model.write_bytes(b"model")
    monkeypatch.setattr(translator.shutil, "which", lambda command: "/usr/bin/onmt_translate")

    def fake_run(arguments, **kwargs):
        source = Path(arguments[arguments.index("-src") + 1])
        output = Path(arguments[arguments.index("-output") + 1])
        assert source.read_text(encoding="utf-8") == "Hello world"
        assert kwargs["check"] is False
        output.write_text("Hej världen\n", encoding="utf-8")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(translator.subprocess, "run", fake_run)
    assert translator.translate_opennmt(
        "Hello world", opennmt_model=str(model)
    ) == "Hej världen"


def test_opennmt_reports_cli_failure(tmp_path, monkeypatch):
    model = tmp_path / "model.pt"
    model.write_bytes(b"model")
    monkeypatch.setattr(translator.shutil, "which", lambda command: "/usr/bin/onmt_translate")
    monkeypatch.setattr(
        translator.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=2, stdout="", stderr="invalid model"
        ),
    )
    with pytest.raises(translator.TranslationError, match="invalid model"):
        translator.translate_opennmt("Hello", opennmt_model=str(model))
