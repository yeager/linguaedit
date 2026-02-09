"""Statistics Dialog for LinguaEdit."""

from __future__ import annotations

from typing import List, Dict, Tuple
from dataclasses import dataclass

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QProgressBar, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialogButtonBox, QFrame, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


@dataclass 
class TranslationStats:
    """Translation statistics data."""
    total_entries: int = 0
    translated_entries: int = 0
    untranslated_entries: int = 0
    fuzzy_entries: int = 0
    
    source_words: int = 0
    source_chars: int = 0
    translation_words: int = 0
    translation_chars: int = 0
    
    longest_entries: List[Tuple[int, str, int]] = None  # (index, text, length)
    
    def __post_init__(self):
        if self.longest_entries is None:
            self.longest_entries = []
    
    @property
    def translated_percentage(self) -> float:
        if self.total_entries == 0:
            return 0.0
        return (self.translated_entries / self.total_entries) * 100.0
        
    @property
    def untranslated_percentage(self) -> float:
        if self.total_entries == 0:
            return 0.0
        return (self.untranslated_entries / self.total_entries) * 100.0
        
    @property
    def fuzzy_percentage(self) -> float:
        if self.total_entries == 0:
            return 0.0
        return (self.fuzzy_entries / self.total_entries) * 100.0
        
    @property
    def expansion_ratio(self) -> float:
        """Calculate text expansion ratio (translation vs source)."""
        if self.source_chars == 0:
            return 0.0
        return self.translation_chars / self.source_chars


def calculate_statistics(entries: List[Dict]) -> TranslationStats:
    """Calculate comprehensive statistics from entries."""
    stats = TranslationStats()
    
    # Basic counts
    stats.total_entries = len(entries)
    
    # For finding longest entries
    entries_with_length = []
    
    for i, entry in enumerate(entries):
        msgid = entry.get("msgid", "")
        msgstr = entry.get("msgstr", "")
        is_fuzzy = entry.get("is_fuzzy", False)
        
        # Count by status
        if msgstr:
            if is_fuzzy:
                stats.fuzzy_entries += 1
            else:
                stats.translated_entries += 1
        else:
            stats.untranslated_entries += 1
            
        # Count words and characters
        if msgid:
            stats.source_words += len(msgid.split())
            stats.source_chars += len(msgid)
            
        if msgstr:
            stats.translation_words += len(msgstr.split())
            stats.translation_chars += len(msgstr)
            
        # Track length for longest entries
        if msgid:
            entries_with_length.append((i, msgid, len(msgid)))
            
    # Find top 5 longest entries
    entries_with_length.sort(key=lambda x: x[2], reverse=True)
    stats.longest_entries = entries_with_length[:5]
    
    return stats


