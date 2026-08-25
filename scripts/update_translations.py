#!/usr/bin/env python3
"""Extract all self.tr() strings from Python source and merge into .ts file.

Unlike pyside6-lupdate, this handles:
- Multiple Python files at once
- Multiline string concatenation in self.tr()
- Preserves existing translations (non-destructive merge)

Usage: python3 scripts/update_translations.py
"""

import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

SRC_DIR = Path("src/linguaedit")
TS_DIR = SRC_DIR / "translations"


def extract_tr_strings(py_file: Path) -> list[tuple[str, str]]:
    """Extract (class_name, string) pairs from self.tr() calls."""
    with open(py_file) as f:
        content = f.read()

    # Determine class name from file
    class_match = re.search(r'class (\w+)\(', content)
    class_name = class_match.group(1) if class_match else py_file.stem

    strings = []

    # Single-line: self.tr("...")
    for m in re.finditer(r'self\.tr\(\s*"((?:[^"\\]|\\.)*)"\s*\)', content):
        strings.append((class_name, m.group(1)))

    # Multi-line: self.tr(\n  "str1"\n  "str2"\n)
    for m in re.finditer(r'self\.tr\(\s*\n((?:\s*"(?:[^"\\]|\\.)*"\s*\n?)+)\s*\)', content):
        parts = re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))
        if parts:
            strings.append((class_name, ''.join(parts)))

    # Handle multiple classes in same file
    # Re-scan with class context
    class_ranges = [(m.start(), m.group(1)) for m in re.finditer(r'class (\w+)\(', content)]
    if len(class_ranges) > 1:
        strings = []
        for i, (start, cls) in enumerate(class_ranges):
            end = class_ranges[i + 1][0] if i + 1 < len(class_ranges) else len(content)
            chunk = content[start:end]
            for m in re.finditer(r'self\.tr\(\s*"((?:[^"\\]|\\.)*)"\s*\)', chunk):
                strings.append((cls, m.group(1)))
            for m in re.finditer(r'self\.tr\(\s*\n((?:\s*"(?:[^"\\]|\\.)*"\s*\n?)+)\s*\)', chunk):
                parts = re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))
                if parts:
                    strings.append((cls, ''.join(parts)))

    return strings


def parse_ts_file(ts_path: Path) -> dict[str, dict[str, str]]:
    """Parse .ts file into {context_name: {source: translation}}."""
    tree = ET.parse(ts_path)
    root = tree.getroot()
    result = {}
    for context in root.findall("context"):
        name = context.find("name").text
        messages = {}
        for msg in context.findall("message"):
            source = msg.find("source")
            trans = msg.find("translation")
            if source is not None and source.text:
                messages[source.text] = trans.text if trans is not None and trans.text else ""
        result[name] = messages
    return result


def merge_catalog(ts_path: Path, all_strings: dict[str, set[str]]) -> int:
    """Append missing messages while preserving the catalog's formatting."""
    existing = parse_ts_file(ts_path)
    additions = {
        context: sorted(
            text.replace("\\n", "\n") for text in strings
            if text.replace("\\n", "\n") not in existing.get(context, {})
        )
        for context, strings in all_strings.items()
    }
    additions = {context: strings for context, strings in additions.items() if strings}
    if not additions:
        return 0

    content = ts_path.read_text(encoding="utf-8")
    for context, strings in sorted(additions.items()):
        messages = "".join(
            "    <message>\n"
            f"        <source>{escape(source)}</source>\n"
            "        <translation type=\"unfinished\"></translation>\n"
            "    </message>\n"
            for source in strings
        )
        marker = f"    <name>{escape(context)}</name>"
        context_start = content.find(marker)
        if context_start >= 0:
            context_end = content.find("</context>", context_start)
            content = content[:context_end] + messages + content[context_end:]
        else:
            block = f"<context>\n{marker}\n{messages}</context>\n"
            content = content.replace("</TS>", block + "</TS>")

    ts_path.write_text(content, encoding="utf-8")
    return sum(len(strings) for strings in additions.values())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check", action="store_true",
        help="report missing strings without changing catalogs",
    )
    args = parser.parse_args()

    # Extract all strings from source
    all_strings: dict[str, set[str]] = {}  # context -> set of source strings
    for py_file in sorted(SRC_DIR.rglob("*.py")):
        if "__pycache__" in str(py_file):
            continue
        for cls, text in extract_tr_strings(py_file):
            all_strings.setdefault(cls, set()).add(text)

    reference_file = TS_DIR / "linguaedit_sv.ts"
    existing = parse_ts_file(reference_file)

    # Find new strings
    new_count = 0
    for context, strings in sorted(all_strings.items()):
        existing_strings = existing.get(context, {})
        for s in sorted(strings):
            # Normalize escaped newlines from Python source to real newlines (as in .ts XML)
            normalized = s.replace("\\n", "\n")
            if normalized not in existing_strings and s not in existing_strings:
                new_count += 1
                print(f"  NEW [{context}]: {s[:80]}")

    total_in_code = sum(len(s) for s in all_strings.values())
    total_in_ts = sum(len(m) for m in existing.values())
    print(f"\nStrings in code: {total_in_code}")
    print(f"Strings in .ts:  {total_in_ts}")
    print(f"New strings:     {new_count}")

    if new_count == 0:
        print("\n✓ All strings are in the .ts file!")
    else:
        print(f"\n⚠ {new_count} strings need to be added to the .ts files")
        if args.check:
            raise SystemExit(1)

    if not args.check:
        updated = 0
        for ts_path in sorted(TS_DIR.glob("*.ts")):
            updated += merge_catalog(ts_path, all_strings)
        print(f"Updated {updated} catalog messages across all .ts files")


if __name__ == "__main__":
    main()
