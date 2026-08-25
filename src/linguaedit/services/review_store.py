"""Local per-segment review states and comment threads."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

VALID_STATES = frozenset({"draft", "needs_review", "approved", "rejected"})


@dataclass(frozen=True)
class ReviewComment:
    author: str
    text: str
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class SegmentReview:
    status: str = "draft"
    assignee: str = ""
    comments: list[ReviewComment] = field(default_factory=list)


class ReviewStore:
    """Persist review metadata locally with restrictive permissions."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._reviews: dict[str, SegmentReview] = {}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text("utf-8"))
            self._reviews = {
                key: SegmentReview(
                    status=value.get("status", "draft"),
                    assignee=value.get("assignee", ""),
                    comments=[ReviewComment(**comment) for comment in value.get("comments", [])],
                )
                for key, value in data.items()
            }
        except (OSError, ValueError, TypeError):
            self._reviews = {}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(
            json.dumps({key: asdict(value) for key, value in self._reviews.items()}, ensure_ascii=False, indent=2),
            "utf-8",
        )
        os.chmod(temporary, 0o600)
        temporary.replace(self.path)

    def get(self, segment_id: str | int) -> SegmentReview:
        return self._reviews.setdefault(str(segment_id), SegmentReview())

    def update(self, segment_id: str | int, *, status: str | None = None, assignee: str | None = None) -> None:
        review = self.get(segment_id)
        if status is not None:
            if status not in VALID_STATES:
                raise ValueError(f"Unsupported review status: {status}")
            review.status = status
        if assignee is not None:
            review.assignee = assignee.strip()
        self.save()

    def add_comment(self, segment_id: str | int, text: str, author: str = "") -> None:
        if not text.strip():
            raise ValueError("Review comments cannot be empty")
        self.get(segment_id).comments.append(ReviewComment(author.strip(), text.strip()))
        self.save()
