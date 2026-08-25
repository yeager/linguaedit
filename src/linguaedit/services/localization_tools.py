"""Offline localization helpers: pseudolocalization, plural rules, and source diffs."""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher

_TOKENS = re.compile(
    r"(%(?:\d+\$)?[-+ #0]*\d*\.?\d*[a-zA-Z%]|\{[^{}]+\}|<[^>]+>|&[A-Za-z0-9#]+;)"
)
_ACCENTS = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "ÅƁÇÐËƑĠĦÏĴĶĿṀÑÖƤǪŔŠŢÜṼŴẊŸŽåƀçðëƒġħïĵķŀṁñöƥǫŕšţüṽŵẋÿž",
)


def pseudolocalize(text: str, expansion: float = 0.35, rtl: bool = False) -> str:
    """Accent and expand visible text while preserving placeholders and markup."""
    if not text:
        return text
    parts = _TOKENS.split(text)
    visible = []
    for part in parts:
        if not part or _TOKENS.fullmatch(part):
            visible.append(part)
            continue
        transformed = part.translate(_ACCENTS)
        letters = [char for char in transformed if char.isalpha()]
        padding = "~" * max(0, round(len(letters) * expansion))
        visible.append(transformed + padding)
    result = "".join(visible)
    if rtl:
        return f"\u202e⟦{result}⟧\u202c"
    return f"⟦{result}⟧"


CLDR_PLURAL_CATEGORIES: dict[str, tuple[str, ...]] = {
    "ar": ("zero", "one", "two", "few", "many", "other"),
    "cs": ("one", "few", "many", "other"),
    "fr": ("one", "many", "other"),
    "ja": ("other",),
    "ko": ("other",),
    "pl": ("one", "few", "many", "other"),
    "ru": ("one", "few", "many", "other"),
    "uk": ("one", "few", "many", "other"),
    "zh": ("other",),
}
_DEFAULT_PLURALS = ("one", "other")


def plural_categories(locale: str) -> tuple[str, ...]:
    """Return the CLDR categories needed by a locale."""
    language = locale.replace("_", "-").split("-", 1)[0].lower()
    return CLDR_PLURAL_CATEGORIES.get(language, _DEFAULT_PLURALS)


def missing_plural_categories(locale: str, supplied: dict[str, str]) -> tuple[str, ...]:
    """Return required categories that have no non-empty translation."""
    return tuple(category for category in plural_categories(locale) if not supplied.get(category, "").strip())


@dataclass(frozen=True)
class DiffChunk:
    """A word-level source change."""

    operation: str
    previous: str
    current: str


def source_diff(previous: str, current: str) -> list[DiffChunk]:
    """Return stable word-level changes between old and current source text."""
    old_words = re.findall(r"\s+|[^\s]+", previous)
    new_words = re.findall(r"\s+|[^\s]+", current)
    matcher = SequenceMatcher(a=old_words, b=new_words, autojunk=False)
    return [
        DiffChunk(tag, "".join(old_words[i1:i2]), "".join(new_words[j1:j2]))
        for tag, i1, i2, j1, j2 in matcher.get_opcodes()
    ]
