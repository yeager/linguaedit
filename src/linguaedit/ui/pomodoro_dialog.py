"""Small reusable Pomodoro focus timer."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QPushButton, QSpinBox, QVBoxLayout,
)


class PomodoroDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Pomodoro Timer"))
        self.setMinimumWidth(300)
        self._remaining = 25 * 60

        layout = QVBoxLayout(self)
        duration_row = QHBoxLayout()
        duration_row.addWidget(QLabel(self.tr("Focus minutes:")))
        self._minutes = QSpinBox()
        self._minutes.setRange(1, 120)
        self._minutes.setValue(25)
        self._minutes.valueChanged.connect(self.reset)
        duration_row.addWidget(self._minutes)
        layout.addLayout(duration_row)

        self._display = QLabel()
        self._display.setStyleSheet("font-size: 36px; font-weight: bold;")
        self._display.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._display)

        buttons = QHBoxLayout()
        self._start = QPushButton(self.tr("Start"))
        self._start.clicked.connect(self.toggle)
        reset_button = QPushButton(self.tr("Reset"))
        reset_button.clicked.connect(self.reset)
        buttons.addWidget(self._start)
        buttons.addWidget(reset_button)
        layout.addLayout(buttons)

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)
        self.reset()

    def toggle(self):
        if self._timer.isActive():
            self._timer.stop()
            self._start.setText(self.tr("Resume"))
        else:
            self._timer.start()
            self._start.setText(self.tr("Pause"))

    def reset(self):
        self._timer.stop() if hasattr(self, "_timer") else None
        self._remaining = self._minutes.value() * 60
        self._start.setText(self.tr("Start"))
        self._update_display()

    def _tick(self):
        self._remaining = max(0, self._remaining - 1)
        self._update_display()
        if self._remaining == 0:
            self._timer.stop()
            self._start.setText(self.tr("Start"))
            self._display.setText(self.tr("Time for a break!"))

    def _update_display(self):
        minutes, seconds = divmod(self._remaining, 60)
        self._display.setText(f"{minutes:02d}:{seconds:02d}")