class StatisticsDialog(QDialog):
    """Comprehensive translation statistics dialog."""
    
    def __init__(self, parent=None, entries: List[Dict] = None, file_name: str = ""):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Translation Statistics"))
        self.setMinimumSize(600, 500)
        
        self._entries = entries or []
        self._file_name = file_name
        self._stats = calculate_statistics(self._entries)
        
        self._build_ui()
        self._populate_data()
        
    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        # File info
        if self._file_name:
            file_label = QLabel(f"<h3>{self.tr('File:')} {self._file_name}</h3>")
            layout.addWidget(file_label)
            
        # Overview section
        overview_group = QGroupBox(self.tr("Overview"))
        overview_layout = QVBoxLayout(overview_group)
        
        # Translation progress
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel(self.tr("Translation Progress:")))
        
        self._progress_bar = QProgressBar()
        self._progress_bar.setTextVisible(True)
        progress_layout.addWidget(self._progress_bar, 1)
        
        overview_layout.addLayout(progress_layout)
        
        # Statistics grid
        stats_grid = QGridLayout()
        
        # Create statistics labels
        self._total_label = QLabel()
        self._translated_label = QLabel()
        self._untranslated_label = QLabel() 
        self._fuzzy_label = QLabel()
        
        stats_grid.addWidget(QLabel(self.tr("Total entries:")), 0, 0)
        stats_grid.addWidget(self._total_label, 0, 1)
        
        stats_grid.addWidget(QLabel(self.tr("Translated:")), 1, 0)
        stats_grid.addWidget(self._translated_label, 1, 1)
        
        stats_grid.addWidget(QLabel(self.tr("Untranslated:")), 2, 0)
        stats_grid.addWidget(self._untranslated_label, 2, 1)
        
        stats_grid.addWidget(QLabel(self.tr("Fuzzy/Needs work:")), 3, 0)
        stats_grid.addWidget(self._fuzzy_label, 3, 1)
        
        overview_layout.addLayout(stats_grid)
        layout.addWidget(overview_group)
        
        # Word/Character statistics
        text_stats_group = QGroupBox(self.tr("Text Statistics"))
        text_layout = QGridLayout(text_stats_group)
        
        self._source_words_label = QLabel()
        self._source_chars_label = QLabel()
        self._translation_words_label = QLabel()
        self._translation_chars_label = QLabel()
        self._expansion_ratio_label = QLabel()
        
        text_layout.addWidget(QLabel(self.tr("Source text:")), 0, 0)
        text_layout.addWidget(QLabel(self.tr("Translation:")), 0, 1)
        
        text_layout.addWidget(QLabel(self.tr("Words:")), 1, 0)
        text_layout.addWidget(self._source_words_label, 1, 1)
        text_layout.addWidget(self._translation_words_label, 1, 2)
        
        text_layout.addWidget(QLabel(self.tr("Characters:")), 2, 0)
        text_layout.addWidget(self._source_chars_label, 2, 1)
        text_layout.addWidget(self._translation_chars_label, 2, 2)
        
        text_layout.addWidget(QLabel(self.tr("Expansion ratio:")), 3, 0)
        text_layout.addWidget(self._expansion_ratio_label, 3, 1, 1, 2)
        
        layout.addWidget(text_stats_group)
        
        # Longest strings
        longest_group = QGroupBox(self.tr("Longest Source Strings"))
        longest_layout = QVBoxLayout(longest_group)
        
        self._longest_table = QTableWidget()
        self._longest_table.setColumnCount(3)
        self._longest_table.setHorizontalHeaderLabels([
            self.tr("Entry #"), self.tr("Length"), self.tr("Text Preview")
        ])
        
        # Table settings
        self._longest_table.setAlternatingRowColors(True)
        self._longest_table.setSelectionBehavior(QTableWidget.SelectRows)
        self._longest_table.verticalHeader().setVisible(False)
        self._longest_table.setMaximumHeight(150)
        
        # Header settings
        header = self._longest_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents) 
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        longest_layout.addWidget(self._longest_table)
        layout.addWidget(longest_group)
        
        # Additional info section (expandable)
        details_group = QGroupBox(self.tr("Additional Details"))
        details_layout = QVBoxLayout(details_group)
        
        self._details_text = QTextEdit()
        self._details_text.setMaximumHeight(100)
        self._details_text.setReadOnly(True)
        details_layout.addWidget(self._details_text)
        
        layout.addWidget(details_group)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Buttons
        self._button_box = QDialogButtonBox(QDialogButtonBox.Close)
        self._button_box.rejected.connect(self.reject)
        layout.addWidget(self._button_box)
        
    def _populate_data(self):
        """Populate the dialog with calculated statistics."""
        stats = self._stats
        
        # Progress bar
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(int(stats.translated_percentage))
        self._progress_bar.setFormat(f"{stats.translated_percentage:.1f}% {self.tr('translated')}")
        
        # Basic statistics
        self._total_label.setText(f"{stats.total_entries:,}")
        self._translated_label.setText(f"{stats.translated_entries:,} ({stats.translated_percentage:.1f}%)")
        self._untranslated_label.setText(f"{stats.untranslated_entries:,} ({stats.untranslated_percentage:.1f}%)")
        self._fuzzy_label.setText(f"{stats.fuzzy_entries:,} ({stats.fuzzy_percentage:.1f}%)")
        
        # Text statistics
        self._source_words_label.setText(f"{stats.source_words:,}")
        self._source_chars_label.setText(f"{stats.source_chars:,}")
        self._translation_words_label.setText(f"{stats.translation_words:,}")
        self._translation_chars_label.setText(f"{stats.translation_chars:,}")
        
        # Expansion ratio
        expansion = stats.expansion_ratio
        if expansion > 1.0:
            expansion_text = f"{expansion:.2f}x {self.tr('(text expanded)')}"
        elif expansion < 1.0 and expansion > 0:
            expansion_text = f"{expansion:.2f}x {self.tr('(text contracted)')}"
        else:
            expansion_text = self.tr("N/A")
        self._expansion_ratio_label.setText(expansion_text)
        
        # Longest strings table
        self._longest_table.setRowCount(len(stats.longest_entries))
        
        for row, (entry_idx, text, length) in enumerate(stats.longest_entries):
            # Entry number (1-based)
            self._longest_table.setItem(row, 0, QTableWidgetItem(str(entry_idx + 1)))
            
            # Length
            length_item = QTableWidgetItem(f"{length:,}")
            length_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._longest_table.setItem(row, 1, length_item)
            
            # Text preview (first 100 chars)
            preview = text[:100].replace('\n', '\\n').replace('\t', '\\t')
            if len(text) > 100:
                preview += "..."
            self._longest_table.setItem(row, 2, QTableWidgetItem(preview))
            
        # Additional details
        details = []
        
        if stats.total_entries > 0:
            avg_src_length = stats.source_chars / stats.total_entries
            #: Average source length label
            lbl = self.tr("Average source length")
            #: characters unit
            chars = self.tr("characters")
            details.append(f"{lbl}: {avg_src_length:.1f} {chars}")

        if stats.translated_entries > 0:
            avg_trans_length = stats.translation_chars / stats.translated_entries
            #: Average translation length label
            lbl2 = self.tr("Average translation length")
            details.append(f"{lbl2}: {avg_trans_length:.1f} {chars}")

        if stats.source_words > 0:
            words_per_entry = stats.source_words / stats.total_entries
            #: Average words per entry label
            lbl3 = self.tr("Average words per entry")
            details.append(f"{lbl3}: {words_per_entry:.1f}")

        # Translation density
        if stats.total_entries > 0:
            completion = (stats.translated_entries + stats.fuzzy_entries) / stats.total_entries * 100
            #: Translation completion label
            lbl4 = self.tr("Translation completion")
            details.append(f"{lbl4}: {completion:.1f}%")
            
        if details:
            self._details_text.setPlainText('\n'.join(details))
        else:
            self._details_text.setPlainText(self.tr("No additional details available."))
            
    def get_statistics(self) -> TranslationStats:
        """Get the calculated statistics."""
        return self._stats