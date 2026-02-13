# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2024-2026 LinguaEdit contributors
"""Toolbar customization dialog."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QDialogButtonBox, QLabel, QCheckBox,
)
from PySide6.QtCore import Qt


class ToolbarCustomizeDialog(QDialog):
    """Let users choose which toolbar actions are visible."""

    def __init__(self, actions_config: list[dict], parent=None):
        """actions_config: list of {"name": str, "group": str, "visible": bool, "action": QAction}"""
        super().__init__(parent)
        self.setWindowTitle(self.tr("Customize Toolbar"))
        self.setMinimumSize(400, 500)
        self._config = actions_config

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(self.tr("Check actions to show in toolbar:")))

        self._list = QListWidget()
        current_group = None
        for cfg in self._config:
            if cfg["group"] != current_group:
                current_group = cfg["group"]
                header = QListWidgetItem(f"── {current_group} ──")
                header.setFlags(Qt.NoItemFlags)
                self._list.addItem(header)

            item = QListWidgetItem(cfg["name"])
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if cfg["visible"] else Qt.Unchecked)
            item.setData(Qt.UserRole, cfg)
            self._list.addItem(item)

        layout.addWidget(self._list, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_visibility(self) -> dict[str, bool]:
        """Return {action_name: visible} mapping."""
        result = {}
        for i in range(self._list.count()):
            item = self._list.item(i)
            cfg = item.data(Qt.UserRole)
            if cfg:
                result[cfg["name"]] = item.checkState() == Qt.Checked
        return result
