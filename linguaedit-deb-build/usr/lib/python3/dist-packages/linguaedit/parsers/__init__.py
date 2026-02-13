"""File format parsers for PO, TS, JSON, XLIFF, Android, ARB, PHP, YAML, SDLXLIFF, and MQXLIFF."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Union

try:
    import defusedxml.ElementTree as _safe_ET
    _HAS_DEFUSEDXML = True
except ImportError:
    _HAS_DEFUSEDXML = False


def _make_safe_parser() -> ET.XMLParser:
    """Create an XMLParser with XXE protection (best-effort for Python 3.14+)."""
    parser = ET.XMLParser()
    # Python < 3.14 exposes the expat parser as .parser
    _expat = getattr(parser, 'parser', None)
    if _expat is not None:
        try:
            _expat.UseForeignDTD(False)
            _expat.SetParamEntityParsing(0)  # XML_PARAM_ENTITY_PARSING_NEVER
            _expat.ExternalEntityRefHandler = lambda *a: 0
        except Exception:
            pass
    return parser


def safe_parse_xml(path: Union[str, Path]) -> ET.ElementTree:
    """Parse XML with external entity resolution disabled (XXE protection).

    Uses defusedxml when available (recommended), otherwise falls back to
    best-effort expat hardening.
    """
    if _HAS_DEFUSEDXML:
        return _safe_ET.parse(str(path))
    return ET.parse(str(path), parser=_make_safe_parser())


def safe_fromstring_xml(text: Union[str, bytes]) -> ET.Element:
    """Parse XML string with external entity resolution disabled (XXE protection)."""
    if _HAS_DEFUSEDXML:
        return _safe_ET.fromstring(text)
    return ET.fromstring(text, parser=_make_safe_parser())
