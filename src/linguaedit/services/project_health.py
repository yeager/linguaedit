"""Project health and accessibility analysis."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class AccessibilityIssue:
    kind: str
    message: str
    entry_index: int


def check_accessibility(entries: list[dict]) -> list[AccessibilityIssue]:
    """Find missing labels and duplicate Qt mnemonic keys."""
    issues = []
    mnemonic_owners: dict[str, int] = {}
    for position, entry in enumerate(entries):
        index = entry.get("index", position)
        source = entry.get("msgid", "")
        target = entry.get("msgstr", "")
        if source and not target:
            issues.append(AccessibilityIssue("missing-label", "Visible text has no translation", index))
        match = re.search(r"(?<!&)&([^&\s])", target)
        if match:
            mnemonic = match.group(1).casefold()
            if mnemonic in mnemonic_owners:
                issues.append(
                    AccessibilityIssue(
                        "duplicate-mnemonic",
                        f"Mnemonic '&{match.group(1)}' is also used by entry {mnemonic_owners[mnemonic]}",
                        index,
                    )
                )
            else:
                mnemonic_owners[mnemonic] = index
    return issues


@dataclass(frozen=True)
class HealthReport:
    score: float
    translated: int
    total: int
    stale: int
    errors: int
    warnings: int
    glossary_violations: int
    accessibility_issues: int
    risks: tuple[str, ...] = field(default_factory=tuple)


def calculate_health(
    entries: list[dict],
    *,
    lint_issues: list | None = None,
    glossary_violations: list | None = None,
    accessibility_issues: list | None = None,
) -> HealthReport:
    """Calculate a deterministic, explainable project health score."""
    lint_issues = lint_issues or []
    glossary_violations = glossary_violations or []
    accessibility_issues = accessibility_issues or []
    total = len(entries)
    translated = sum(bool(entry.get("msgstr", "").strip()) for entry in entries)
    stale = sum("fuzzy" in entry.get("flags", []) or entry.get("stale", False) for entry in entries)
    def severity(issue: object) -> str:
        if isinstance(issue, dict):
            return str(issue.get("severity", ""))
        return str(getattr(issue, "severity", ""))

    errors = sum(severity(issue) == "error" for issue in lint_issues)
    warnings = sum(severity(issue) == "warning" for issue in lint_issues)
    base = translated / total * 100 if total else 100.0
    penalty = errors * 3 + warnings + stale + len(glossary_violations) * 2 + len(accessibility_issues)
    score = max(0.0, min(100.0, base - penalty))
    risks = []
    if translated < total:
        risks.append("untranslated")
    if stale:
        risks.append("stale")
    if errors:
        risks.append("qa-errors")
    if glossary_violations:
        risks.append("terminology")
    if accessibility_issues:
        risks.append("accessibility")
    return HealthReport(
        score, translated, total, stale, errors, warnings,
        len(glossary_violations), len(accessibility_issues), tuple(risks),
    )
