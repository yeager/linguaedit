"""Compile sufficiently translated Qt TS catalogs into build-only QM files."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


MIN_COMPLETION = 0.20


def translation_completion(ts_file: Path) -> tuple[int, int, float]:
    """Return finished, total, and completion ratio for a Qt TS catalog."""
    root = ET.parse(ts_file).getroot()
    finished = 0
    total = 0
    for message in root.findall(".//message"):
        translation = message.find("translation")
        if translation is not None and translation.get("type") in {"vanished", "obsolete"}:
            continue
        total += 1
        if translation is None or translation.get("type") == "unfinished":
            continue
        numerus_forms = translation.findall("numerusform")
        if numerus_forms:
            is_finished = all((form.text or "").strip() for form in numerus_forms)
        else:
            is_finished = bool("".join(translation.itertext()).strip())
        finished += int(is_finished)
    ratio = finished / total if total else 0.0
    return finished, total, ratio


def find_lrelease() -> str:
    """Find the Qt lrelease executable supplied by PySide6."""
    executable = shutil.which("pyside6-lrelease") or shutil.which("lrelease")
    if executable:
        return executable
    try:
        import PySide6
        bundled = Path(PySide6.__file__).parent / "lrelease"
        if bundled.is_file():
            return str(bundled)
    except ImportError:
        pass
    raise RuntimeError("pyside6-lrelease or lrelease is required to compile translations")


def compile_translations(
    translations_dir: Path,
    *,
    minimum: float = MIN_COMPLETION,
) -> list[Path]:
    """Compile catalogs above ``minimum`` and return generated QM paths."""
    lrelease = find_lrelease()
    generated: list[Path] = []
    for ts_file in sorted(translations_dir.glob("linguaedit_*.ts")):
        if ts_file.stem.endswith("_template"):
            continue
        finished, total, ratio = translation_completion(ts_file)
        percent = ratio * 100
        if ratio <= minimum:
            print(
                f"Skipping {ts_file.name}: {finished}/{total} "
                f"finished ({percent:.1f}%, requires > {minimum * 100:.0f}%)"
            )
            continue
        qm_file = ts_file.with_suffix(".qm")
        subprocess.run(
            [lrelease, str(ts_file), "-qm", str(qm_file)],
            check=True,
        )
        generated.append(qm_file)
        print(f"Compiled {ts_file.name}: {finished}/{total} finished ({percent:.1f}%)")
    return generated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "directory",
        nargs="?",
        type=Path,
        default=Path("src/linguaedit/translations"),
    )
    parser.add_argument("--minimum", type=float, default=MIN_COMPLETION)
    args = parser.parse_args()
    compile_translations(args.directory, minimum=args.minimum)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
