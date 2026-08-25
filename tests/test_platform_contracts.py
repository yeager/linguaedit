"""Offline contract tests for translation-platform adapters."""

from __future__ import annotations

import io
import urllib.error

import pytest


def test_transifex_aggregates_language_statistics(monkeypatch):
    from linguaedit.services import transifex

    monkeypatch.setattr(transifex, "_paginate", lambda *args, **kwargs: [
        {
            "attributes": {"translated_strings": 8, "reviewed_strings": 4, "total_strings": 10},
            "relationships": {"language": {"data": {"id": "l:sv"}}},
        },
        {
            "attributes": {"translated_strings": 1, "reviewed_strings": 1, "total_strings": 2},
            "relationships": {"language": {"data": {"id": "l:sv"}}},
        },
    ])
    assert transifex.fetch_project_stats("token", "org", "project") == [{
        "language": "sv", "translated": 9, "reviewed": 5, "total": 12, "pct": 75.0,
    }]


def test_weblate_normalizes_project_statistics(monkeypatch):
    from linguaedit.services import weblate

    monkeypatch.setattr(weblate, "_request", lambda *args, **kwargs: [{
        "language": "sv", "translated": 15, "fuzzy": 2, "total": 20,
    }])
    assert weblate.fetch_project_statistics("https://example.invalid", "token", "project") == [{
        "language": "sv", "translated": 15, "fuzzy": 2, "total": 20, "pct": 75.0,
    }]


def test_crowdin_normalizes_progress(monkeypatch):
    from linguaedit.services import crowdin

    monkeypatch.setattr(crowdin, "_paginate", lambda *args, **kwargs: [{"data": {
        "languageId": "sv", "phrases": {"total": 10, "translated": 8, "approved": 6},
        "translationProgress": 80, "approvalProgress": 60,
    }}])
    assert crowdin.fetch_project_progress("token", 1)[0]["pct_translated"] == 80


@pytest.mark.parametrize(
    ("module_name", "error_name"),
    [("transifex", "TransifexError"), ("weblate", "WeblateError"), ("crowdin", "CrowdinError")],
)
def test_platform_http_errors_never_echo_response_bodies(monkeypatch, module_name, error_name):
    module = __import__(f"linguaedit.services.{module_name}", fromlist=[module_name])
    secret = b"token-that-must-not-leak"
    error = urllib.error.HTTPError("https://example.invalid", 403, "denied", {}, io.BytesIO(secret))
    monkeypatch.setattr(module.urllib.request, "urlopen", lambda *args, **kwargs: (_ for _ in ()).throw(error))

    with pytest.raises(getattr(module, error_name)) as caught:
        if module_name == "weblate":
            module._request("https://example.invalid", "/api/", "token")
        else:
            module._request("/api/", "token")
    assert secret.decode() not in str(caught.value)


def test_confidence_reports_method_band_and_evidence(qapp):
    from linguaedit.services.confidence import ConfidenceCalculator

    calculator = ConfidenceCalculator()
    factors = calculator.calculate_confidence(
        "entry", "Save %s", "Spara %s",
        {"tm_match": 100, "glossary_terms": [], "similar_translations": ["Spara %s"]},
    )
    assert factors.method == "heuristic-v1"
    assert factors.evidence_ratio == 1.0
    assert factors.confidence_band == "high"
    assert "heuristic" in calculator.get_badge_text(factors.overall_score)
    calculator._executor.shutdown(wait=True)
