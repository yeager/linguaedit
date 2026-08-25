"""Inspect source catalogs and built wheels without extracting them."""

from __future__ import annotations

import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from pathlib import Path

MIN_COMPLETION = 0.20


def _translation_completion(path: Path) -> tuple[int, int, float]:
    root = ET.parse(path).getroot()
    messages = root.findall(".//message")
    finished = 0
    for message in messages:
        translation = message.find("translation")
        if (
            translation is not None
            and translation.get("type") not in {"unfinished", "obsolete", "vanished"}
            and "".join(translation.itertext()).strip()
        ):
            finished += 1
    total = len(messages)
    return finished, total, finished / total if total else 0.0


@dataclass(frozen=True)
class CatalogBuildStatus:
    locale: str
    finished: int
    total: int
    completion: float
    will_build: bool
    reason: str


def inspect_catalogs(directory: str | Path) -> list[CatalogBuildStatus]:
    """Explain which Qt catalogs qualify for compilation."""
    result = []
    for path in sorted(Path(directory).glob("linguaedit_*.ts")):
        locale = path.stem.removeprefix("linguaedit_")
        finished, total, completion = _translation_completion(path)
        qualifies = total > 0 and completion > MIN_COMPLETION
        reason = (
            f"{completion:.1%} is above {MIN_COMPLETION:.0%}"
            if qualifies
            else f"{completion:.1%} is not above {MIN_COMPLETION:.0%}"
        )
        result.append(CatalogBuildStatus(locale, finished, total, completion, qualifies, reason))
    return result


def inspect_wheel(path: str | Path) -> dict[str, list[str]]:
    """List compiled and source translation assets in a wheel."""
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
    return {
        "qm": sorted(name for name in names if name.endswith(".qm")),
        "ts": sorted(name for name in names if name.endswith(".ts")),
    }
