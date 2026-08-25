"""Regression tests for the offline localization feature suite."""

import json
import stat
import zipfile
from pathlib import Path

import pytest

from linguaedit.services.glossary import GlossaryTerm
from linguaedit.services.localization_tools import (
    missing_plural_categories,
    plural_categories,
    pseudolocalize,
    source_diff,
)
from linguaedit.services.package_inspector import inspect_catalogs, inspect_wheel
from linguaedit.services.plugins import PLUGIN_API_VERSION, PluginBase
from linguaedit.services.project_health import calculate_health, check_accessibility
from linguaedit.services.recovery import RecoveryJournal
from linguaedit.services.review_store import ReviewStore
from linguaedit.services.security_policy import (
    NetworkPolicy,
    redact,
    scan_text_for_secrets,
)
from linguaedit.services.terminology_io import (
    export_delimited,
    import_delimited,
    import_tbx,
)


def test_pseudolocalization_preserves_placeholders_and_markup():
    result = pseudolocalize("Save {count} <b>%1</b>")
    assert result.startswith("⟦") and result.endswith("⟧")
    assert "{count}" in result
    assert "<b>" in result and "</b>" in result
    assert "%1" in result
    assert len(result) > len("Save {count} <b>%1</b>")


def test_plural_categories_and_missing_forms():
    assert plural_categories("ja-JP") == ("other",)
    assert plural_categories("pl_PL") == ("one", "few", "many", "other")
    assert missing_plural_categories("sv", {"one": "en", "other": ""}) == ("other",)


def test_source_diff_preserves_equal_and_changed_chunks():
    chunks = source_diff("Save the file", "Save this file now")
    assert chunks[0].operation == "equal"
    assert any(chunk.operation != "equal" for chunk in chunks)


def test_recovery_journal_is_private_and_atomic(tmp_path):
    source = tmp_path / "catalog.po"
    source.write_text("original", "utf-8")
    journal = RecoveryJournal(tmp_path / "recovery")
    path = journal.save(source, [{"index": 1, "msgstr": "utkast"}])
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert journal.needs_recovery(source)
    assert journal.load(source).entries[0]["msgstr"] == "utkast"
    journal.discard(source)
    assert journal.load(source) is None


def _write_catalog(path: Path, finished: int, total: int) -> None:
    messages = []
    for index in range(total):
        translation = f"<translation>T{index}</translation>" if index < finished else '<translation type="unfinished"/>'
        messages.append(f"<message><source>S{index}</source>{translation}</message>")
    path.write_text(f"<TS><context>{''.join(messages)}</context></TS>", "utf-8")


def test_package_inspector_explains_threshold_and_wheel_contents(tmp_path):
    _write_catalog(tmp_path / "linguaedit_sv.ts", 3, 10)
    _write_catalog(tmp_path / "linguaedit_de.ts", 2, 10)
    statuses = {status.locale: status for status in inspect_catalogs(tmp_path)}
    assert statuses["sv"].will_build
    assert not statuses["de"].will_build

    wheel = tmp_path / "test.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("pkg/translations/linguaedit_sv.qm", b"compiled")
    assert inspect_wheel(wheel) == {"qm": ["pkg/translations/linguaedit_sv.qm"], "ts": []}


def test_accessibility_and_health_are_explainable():
    entries = [
        {"index": 0, "msgid": "Open", "msgstr": "&Öppna", "flags": []},
        {"index": 1, "msgid": "Other", "msgstr": "&Övrigt", "flags": ["fuzzy"]},
        {"index": 2, "msgid": "Save", "msgstr": "", "flags": []},
    ]
    accessibility = check_accessibility(entries)
    assert {issue.kind for issue in accessibility} == {"duplicate-mnemonic", "missing-label"}
    health = calculate_health(
        entries,
        lint_issues=[{"severity": "error"}],
        glossary_violations=[object()],
        accessibility_issues=accessibility,
    )
    assert 0 < health.score < 100
    assert health.risks == ("untranslated", "stale", "qa-errors", "terminology", "accessibility")


def test_network_policy_secret_scan_and_redaction_do_not_echo_secrets():
    policy = NetworkPolicy(frozenset({"api.example.com"}))
    assert policy.validate("https://api.example.com/v1")
    with pytest.raises(ValueError):
        policy.validate("http://api.example.com/v1")
    with pytest.raises(ValueError):
        policy.validate("https://localhost/v1")

    secret = "ghp_" + "abcdefghijklmnopqrstuvwxyz123456"
    findings = scan_text_for_secrets(f"TOKEN='{secret}'", "settings.py")
    assert findings and secret not in repr(findings)
    assert secret not in redact(f"failed: {secret}")


def test_review_store_persists_status_assignment_and_comments(tmp_path):
    path = tmp_path / "reviews.json"
    store = ReviewStore(path)
    store.update(3, status="approved", assignee="Ada")
    store.add_comment(3, "Checked terminology", "Lin")
    restored = ReviewStore(path).get(3)
    assert restored.status == "approved"
    assert restored.assignee == "Ada"
    assert restored.comments[0].text == "Checked terminology"
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_terminology_csv_tsv_and_tbx_round_trip(tmp_path):
    terms = [GlossaryTerm("Save", "Spara", "Verb", "UI")]
    csv_path = tmp_path / "terms.csv"
    tsv_path = tmp_path / "terms.tsv"
    export_delimited(terms, csv_path)
    export_delimited(terms, tsv_path)
    assert import_delimited(csv_path) == terms
    assert import_delimited(tsv_path) == terms

    tbx = tmp_path / "terms.tbx"
    tbx.write_text(
        """<tbx><text><body><termEntry id="1">
        <langSet xml:lang="en"><tig><term>Open</term></tig></langSet>
        <langSet xml:lang="sv"><tig><term>Öppna</term></tig></langSet>
        </termEntry></body></text></tbx>""",
        "utf-8",
    )
    imported = import_tbx(tbx, "en-US", "sv-SE")
    assert imported == [GlossaryTerm("Open", "Öppna")]


def test_review_file_contains_no_implicit_credentials(tmp_path):
    path = tmp_path / "reviews.json"
    ReviewStore(path).update("segment", status="needs_review")
    assert json.loads(path.read_text("utf-8"))["segment"]["status"] == "needs_review"


def test_plugin_contract_has_a_stable_version():
    assert PLUGIN_API_VERSION == "1.0"
    assert PluginBase.api_version == PLUGIN_API_VERSION
