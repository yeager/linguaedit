"""Java Properties parser — hantera Java .properties-filer."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Union


@dataclass
class JavaPropertiesEntry:
    """En enskild nyckel-värde-par i .properties-format."""
    key: str
    value: str = ""
    comment: str = ""
    line_number: int = 0
    is_comment_line: bool = False  # För rena kommentarrader


@dataclass
class JavaPropertiesFileData:
    """Java Properties fildata."""
    path: Path
    entries: List[JavaPropertiesEntry] = field(default_factory=list)
    encoding: str = "utf-8"
    header_comment: str = ""

    @property
    def total_count(self) -> int:
        return len(self.entries)

    @property
    def translated_count(self) -> int:
        return sum(bool(entry.value) for entry in self.entries)

    @property
    def untranslated_count(self) -> int:
        return self.total_count - self.translated_count

    @property
    def fuzzy_count(self) -> int:
        return 0


def _unescape_properties_value(value: str) -> str:
    """Unescape Java Properties-värde."""
    result = []
    i = 0
    while i < len(value):
        if value[i] != "\\" or i + 1 == len(value):
            result.append(value[i])
            i += 1
            continue
        i += 1
        char = value[i]
        if char == "u" and i + 4 < len(value):
            digits = value[i + 1:i + 5]
            if re.fullmatch(r"[0-9a-fA-F]{4}", digits):
                result.append(chr(int(digits, 16)))
                i += 5
                continue
        result.append({"n": "\n", "r": "\r", "t": "\t", "f": "\f"}.get(char, char))
        i += 1
    return "".join(result)


def _escape_properties_value(value: str) -> str:
    """Escape Java Properties-värde."""
    # Escape specialtecken
    escapes = {
        '\\': '\\\\',
        '\n': '\\n',
        '\r': '\\r',
        '\t': '\\t',
        '\f': '\\f',
    }
    
    for unescaped, escaped in escapes.items():
        value = value.replace(unescaped, escaped)
    
    # Escape unicode-tecken utanför ASCII
    result = ""
    for char in value:
        if ord(char) > 127:
            result += f"\\u{ord(char):04x}"
        else:
            result += char
    
    return result


def _parse_properties_line(line: str) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Parsa en rad från properties-fil. Returnerar (key, value, comment)."""
    line = line.lstrip()
    
    # Tomma rader
    if not line:
        return None, None, None
    
    # Kommentarrader (# eller !)
    if line.startswith('#') or line.startswith('!'):
        comment = line[1:].strip()
        return None, None, comment
    
    # Hitta separator (=, :, eller whitespace)
    # Hantera escaped separators
    separator_pos = -1
    in_escape = False
    
    for i, char in enumerate(line):
        if in_escape:
            in_escape = False
            continue
        if char == '\\':
            in_escape = True
            continue
        if char in '=:' or char.isspace():
            separator_pos = i
            break
    
    if separator_pos == -1:
        # Ingen separator funnen, hela raden är key med tomt värde
        return line, "", None
    
    key = line[:separator_pos]
    value_part = line[separator_pos:]
    if value_part[:1].isspace():
        value_part = value_part.lstrip(" \t\f")
    if value_part[:1] in ("=", ":"):
        value_part = value_part[1:]
    value_part = value_part.lstrip(" \t\f")
    
    return key, value_part, None


def _has_continuation(line: str) -> bool:
    """Java Properties continues a line only after an odd number of slashes."""
    slash_count = len(line) - len(line.rstrip("\\"))
    return slash_count % 2 == 1


def parse_java_properties(path: Union[str, Path]) -> JavaPropertiesFileData:
    """Parsa Java .properties-fil."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    # Läs fil med encoding-detektion
    content = ""
    encoding = "utf-8"
    
    for enc in ["utf-8", "latin1", "cp1252", "iso-8859-1"]:
        try:
            content = path.read_text(encoding=enc)
            encoding = enc
            break
        except UnicodeDecodeError:
            continue
    
    if not content:
        raise ValueError(f"Could not decode file: {path}")
    
    physical_lines = content.splitlines()
    lines = []
    i = 0
    while i < len(physical_lines):
        logical = physical_lines[i]
        while _has_continuation(logical) and i + 1 < len(physical_lines):
            logical = logical[:-1]
            i += 1
            logical += physical_lines[i].lstrip(" \t\f")
        lines.append(logical)
        i += 1
    entries = []
    header_comments = []
    in_header = True
    current_key = None
    current_value = ""
    current_comment = ""
    pending_comments = []
    
    for line_num, line in enumerate(lines, 1):
        key, value, comment = _parse_properties_line(line)
        
        if comment is not None and key is None:
            if in_header:
                header_comments.append(comment)
            else:
                pending_comments.append(comment)
            continue
        
        if key is not None:
            in_header = False
            
            # Spara föregående entry om vi har en
            if current_key is not None:
                entry = JavaPropertiesEntry(
                    key=current_key,
                    value=_unescape_properties_value(current_value),
                    comment=current_comment,
                    line_number=line_num - 1
                )
                entries.append(entry)
            
            # Börja ny entry
            current_key = _unescape_properties_value(key)
            current_value = value or ""
            current_comment = "\n".join(pending_comments)
            pending_comments.clear()
        
    # Spara sista entry
    if current_key is not None:
        entry = JavaPropertiesEntry(
            key=current_key,
            value=_unescape_properties_value(current_value),
            comment=current_comment,
            line_number=len(lines)
        )
        entries.append(entry)
    
    return JavaPropertiesFileData(
        path=path,
        entries=entries,
        encoding=encoding,
        header_comment="\n".join(header_comments)
    )


def save_java_properties(file_data: JavaPropertiesFileData, path: Optional[Path] = None) -> None:
    """Spara Java .properties-fil."""
    if path:
        file_data.path = path
    
    lines = []
    
    # Header-kommentar
    if file_data.header_comment:
        for line in file_data.header_comment.split('\n'):
            if line.strip():
                lines.append(f"# {line.strip()}")
            else:
                lines.append("#")
        lines.append("")
    
    # Entries
    for entry in file_data.entries:
        # Kommentar för denna entry
        if entry.comment:
            for comment_line in entry.comment.split('\n'):
                if comment_line.strip():
                    lines.append(f"# {comment_line.strip()}")
        
        # Escape keys as well as values: separators, leading spaces and
        # backslashes have syntactic meaning in Java Properties.
        escaped_key = _escape_properties_value(entry.key).replace("=", "\\=").replace(":", "\\:")
        escaped_key = escaped_key.replace(" ", "\\ ").replace("#", "\\#").replace("!", "\\!")
        escaped_value = _escape_properties_value(entry.value)
        leading_spaces = len(escaped_value) - len(escaped_value.lstrip(" "))
        escaped_value = "\\ " * leading_spaces + escaped_value[leading_spaces:]
        # Long physical lines are valid; wrapping can change continuation
        # semantics and split escape sequences.
        lines.append(f"{escaped_key}={escaped_value}")
        
        lines.append("")  # Tom rad mellan entries
    
    content = '\n'.join(lines)
    file_data.path.write_text(content, encoding=file_data.encoding)
