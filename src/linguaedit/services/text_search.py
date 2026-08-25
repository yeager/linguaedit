"""Reusable matching and replacement primitives for translation editors."""

from __future__ import annotations

import re


def build_pattern(pattern: str, *, case_sensitive: bool = False,
                  whole_words: bool = False, regex: bool = False) -> re.Pattern[str] | None:
    """Compile search options, returning ``None`` for an invalid expression."""
    flags = 0 if case_sensitive else re.IGNORECASE
    expression = pattern if regex else re.escape(pattern)
    if whole_words:
        expression = rf"\b(?:{expression})\b"
    try:
        return re.compile(expression, flags)
    except re.error:
        return None


def matches(text: str, pattern: str, *, case_sensitive: bool = False,
            whole_words: bool = False, regex: bool = False) -> bool:
    """Return whether text matches the selected search options."""
    compiled = build_pattern(
        pattern, case_sensitive=case_sensitive, whole_words=whole_words, regex=regex,
    )
    return compiled.search(text) is not None if compiled else False


def replace(text: str, pattern: str, replacement: str, *,
            case_sensitive: bool = False, whole_words: bool = False,
            regex: bool = False, count: int = 0) -> tuple[str, int]:
    """Replace matches and return ``(new_text, replacement_count)``."""
    compiled = build_pattern(
        pattern, case_sensitive=case_sensitive, whole_words=whole_words, regex=regex,
    )
    if compiled is None:
        return text, 0
    return compiled.subn(replacement, text, count=count)
