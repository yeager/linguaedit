"""UI language selection tests."""

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
