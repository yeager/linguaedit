"""Atomic local session journals for autosave and crash recovery."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RecoverySnapshot:
    source_path: str
    source_mtime_ns: int
    saved_at: str
    entries: list[dict[str, Any]]


class RecoveryJournal:
    """Store recovery data locally, separate from project files and Git."""

    def __init__(self, directory: Path | None = None):
        self.directory = directory or Path.home() / ".local/share/linguaedit/recovery"
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)

    def _path_for(self, source_path: str | Path) -> Path:
        resolved = str(Path(source_path).resolve())
        digest = hashlib.sha256(resolved.encode()).hexdigest()
        return self.directory / f"{digest}.json"

    def save(self, source_path: str | Path, entries: list[dict[str, Any]]) -> Path:
        source = Path(source_path).resolve()
        snapshot = RecoverySnapshot(
            source_path=str(source),
            source_mtime_ns=source.stat().st_mtime_ns if source.exists() else 0,
            saved_at=datetime.now(UTC).isoformat(),
            entries=entries,
        )
        destination = self._path_for(source)
        temporary = destination.with_suffix(".tmp")
        temporary.write_text(json.dumps(asdict(snapshot), ensure_ascii=False), "utf-8")
        os.chmod(temporary, 0o600)
        temporary.replace(destination)
        return destination

    def load(self, source_path: str | Path) -> RecoverySnapshot | None:
        journal = self._path_for(source_path)
        if not journal.exists():
            return None
        try:
            data = json.loads(journal.read_text("utf-8"))
            if Path(data["source_path"]).resolve() != Path(source_path).resolve():
                return None
            return RecoverySnapshot(**data)
        except (OSError, ValueError, KeyError, TypeError):
            return None

    def needs_recovery(self, source_path: str | Path) -> bool:
        snapshot = self.load(source_path)
        if snapshot is None:
            return False
        source = Path(source_path)
        current_mtime = source.stat().st_mtime_ns if source.exists() else 0
        return snapshot.source_mtime_ns >= current_mtime

    def discard(self, source_path: str | Path) -> None:
        self._path_for(source_path).unlink(missing_ok=True)
