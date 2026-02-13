# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2024-2026 LinguaEdit contributors
"""Auto-collapsing side panel with animated expand/collapse."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton,
    QFrame, QSizePolicy,
)
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, Property, Signal,
)
from PySide6.QtGui import QFont


class CollapsibleSidePanel(QWidget):
    """Wraps a QTabWidget with auto-collapse and animated show/hide."""

    toggled = Signal(bool)  # True = expanded

    def __init__(self, tab_widget: QTabWidget, parent=None):
        super().__init__(parent)
        self._tab_widget = tab_widget
        self._expanded = True
        self._target_width = 300
        self._anim: QPropertyAnimation | None = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Thin vertical tab bar when collapsed
        self._tab_bar = QFrame()
        self._tab_bar.setMaximumWidth(28)
        self._tab_bar.setMinimumWidth(28)
        self._tab_bar.setStyleSheet(
            "QFrame { background: palette(window); border-left: 1px solid palette(mid); }"
        )
        tab_bar_layout = QVBoxLayout(self._tab_bar)
        tab_bar_layout.setContentsMargins(2, 4, 2, 4)
        tab_bar_layout.setSpacing(4)

        self._toggle_btn = QPushButton("◀")
        self._toggle_btn.setMaximumWidth(24)
        self._toggle_btn.setMaximumHeight(24)
        self._toggle_btn.setToolTip(self.tr("Toggle side panel"))
        self._toggle_btn.clicked.connect(self.toggle)
        tab_bar_layout.addWidget(self._toggle_btn)

        # Vertical tab labels
        tab_labels = [self.tr("Info"), self.tr("TM"), self.tr("Ref"), self.tr("Ctx"), self.tr("Pre")]
        for label_text in tab_labels:
            btn = QPushButton(label_text)
            btn.setMaximumWidth(24)
            font = QFont()
            font.setPointSize(8)
            btn.setFont(font)
            btn.setToolTip(label_text)
            btn.clicked.connect(self._on_tab_button_clicked)
            tab_bar_layout.addWidget(btn)

        tab_bar_layout.addStretch()

        layout.addWidget(self._tab_bar)
        layout.addWidget(self._tab_widget, 1)

        self._tab_bar.setVisible(False)  # hidden when expanded

    def _on_tab_button_clicked(self):
        """Expand panel when a collapsed tab button is clicked."""
        if not self._expanded:
            self.toggle()

    def toggle(self):
        """Toggle expanded/collapsed state with animation."""
        self._expanded = not self._expanded
        self._toggle_btn.setText("◀" if self._expanded else "▶")
        self._tab_bar.setVisible(not self._expanded)

        if self._anim:
            self._anim.stop()

        if self._expanded:
            self._tab_widget.setVisible(True)
            self._anim = QPropertyAnimation(self._tab_widget, b"maximumWidth")
            self._anim.setDuration(200)
            self._anim.setStartValue(0)
            self._anim.setEndValue(self._target_width)
            self._anim.setEasingCurve(QEasingCurve.OutCubic)
            self._anim.start()
        else:
            self._target_width = self._tab_widget.width()
            self._anim = QPropertyAnimation(self._tab_widget, b"maximumWidth")
            self._anim.setDuration(200)
            self._anim.setStartValue(self._target_width)
            self._anim.setEndValue(0)
            self._anim.setEasingCurve(QEasingCurve.InCubic)
            self._anim.finished.connect(lambda: self._tab_widget.setVisible(False))
            self._anim.start()

        self.toggled.emit(self._expanded)

    def is_expanded(self) -> bool:
        return self._expanded

    def set_expanded(self, expanded: bool):
        if expanded != self._expanded:
            self.toggle()

    def auto_hide_if_empty(self, has_content: bool):
        """Auto-collapse when there's no content, expand when there is."""
        if not has_content and self._expanded:
            self.toggle()
        elif has_content and not self._expanded:
            pass  # Don't auto-expand — user chose to collapse
