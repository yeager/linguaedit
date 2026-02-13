"""Layout Simulator Dialog - Test text rendering with different fonts and widths."""

from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QSpinBox, QComboBox, QFormLayout, QGroupBox,
    QFrame, QSizePolicy, QSlider, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QFontMetrics, QPainter, QColor, QPalette


class TextRenderWidget(QFrame):
    """Custom widget to render text and show pixel measurements."""
    
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Box)
        self.setMinimumHeight(100)
        self._text = ""
        self._font = QFont()
        self._max_width = 200
        self._show_overflow = True
        
    def set_text(self, text: str):
        self._text = text
        self.update()
        
    def set_font_settings(self, font: QFont):
        self._font = font
        self.update()
        
    def set_max_width(self, width: int):
        self._max_width = width
        self.update()
        
    def set_show_overflow(self, show: bool):
        self._show_overflow = show
        self.update()
    
    def paintEvent(self, event):
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setFont(self._font)
        
        metrics = QFontMetrics(self._font)
        text_width = metrics.horizontalAdvance(self._text)
        text_height = metrics.height()
        
        # Draw max width boundary
        painter.setPen(QColor(100, 100, 100))
        painter.drawLine(10 + self._max_width, 10, 10 + self._max_width, self.height() - 10)
        
        # Draw text
        text_x = 10
        text_y = 30
        
        if text_width > self._max_width and self._show_overflow:
            painter.setPen(QColor(255, 0, 0))  # Red for overflow
        else:
            painter.setPen(self.palette().color(QPalette.Text))
            
        painter.drawText(text_x, text_y, self._text)
        
        # Draw measurements
        painter.setPen(QColor(100, 100, 100))
        painter.drawText(text_x, text_y + text_height + 10, 
                        f"Width: {text_width}px")
        
        if text_width > self._max_width:
            overflow = text_width - self._max_width
            painter.setPen(QColor(255, 0, 0))
            painter.drawText(text_x, text_y + text_height + 30,
                           f"OVERFLOW: +{overflow}px")


