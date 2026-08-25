"""Tests for build-time TS completion filtering."""

from pathlib import Path

import translation_build


def _write_ts(path: Path, finished: int, total: int):
    messages = []
    for index in range(total):
        if index < finished:
            translation = f"<translation>Translated {index}</translation>"
        else:
            translation = '<translation type="unfinished"></translation>'
        messages.append(
            f"<message><source>Source {index}</source>{translation}</message>"
        )
    path.write_text(
        "<TS><context><name>Test</name>" + "".join(messages) + "</context></TS>",
        encoding="utf-8",
    )


def test_completion_counts_finished_messages(tmp_path):
    path = tmp_path / "linguaedit_sv.ts"
    _write_ts(path, finished=3, total=10)
    assert translation_build.translation_completion(path) == (3, 10, 0.3)


def test_build_requires_strictly_more_than_twenty_percent(tmp_path, monkeypatch):
    at_threshold = tmp_path / "linguaedit_de.ts"
    above_threshold = tmp_path / "linguaedit_sv.ts"
    _write_ts(at_threshold, finished=2, total=10)
    _write_ts(above_threshold, finished=3, total=10)

    monkeypatch.setattr(translation_build, "find_lrelease", lambda: "lrelease")

    def fake_run(command, check):
        assert check
        Path(command[-1]).write_bytes(b"compiled")

    monkeypatch.setattr(translation_build.subprocess, "run", fake_run)
    generated = translation_build.compile_translations(tmp_path)

    assert generated == [above_threshold.with_suffix(".qm")]
    assert not at_threshold.with_suffix(".qm").exists()
    assert above_threshold.with_suffix(".qm").exists()
