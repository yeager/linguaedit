"""Import and export terminology using CSV, TSV, and TBX."""

from __future__ import annotations

import csv
import xml.etree.ElementTree as ET
from dataclasses import asdict
from pathlib import Path

from linguaedit.services.glossary import GlossaryTerm


def import_delimited(path: str | Path) -> list[GlossaryTerm]:
    """Import source/target terms from a UTF-8 CSV or TSV file."""
    path = Path(path)
    delimiter = "\t" if path.suffix.lower() in {".tsv", ".tab"} else ","
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=delimiter)
        return [
            GlossaryTerm(
                source=(row.get("source") or "").strip(),
                target=(row.get("target") or "").strip(),
                notes=(row.get("notes") or "").strip(),
                domain=(row.get("domain") or "").strip(),
                variants=tuple(
                    value.strip() for value in (row.get("variants") or "").split("|") if value.strip()
                ),
                forbidden=(row.get("forbidden") or "").strip().lower() in {"1", "true", "yes"},
            )
            for row in reader
            if (row.get("source") or "").strip() and (row.get("target") or "").strip()
        ]


def export_delimited(terms: list[GlossaryTerm], path: str | Path) -> None:
    path = Path(path)
    delimiter = "\t" if path.suffix.lower() in {".tsv", ".tab"} else ","
    with path.open("w", encoding="utf-8", newline="") as stream:
        fields = ("source", "target", "notes", "domain", "variants", "forbidden")
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(
            {
                **asdict(term),
                "variants": "|".join(term.variants),
                "forbidden": str(term.forbidden).lower(),
            }
            for term in terms
        )


def import_tbx(path: str | Path, source_lang: str, target_lang: str) -> list[GlossaryTerm]:
    """Import bilingual terms from TBX termEntry/langSet/tig structures."""
    root = ET.parse(path).getroot()
    terms = []
    for entry in root.findall(".//{*}termEntry"):
        by_language: dict[str, str] = {}
        for language_set in entry.findall("./{*}langSet"):
            language = (
                language_set.get("{http://www.w3.org/XML/1998/namespace}lang", "")
                .replace("_", "-")
                .lower()
            )
            term = language_set.findtext(".//{*}term", default="").strip()
            if term:
                by_language[language] = term
        source = _language_term(by_language, source_lang)
        target = _language_term(by_language, target_lang)
        if source and target:
            terms.append(GlossaryTerm(source, target))
    return terms


def _language_term(terms: dict[str, str], language: str) -> str:
    normalized = language.replace("_", "-").lower()
    return terms.get(normalized) or terms.get(normalized.split("-", 1)[0], "")