class LayoutSimulatorDialog(QDialog):
    """Dialog for simulating text layout with different fonts and constraints."""
    
    def __init__(self, parent=None, source_text: str = "", target_text: str = ""):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Layout Simulator"))
        self.setModal(True)
        self.resize(900, 700)
        
        self._source_text = source_text
        self._target_text = target_text
        
        self._setup_ui()
        self._update_rendering()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Font settings
        font_group = QGroupBox(self.tr("Font Settings"))
        font_layout = QFormLayout(font_group)
        
        self._font_combo = QComboBox()
        self._font_combo.addItems([
            "Arial", "Helvetica", "Times New Roman", "Courier New",
            "Verdana", "Georgia", "Roboto", "SF Pro Display",
            "System Font"
        ])
        self._font_combo.currentTextChanged.connect(self._update_rendering)
        font_layout.addRow(self.tr("Font Family:"), self._font_combo)
        
        self._size_spin = QSpinBox()
        self._size_spin.setRange(6, 72)
        self._size_spin.setValue(12)
        self._size_spin.valueChanged.connect(self._update_rendering)
        font_layout.addRow(self.tr("Size (pt):"), self._size_spin)
        
        self._bold_check = QCheckBox(self.tr("Bold"))
        self._bold_check.toggled.connect(self._update_rendering)
        font_layout.addRow(self._bold_check)
        
        layout.addWidget(font_group)
        
        # Width constraints
        width_group = QGroupBox(self.tr("Width Constraints"))
        width_layout = QFormLayout(width_group)
        
        self._width_spin = QSpinBox()
        self._width_spin.setRange(50, 1000)
        self._width_spin.setValue(200)
        self._width_spin.setSuffix(" px")
        self._width_spin.valueChanged.connect(self._update_rendering)
        width_layout.addRow(self.tr("Max Width:"), self._width_spin)
        
        # Quick presets
        preset_layout = QHBoxLayout()
        presets = [
            (self.tr("Mobile Button"), 120),
            (self.tr("Dialog Button"), 200),
            (self.tr("Menu Item"), 300),
            (self.tr("Tablet"), 400)
        ]
        
        for name, width in presets:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, w=width: self._set_width_preset(w))
            preset_layout.addWidget(btn)
            
        width_layout.addRow(self.tr("Presets:"), preset_layout)
        
        self._overflow_check = QCheckBox(self.tr("Highlight Overflow"))
        self._overflow_check.setChecked(True)
        self._overflow_check.toggled.connect(self._update_rendering)
        width_layout.addRow(self._overflow_check)
        
        layout.addWidget(width_group)
        
        # Text comparison
        comparison_group = QGroupBox(self.tr("Text Comparison"))
        comparison_layout = QVBoxLayout(comparison_group)
        
        # Source text
        source_layout = QVBoxLayout()
        source_layout.addWidget(QLabel(self.tr("Source Text:")))
        
        self._source_edit = QTextEdit()
        self._source_edit.setPlainText(self._source_text)
        self._source_edit.setMaximumHeight(60)
        self._source_edit.textChanged.connect(self._update_rendering)
        source_layout.addWidget(self._source_edit)
        
        self._source_render = TextRenderWidget()
        source_layout.addWidget(self._source_render)
        
        comparison_layout.addLayout(source_layout)
        
        # Target text
        target_layout = QVBoxLayout()
        target_layout.addWidget(QLabel(self.tr("Translation Text:")))
        
        self._target_edit = QTextEdit()
        self._target_edit.setPlainText(self._target_text)
        self._target_edit.setMaximumHeight(60)
        self._target_edit.textChanged.connect(self._update_rendering)
        target_layout.addWidget(self._target_edit)
        
        self._target_render = TextRenderWidget()
        target_layout.addWidget(self._target_render)
        
        comparison_layout.addLayout(target_layout)
        
        layout.addWidget(comparison_group)
        
        # Width comparison
        self._comparison_label = QLabel()
        self._comparison_label.setStyleSheet("font-weight: bold; padding: 10px;")
        layout.addWidget(self._comparison_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton(self.tr("Close"))
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _set_width_preset(self, width: int):
        self._width_spin.setValue(width)
    
    def _update_rendering(self):
        """Update the text rendering with current settings."""
        # Create font
        font = QFont()
        font_family = self._font_combo.currentText()
        if font_family == "System Font":
            font = QFont()  # Use system default
        else:
            font.setFamily(font_family)
        
        font.setPointSize(self._size_spin.value())
        font.setBold(self._bold_check.isChecked())
        
        max_width = self._width_spin.value()
        show_overflow = self._overflow_check.isChecked()
        
        # Update source rendering
        source_text = self._source_edit.toPlainText().replace('\n', ' ')
        self._source_render.set_text(source_text)
        self._source_render.set_font_settings(font)
        self._source_render.set_max_width(max_width)
        self._source_render.set_show_overflow(show_overflow)
        
        # Update target rendering
        target_text = self._target_edit.toPlainText().replace('\n', ' ')
        self._target_render.set_text(target_text)
        self._target_render.set_font_settings(font)
        self._target_render.set_max_width(max_width)
        self._target_render.set_show_overflow(show_overflow)
        
        # Calculate and show comparison
        metrics = QFontMetrics(font)
        source_width = metrics.horizontalAdvance(source_text)
        target_width = metrics.horizontalAdvance(target_text)
        
        width_diff = target_width - source_width
        width_ratio = (target_width / source_width * 100) if source_width > 0 else 100
        
        comparison_text = self.tr("Source: {0}px | Translation: {1}px | Difference: {2}px ({3:.1f}%)").format(
            source_width, target_width, width_diff, width_ratio
        )
        
        # Color code the comparison
        if abs(width_diff) <= 10:
            color = "green"
        elif abs(width_diff) <= 30:
            color = "orange"
        else:
            color = "red"
            
        self._comparison_label.setText(comparison_text)
        self._comparison_label.setStyleSheet(f"color: {color}; font-weight: bold; padding: 10px;")