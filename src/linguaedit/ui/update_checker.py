"""Background update checker with non-intrusive dialog."""

from __future__ import annotations

import json
import time
from typing import Optional

from PySide6.QtCore import QThread, Signal, QSettings, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox,
    QTextEdit,
)

from linguaedit import __version__

GITHUB_API_URL = "https://api.github.com/repos/yeager/linguaedit/releases/latest"
CHECK_INTERVAL_SECONDS = 86400  # once per day


class _UpdateWorker(QThread):
    """Background thread that checks GitHub for a newer release."""

    update_available = Signal(str, str, str, str)  # version, notes, html_url, tag

    def run(self):
        try:
            import urllib.request

            req = urllib.request.Request(
                GITHUB_API_URL,
                headers={"Accept": "application/vnd.github+json", "User-Agent": "LinguaEdit"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())

            tag = data.get("tag_name", "")
            latest = tag.lstrip("v")
            if not latest:
                return

            from packaging.version import Version

            if Version(latest) > Version(__version__):
                self.update_available.emit(
                    latest,
                    data.get("body", ""),
                    data.get("html_url", ""),
                    tag,
                )
        except Exception:
            pass  # silently skip on any error


class UpdateDialog(QDialog):
    """Non-intrusive dialog showing available update info."""

    def __init__(self, parent, new_version: str, notes: str, html_url: str):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Update Available"))
        self.resize(520, 380)
        self._html_url = html_url
        self._new_version = new_version

        layout = QVBoxLayout(self)

        header = QLabel(
            self.tr("A new version of LinguaEdit is available!")
        )
        header.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(header)

        version_label = QLabel(
            self.tr("Current version: %s\nNew version: %s") % (__version__, new_version)
        )
        layout.addWidget(version_label)

        if notes:
            notes_label = QLabel(self.tr("Release notes:"))
            layout.addWidget(notes_label)
            notes_view = QTextEdit()
            notes_view.setReadOnly(True)
            notes_view.setMarkdown(notes)
            layout.addWidget(notes_view)

        self._skip_check = QCheckBox(self.tr("Skip this version"))
        layout.addWidget(self._skip_check)

        btn_row = QHBoxLayout()
        download_btn = QPushButton(self.tr("Download"))
        download_btn.setDefault(True)
        download_btn.clicked.connect(self._on_download)
        remind_btn = QPushButton(self.tr("Remind me later"))
        remind_btn.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(remind_btn)
        btn_row.addWidget(download_btn)
        layout.addLayout(btn_row)

    def _on_download(self):
        QDesktopServices.openUrl(QUrl(self._html_url))
        self._save_skip_if_checked()
        self.accept()

    def reject(self):
        self._save_skip_if_checked()
        super().reject()

    def _save_skip_if_checked(self):
        if self._skip_check.isChecked():
            settings = QSettings("LinguaEdit", "LinguaEdit")
            settings.setValue("skip_version", self._new_version)


class UpdateChecker:
    """Manages the startup update check lifecycle."""

    def __init__(self, parent_window):
        self._parent = parent_window
        self._worker: Optional[_UpdateWorker] = None

    def check(self):
        """Start a background check if enough time has passed."""
        settings = QSettings("LinguaEdit", "LinguaEdit")

        last_check = settings.value("last_update_check", 0)
        try:
            last_check = int(last_check)
        except (TypeError, ValueError):
            last_check = 0

        now = int(time.time())
        if now - last_check < CHECK_INTERVAL_SECONDS:
            return

        settings.setValue("last_update_check", now)

        self._worker = _UpdateWorker()
        self._worker.update_available.connect(self._on_update_available)
        self._worker.finished.connect(self._cleanup)
        self._worker.start()

    def _on_update_available(self, version: str, notes: str, html_url: str, tag: str):
        settings = QSettings("LinguaEdit", "LinguaEdit")
        skip = settings.value("skip_version", "")
        if skip == version:
            return

        dlg = UpdateDialog(self._parent, version, notes, html_url)
        dlg.exec()

    def _cleanup(self):
        if self._worker:
            self._worker.deleteLater()
            self._worker = None
