"""Search and Replace Dialog for LinguaEdit."""

from __future__ import annotations

import re
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QCheckBox, QPushButton, QLabel, QComboBox,
    QTextEdit, QFrame, QProgressBar, QDialogButtonBox,
    QGroupBox, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QKeySequence, QShortcut


class SearchReplaceDialog(QDialog):
    """Advanced search and replace dialog."""
    
    # Signal emitted when highlighting should be updated
    highlight_requested = Signal(str, bool, bool, str)  # pattern, case_sensitive, regex, scope
    
    # Signal emitted when replace operation is requested
    replace_requested = Signal(str, str, bool, bool, str, bool)  # find, replace, case_sensitive, regex, scope, replace_all
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Find & Replace"))
        self.setMinimumSize(500, 350)
        
        # Track search results
        self._current_match = 0
        self._total_matches = 0
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._perform_search)
        
        self._build_ui()
        self._setup_connections()
        self._setup_shortcuts()
        
    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        # Search fields
        search_group = QGroupBox(self.tr("Search"))
        search_layout = QGridLayout(search_group)
        
        # Find field
        search_layout.addWidget(QLabel(self.tr("Find:")), 0, 0)
        self._find_entry = QLineEdit()
        self._find_entry.setPlaceholderText(self.tr("Enter search text..."))
        search_layout.addWidget(self._find_entry, 0, 1)
        
        # Replace field  
        search_layout.addWidget(QLabel(self.tr("Replace:")), 1, 0)
        self._replace_entry = QLineEdit()
        self._replace_entry.setPlaceholderText(self.tr("Enter replacement text..."))
        search_layout.addWidget(self._replace_entry, 1, 1)
        
        layout.addWidget(search_group)
        
        # Options
        options_group = QGroupBox(self.tr("Options"))
        options_layout = QVBoxLayout(options_group)
        
        # Checkboxes row 1
        cb_row1 = QHBoxLayout()
        self._case_sensitive_cb = QCheckBox(self.tr("Case sensitive"))
        self._whole_words_cb = QCheckBox(self.tr("Whole words"))
        self._regex_cb = QCheckBox(self.tr("Regular expression"))
        cb_row1.addWidget(self._case_sensitive_cb)
        cb_row1.addWidget(self._whole_words_cb) 
        cb_row1.addWidget(self._regex_cb)
        cb_row1.addStretch()
        options_layout.addLayout(cb_row1)
        
        # Search scope
        scope_layout = QHBoxLayout()
        scope_layout.addWidget(QLabel(self.tr("Search in:")))
        
        self._scope_group = QButtonGroup(self)
        self._scope_source = QRadioButton(self.tr("Source text"))
        self._scope_translation = QRadioButton(self.tr("Translation"))
        self._scope_both = QRadioButton(self.tr("Both"))
        self._scope_both.setChecked(True)  # Default
        
        self._scope_group.addButton(self._scope_source, 0)
        self._scope_group.addButton(self._scope_translation, 1) 
        self._scope_group.addButton(self._scope_both, 2)
        
        scope_layout.addWidget(self._scope_source)
        scope_layout.addWidget(self._scope_translation)
        scope_layout.addWidget(self._scope_both)
        scope_layout.addStretch()
        options_layout.addLayout(scope_layout)
        
        layout.addWidget(options_group)
        
        # Results info
        self._results_label = QLabel()
        self._results_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self._results_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Find buttons
        self._find_next_btn = QPushButton(self.tr("Find Next"))
        self._find_prev_btn = QPushButton(self.tr("Find Previous"))
        self._find_all_btn = QPushButton(self.tr("Find All"))
        
        button_layout.addWidget(self._find_next_btn)
        button_layout.addWidget(self._find_prev_btn)
        button_layout.addWidget(self._find_all_btn)
        
        button_layout.addWidget(self._create_separator())
        
        # Replace buttons
        self._replace_btn = QPushButton(self.tr("Replace"))
        self._replace_all_btn = QPushButton(self.tr("Replace All"))
        
        button_layout.addWidget(self._replace_btn)
        button_layout.addWidget(self._replace_all_btn)
        
        button_layout.addStretch()
        
        # Close button
        close_btn = QPushButton(self.tr("Close"))
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Progress bar (hidden by default)
        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        layout.addWidget(self._progress_bar)
        
    def _create_separator(self) -> QFrame:
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        return separator
        
    def _setup_connections(self):
        # Search text changes
        self._find_entry.textChanged.connect(self._on_search_text_changed)
        
        # Options changes
        self._case_sensitive_cb.toggled.connect(self._on_options_changed)
        self._whole_words_cb.toggled.connect(self._on_options_changed)
        self._regex_cb.toggled.connect(self._on_options_changed)
        self._scope_group.buttonToggled.connect(self._on_options_changed)
        
        # Buttons
        self._find_next_btn.clicked.connect(self._find_next)
        self._find_prev_btn.clicked.connect(self._find_previous)
        self._find_all_btn.clicked.connect(self._find_all)
        self._replace_btn.clicked.connect(self._replace_current)
        self._replace_all_btn.clicked.connect(self._replace_all)
        
    def _setup_shortcuts(self):
        # Find shortcuts
        QShortcut(QKeySequence.FindNext, self, self._find_next)
        QShortcut(QKeySequence.FindPrevious, self, self._find_previous)
        QShortcut(QKeySequence("F3"), self, self._find_next)
        QShortcut(QKeySequence("Shift+F3"), self, self._find_previous)
        
        # Replace shortcuts  
        QShortcut(QKeySequence("Ctrl+R"), self, self._replace_current)
        QShortcut(QKeySequence("Ctrl+Alt+R"), self, self._replace_all)
        
    def _on_search_text_changed(self):
        """Start search timer when text changes."""
        self._search_timer.start(300)  # Debounce
        
    def _on_options_changed(self):
        """Options changed, refresh search."""
        if self._find_entry.text():
            self._search_timer.start(100)
            
    def _perform_search(self):
        """Perform the actual search and emit highlight signal."""
        search_text = self._find_entry.text()
        if not search_text:
            self._results_label.setText("")
            return
            
        case_sensitive = self._case_sensitive_cb.isChecked()
        is_regex = self._regex_cb.isChecked()
        scope = self._get_scope()
        
        # Emit signal for parent to handle highlighting
        self.highlight_requested.emit(search_text, case_sensitive, is_regex, scope)
        
    def _get_scope(self) -> str:
        """Get current search scope."""
        scope_id = self._scope_group.checkedId()
        if scope_id == 0:
            return "source"
        elif scope_id == 1:
            return "translation"
        else:
            return "both"
            
    def _find_next(self):
        """Find next occurrence."""
        search_text = self._find_entry.text()
        if not search_text:
            return
            
        # For now, just emit the search signal
        # The parent window should handle actual navigation
        self._perform_search()
        
    def _find_previous(self):
        """Find previous occurrence."""
        search_text = self._find_entry.text()
        if not search_text:
            return
            
        # Similar to find_next, parent handles navigation
        self._perform_search()
        
    def _find_all(self):
        """Find all occurrences."""
        search_text = self._find_entry.text()
        if not search_text:
            return
            
        # Show all matches - parent window should handle this
        self._perform_search()
        
    def _replace_current(self):
        """Replace current selection."""
        search_text = self._find_entry.text()
        replace_text = self._replace_entry.text()
        
        if not search_text:
            return
            
        case_sensitive = self._case_sensitive_cb.isChecked()
        is_regex = self._regex_cb.isChecked()
        scope = self._get_scope()
        
        self.replace_requested.emit(search_text, replace_text, case_sensitive, is_regex, scope, False)
        
    def _replace_all(self):
        """Replace all occurrences."""
        search_text = self._find_entry.text()
        replace_text = self._replace_entry.text()
        
        if not search_text:
            return
            
        case_sensitive = self._case_sensitive_cb.isChecked()
        is_regex = self._regex_cb.isChecked()
        scope = self._get_scope()
        
        self.replace_requested.emit(search_text, replace_text, case_sensitive, is_regex, scope, True)
        
    def set_search_text(self, text: str):
        """Set the search field text."""
        self._find_entry.setText(text)
        self._find_entry.selectAll()
        
    def set_match_count(self, current: int, total: int):
        """Update match count display."""
        self._current_match = current
        self._total_matches = total
        
        if total > 0:
            self._results_label.setText(self.tr("%d of %d matches") % (current, total))
        elif self._find_entry.text():
            self._results_label.setText(self.tr("No matches found"))
        else:
            self._results_label.setText("")
            
    def show_progress(self, value: int, maximum: int):
        """Show progress during replace operations."""
        if maximum > 0:
            self._progress_bar.setVisible(True)
            self._progress_bar.setRange(0, maximum)
            self._progress_bar.setValue(value)
        else:
            self._progress_bar.setVisible(False)
            
    def focus_find_field(self):
        """Focus the find field and select all text."""
        self._find_entry.setFocus()
        self._find_entry.selectAll()