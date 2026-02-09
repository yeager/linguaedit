"""Video Preview Widget — plays video synced with subtitle translation.

Shows a video player that seeks to the correct timestamp when the
translator selects a subtitle entry. Non-modal, dockable alongside editor.

SPDX-License-Identifier: GPL-3.0-or-later
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSlider, QLabel, QStyle, QSizePolicy,
)
from PySide6.QtCore import Qt, QUrl, Slot
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget


def _ms_to_timestamp(ms: int) -> str:
    """Convert milliseconds to HH:MM:SS."""
    s = ms // 1000
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _parse_time_to_ms(time_str: str) -> int:
    """Parse HH:MM:SS,mmm or HH:MM:SS.mmm to milliseconds."""
    time_str = time_str.strip().replace(",", ".")
    parts = time_str.split(":")
    if len(parts) == 3:
        h, m, rest = parts
        if "." in rest:
            s, ms = rest.split(".", 1)
            ms = ms.ljust(3, "0")[:3]
        else:
            s, ms = rest, "0"
        return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)
    return 0


class VideoPreviewWidget(QWidget):
    """Embedded video player for subtitle translation workflow."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Video Preview"))
        self.setMinimumSize(480, 360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Video widget
        self._video_widget = QVideoWidget()
        self._video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self._video_widget, 1)

        # Subtitle overlay
        self._subtitle_label = QLabel("")
        self._subtitle_label.setAlignment(Qt.AlignCenter)
        self._subtitle_label.setWordWrap(True)
        self._subtitle_label.setStyleSheet(
            "QLabel { background: rgba(0,0,0,0.7); color: white; "
            "font-size: 14px; padding: 8px 16px; border-radius: 6px; }"
        )
        self._subtitle_label.setVisible(False)
        layout.addWidget(self._subtitle_label)

        # Controls
        controls = QHBoxLayout()
        controls.setContentsMargins(8, 4, 8, 8)
        controls.setSpacing(8)

        style = self.style()

        self._play_btn = QPushButton()
        self._play_btn.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self._play_btn.setFixedSize(32, 32)
        self._play_btn.clicked.connect(self._toggle_play)
        controls.addWidget(self._play_btn)

        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(0, 0)
        self._slider.sliderMoved.connect(self._on_slider_seek)
        controls.addWidget(self._slider, 1)

        self._time_label = QLabel("00:00:00 / 00:00:00")
        self._time_label.setStyleSheet("font-family: Menlo, monospace; font-size: 12px;")
        controls.addWidget(self._time_label)

        layout.addLayout(controls)

        # Media player
        self._player = QMediaPlayer()
        self._audio = QAudioOutput()
        self._player.setAudioOutput(self._audio)
        self._player.setVideoOutput(self._video_widget)
        self._player.positionChanged.connect(self._on_position_changed)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.playbackStateChanged.connect(self._on_state_changed)

        self._video_path: Optional[Path] = None

    def open_video(self, path: Path):
        """Load a video file."""
        self._video_path = path
        self._player.setSource(QUrl.fromLocalFile(str(path)))
        self.setWindowTitle(f"🎬 {path.name}")

    def seek_to_time(self, time_str: str):
        """Seek to a timestamp like '00:01:23,456' or '00:01:23.456'."""
        ms = _parse_time_to_ms(time_str)
        if ms >= 0:
            self._player.setPosition(ms)
            # Auto-play from this position
            if self._player.playbackState() != QMediaPlayer.PlaybackState.PlayingState:
                self._player.play()

    def seek_to_ms(self, ms: int):
        """Seek to a position in milliseconds."""
        self._player.setPosition(ms)
        if self._player.playbackState() != QMediaPlayer.PlaybackState.PlayingState:
            self._player.play()

    def show_subtitle(self, text: str):
        """Show subtitle text overlay."""
        if text.strip():
            self._subtitle_label.setText(text)
            self._subtitle_label.setVisible(True)
        else:
            self._subtitle_label.setVisible(False)

    def _toggle_play(self):
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
        else:
            self._player.play()

    def _on_slider_seek(self, position: int):
        self._player.setPosition(position)

    def _on_position_changed(self, position: int):
        self._slider.setValue(position)
        total = self._player.duration()
        self._time_label.setText(
            f"{_ms_to_timestamp(position)} / {_ms_to_timestamp(total)}"
        )

    def _on_duration_changed(self, duration: int):
        self._slider.setRange(0, duration)

    def _on_state_changed(self, state):
        style = self.style()
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self._play_btn.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self._play_btn.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def closeEvent(self, event):
        self._player.stop()
        super().closeEvent(event)
