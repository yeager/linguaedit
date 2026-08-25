"""Network and Git safety policies that never persist credentials."""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

_SECRET_PATTERNS = {
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "github-token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "generic-api-key": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    "credential-assignment": re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]"
    ),
}


@dataclass(frozen=True)
class SecretFinding:
    path: str
    line: int
    kind: str


def scan_text_for_secrets(text: str, path: str = "") -> list[SecretFinding]:
    """Return finding metadata without returning the matched secret."""
    findings = []
    for number, line in enumerate(text.splitlines(), 1):
        for kind, pattern in _SECRET_PATTERNS.items():
            if pattern.search(line):
                findings.append(SecretFinding(path, number, kind))
    return findings


def scan_paths(paths: list[str | Path], root: str | Path | None = None) -> list[SecretFinding]:
    """Scan explicit text files; symlinks and files outside *root* are refused."""
    root_path = Path(root).resolve() if root else None
    findings = []
    for item in paths:
        path = Path(item)
        resolved = path.resolve()
        if path.is_symlink() or (root_path and not resolved.is_relative_to(root_path)):
            continue
        try:
            findings.extend(scan_text_for_secrets(path.read_text("utf-8"), str(path)))
        except (OSError, UnicodeDecodeError):
            continue
    return findings


@dataclass(frozen=True)
class NetworkPolicy:
    """Allow HTTPS requests only to explicitly configured public hosts."""

    allowed_hosts: frozenset[str]

    def validate(self, url: str) -> str:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower().rstrip(".")
        if parsed.scheme != "https" or not host or parsed.username or parsed.password:
            raise ValueError("Only credential-free HTTPS URLs are allowed")
        if host == "localhost" or host.endswith(".localhost") or host.endswith(".local"):
            raise ValueError("Private and local network destinations are not allowed")
        if host not in self.allowed_hosts:
            raise ValueError("Host is not allowed by the active network policy")
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            address = None
        if address and (address.is_private or address.is_loopback or address.is_link_local):
            raise ValueError("Private and local network destinations are not allowed")
        return url


def redact(value: str, secrets: list[str] | tuple[str, ...] = ()) -> str:
    """Redact supplied credentials and known token shapes from logs."""
    result = value
    for secret in secrets:
        if secret:
            result = result.replace(secret, "[REDACTED]")
    for pattern in _SECRET_PATTERNS.values():
        result = pattern.sub("[REDACTED]", result)
    return result
