"""File Header Editor Dialog for LinguaEdit."""

from __future__ import annotations

from typing import Dict, Optional, Any
from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit,
    QGroupBox, QDialogButtonBox, QTabWidget, QWidget,
    QMessageBox, QDateTimeEdit, QCheckBox, QSpinBox
)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QFont


class HeaderDialog(QDialog):
    """Dialog for editing translation file headers and metadata."""
    
    def __init__(self, parent=None, file_type: str = "po", file_data=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Edit File Header"))
        self.setMinimumSize(600, 500)
        
        self._file_type = file_type.lower()
        self._file_data = file_data
        self._original_data = {}
        
        self._build_ui()
        self._load_current_data()
        
    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        # Create tab widget for different file types
        self._tab_widget = QTabWidget()
        
        if self._file_type == "po":
            self._build_po_tab()
        elif self._file_type == "ts":
            self._build_ts_tab()
        elif self._file_type in ("xliff", "xlf"):
            self._build_xliff_tab()
        else:
            # Generic metadata tab for other formats
            self._build_generic_tab()
            
        layout.addWidget(self._tab_widget)
        
        # Buttons
        self._button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.RestoreDefaults
        )
        
        # Connect buttons
        self._button_box.accepted.connect(self._save_changes)
        self._button_box.rejected.connect(self.reject)
        self._button_box.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self._restore_defaults)
        
        layout.addWidget(self._button_box)
        
    def _build_po_tab(self):
        """Build PO file headers tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Project Information group
        project_group = QGroupBox(self.tr("Project Information"))
        project_layout = QFormLayout(project_group)
        
        self._po_project_id = QLineEdit()
        project_layout.addRow(self.tr("Project-Id-Version:"), self._po_project_id)
        
        self._po_package = QLineEdit()
        project_layout.addRow(self.tr("Package:"), self._po_package)
        
        self._po_bugs_address = QLineEdit()
        self._po_bugs_address.setPlaceholderText("email@example.com")
        project_layout.addRow(self.tr("Report-Msgid-Bugs-To:"), self._po_bugs_address)
        
        layout.addWidget(project_group)
        
        # Translation Information group
        translation_group = QGroupBox(self.tr("Translation Information"))
        translation_layout = QFormLayout(translation_group)
        
        self._po_translator = QLineEdit()
        self._po_translator.setPlaceholderText("Name <email@example.com>")
        translation_layout.addRow(self.tr("Last-Translator:"), self._po_translator)
        
        self._po_team = QLineEdit()
        self._po_team.setPlaceholderText("Language Team <team@example.com>")
        translation_layout.addRow(self.tr("Language-Team:"), self._po_team)
        
        self._po_language = QComboBox()
        self._po_language.setEditable(True)
        self._populate_language_combo(self._po_language)
        translation_layout.addRow(self.tr("Language:"), self._po_language)
        
        layout.addWidget(translation_group)
        
        # Technical Information group
        technical_group = QGroupBox(self.tr("Technical Information"))
        technical_layout = QFormLayout(technical_group)
        
        self._po_pot_date = QDateTimeEdit()
        self._po_pot_date.setCalendarPopup(True)
        self._po_pot_date.setDisplayFormat("yyyy-MM-dd hh:mm")
        technical_layout.addRow(self.tr("POT-Creation-Date:"), self._po_pot_date)
        
        self._po_revision_date = QDateTimeEdit()
        self._po_revision_date.setCalendarPopup(True) 
        self._po_revision_date.setDisplayFormat("yyyy-MM-dd hh:mm")
        technical_layout.addRow(self.tr("PO-Revision-Date:"), self._po_revision_date)
        
        self._po_charset = QComboBox()
        self._po_charset.addItems(["UTF-8", "ISO-8859-1", "ISO-8859-15"])
        technical_layout.addRow(self.tr("Charset:"), self._po_charset)
        
        self._po_encoding = QComboBox()
        self._po_encoding.addItems(["8bit", "7bit", "quoted-printable", "base64"])
        technical_layout.addRow(self.tr("Content-Transfer-Encoding:"), self._po_encoding)
        
        layout.addWidget(technical_group)
        
        # Plural Forms
        plural_group = QGroupBox(self.tr("Plural Forms"))
        plural_layout = QVBoxLayout(plural_group)
        
        plural_info = QLabel(self.tr("Define how plural forms work for this language."))
        plural_info.setWordWrap(True)
        plural_layout.addWidget(plural_info)
        
        self._po_plural_forms = QLineEdit()
        self._po_plural_forms.setPlaceholderText("nplurals=2; plural=(n != 1);")
        plural_layout.addWidget(self._po_plural_forms)
        
        # Add some common plural forms buttons
        common_layout = QHBoxLayout()
        
        english_btn = QPushButton(self.tr("English (2 forms)"))
        english_btn.clicked.connect(lambda: self._po_plural_forms.setText("nplurals=2; plural=(n != 1);"))
        common_layout.addWidget(english_btn)
        
        germanic_btn = QPushButton(self.tr("Germanic (2 forms)"))
        germanic_btn.clicked.connect(lambda: self._po_plural_forms.setText("nplurals=2; plural=(n != 1);"))
        common_layout.addWidget(germanic_btn)
        
        romance_btn = QPushButton(self.tr("Romance (2 forms)"))  
        romance_btn.clicked.connect(lambda: self._po_plural_forms.setText("nplurals=2; plural=(n > 1);"))
        common_layout.addWidget(romance_btn)
        
        plural_layout.addLayout(common_layout)
        layout.addWidget(plural_group)
        
        layout.addStretch()
        self._tab_widget.addTab(tab, self.tr("PO Headers"))
        
    def _build_ts_tab(self):
        """Build TS file headers tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # TS File attributes
        ts_group = QGroupBox(self.tr("TS File Attributes"))
        ts_layout = QFormLayout(ts_group)
        
        self._ts_language = QComboBox()
        self._ts_language.setEditable(True)
        self._populate_language_combo(self._ts_language)
        ts_layout.addRow(self.tr("Target Language:"), self._ts_language)
        
        self._ts_source_language = QComboBox()
        self._ts_source_language.setEditable(True)
        self._populate_language_combo(self._ts_source_language)
        ts_layout.addRow(self.tr("Source Language:"), self._ts_source_language)
        
        self._ts_version = QLineEdit()
        self._ts_version.setPlaceholderText("2.1")
        ts_layout.addRow(self.tr("TS Version:"), self._ts_version)
        
        layout.addWidget(ts_group)
        
        # Additional metadata
        metadata_group = QGroupBox(self.tr("Additional Metadata"))
        metadata_layout = QFormLayout(metadata_group)
        
        self._ts_translator = QLineEdit()
        metadata_layout.addRow(self.tr("Translator:"), self._ts_translator)
        
        self._ts_comment = QTextEdit()
        self._ts_comment.setMaximumHeight(80)
        metadata_layout.addRow(self.tr("Comment:"), self._ts_comment)
        
        layout.addWidget(metadata_group)
        layout.addStretch()
        
        self._tab_widget.addTab(tab, self.tr("TS Attributes"))
        
    def _build_xliff_tab(self):
        """Build XLIFF file headers tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # XLIFF file attributes
        xliff_group = QGroupBox(self.tr("XLIFF File Attributes"))
        xliff_layout = QFormLayout(xliff_group)
        
        self._xliff_source_lang = QComboBox()
        self._xliff_source_lang.setEditable(True)
        self._populate_language_combo(self._xliff_source_lang)
        xliff_layout.addRow(self.tr("Source Language:"), self._xliff_source_lang)
        
        self._xliff_target_lang = QComboBox()
        self._xliff_target_lang.setEditable(True)
        self._populate_language_combo(self._xliff_target_lang)
        xliff_layout.addRow(self.tr("Target Language:"), self._xliff_target_lang)
        
        self._xliff_version = QComboBox()
        self._xliff_version.addItems(["1.2", "2.0", "2.1"])
        xliff_layout.addRow(self.tr("XLIFF Version:"), self._xliff_version)
        
        self._xliff_original = QLineEdit()
        xliff_layout.addRow(self.tr("Original File:"), self._xliff_original)
        
        self._xliff_datatype = QComboBox()
        self._xliff_datatype.addItems([
            "plaintext", "html", "xml", "winres", "po", 
            "properties", "java", "csharp", "javascript"
        ])
        xliff_layout.addRow(self.tr("Data Type:"), self._xliff_datatype)
        
        layout.addWidget(xliff_group)
        
        # Tool information
        tool_group = QGroupBox(self.tr("Tool Information"))
        tool_layout = QFormLayout(tool_group)
        
        self._xliff_tool_id = QLineEdit()
        self._xliff_tool_id.setText("LinguaEdit")
        tool_layout.addRow(self.tr("Tool ID:"), self._xliff_tool_id)
        
        self._xliff_tool_name = QLineEdit()
        self._xliff_tool_name.setText("LinguaEdit")
        tool_layout.addRow(self.tr("Tool Name:"), self._xliff_tool_name)
        
        self._xliff_tool_version = QLineEdit()
        tool_layout.addRow(self.tr("Tool Version:"), self._xliff_tool_version)
        
        layout.addWidget(tool_group)
        layout.addStretch()
        
        self._tab_widget.addTab(tab, self.tr("XLIFF Attributes"))
        
    def _build_generic_tab(self):
        """Build generic metadata tab for other file formats."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Generic metadata
        metadata_group = QGroupBox(self.tr("File Metadata"))
        metadata_layout = QFormLayout(metadata_group)
        
        self._generic_name = QLineEdit()
        metadata_layout.addRow(self.tr("Project Name:"), self._generic_name)
        
        self._generic_version = QLineEdit()
        metadata_layout.addRow(self.tr("Version:"), self._generic_version)
        
        self._generic_description = QTextEdit()
        self._generic_description.setMaximumHeight(100)
        metadata_layout.addRow(self.tr("Description:"), self._generic_description)
        
        layout.addWidget(metadata_group)
        layout.addStretch()
        
        self._tab_widget.addTab(tab, self.tr("Metadata"))
        
    def _populate_language_combo(self, combo: QComboBox):
        """Populate language combobox with common languages."""
        languages = [
            ("en", "English"),
            ("sv", "Svenska"),
            ("de", "Deutsch"),
            ("fr", "Français"),
            ("es", "Español"), 
            ("pt", "Português"),
            ("pt_BR", "Português (Brasil)"),
            ("it", "Italiano"),
            ("nl", "Nederlands"),
            ("da", "Dansk"),
            ("nb", "Norsk bokmål"),
            ("fi", "Suomi"),
            ("pl", "Polski"),
            ("ru", "Русский"),
            ("ja", "日本語"),
            ("zh_CN", "中文 (简体)"),
            ("ko", "한국어"),
            ("ar", "العربية"),
        ]
        
        for code, name in languages:
            combo.addItem(f"{name} ({code})", code)
            
    def _load_current_data(self):
        """Load current file data into the form fields."""
        if not self._file_data:
            self._set_defaults()
            return
            
        if self._file_type == "po":
            self._load_po_data()
        elif self._file_type == "ts":
            self._load_ts_data()
        elif self._file_type in ("xliff", "xlf"):
            self._load_xliff_data()
        else:
            self._load_generic_data()
            
    def _load_po_data(self):
        """Load PO file metadata."""
        if not hasattr(self._file_data, 'metadata'):
            self._set_defaults()
            return
            
        metadata = self._file_data.metadata
        
        # Store original data for comparison
        self._original_data = metadata.copy()
        
        # Project information
        self._po_project_id.setText(metadata.get("Project-Id-Version", ""))
        self._po_bugs_address.setText(metadata.get("Report-Msgid-Bugs-To", ""))
        
        # Translation information
        self._po_translator.setText(metadata.get("Last-Translator", ""))
        self._po_team.setText(metadata.get("Language-Team", ""))
        
        language = metadata.get("Language", "")
        index = self._po_language.findData(language)
        if index >= 0:
            self._po_language.setCurrentIndex(index)
        else:
            self._po_language.setEditText(language)
            
        # Technical information
        pot_date = metadata.get("POT-Creation-Date", "")
        if pot_date:
            try:
                dt = QDateTime.fromString(pot_date, "yyyy-MM-dd hh:mm")
                if dt.isValid():
                    self._po_pot_date.setDateTime(dt)
            except:
                pass
                
        revision_date = metadata.get("PO-Revision-Date", "")
        if revision_date:
            try:
                dt = QDateTime.fromString(revision_date, "yyyy-MM-dd hh:mm")
                if dt.isValid():
                    self._po_revision_date.setDateTime(dt)
            except:
                pass
                
        # Content-Type parsing
        content_type = metadata.get("Content-Type", "")
        if "charset=" in content_type:
            charset = content_type.split("charset=")[1].strip()
            index = self._po_charset.findText(charset)
            if index >= 0:
                self._po_charset.setCurrentIndex(index)
                
        encoding = metadata.get("Content-Transfer-Encoding", "8bit")
        index = self._po_encoding.findText(encoding)
        if index >= 0:
            self._po_encoding.setCurrentIndex(index)
            
        # Plural forms
        self._po_plural_forms.setText(metadata.get("Plural-Forms", ""))
        
    def _load_ts_data(self):
        """Load TS file metadata."""
        # TS files store language information differently
        if hasattr(self._file_data, 'language'):
            language = self._file_data.language
            index = self._ts_language.findData(language)
            if index >= 0:
                self._ts_language.setCurrentIndex(index)
            else:
                self._ts_language.setEditText(language)
                
        if hasattr(self._file_data, 'source_language'):
            source_lang = self._file_data.source_language
            index = self._ts_source_language.findData(source_lang)
            if index >= 0:
                self._ts_source_language.setCurrentIndex(index)
            else:
                self._ts_source_language.setEditText(source_lang)
                
        if hasattr(self._file_data, 'version'):
            self._ts_version.setText(str(self._file_data.version))
            
    def _load_xliff_data(self):
        """Load XLIFF file metadata."""
        if hasattr(self._file_data, 'source_language'):
            source_lang = self._file_data.source_language
            index = self._xliff_source_lang.findData(source_lang)
            if index >= 0:
                self._xliff_source_lang.setCurrentIndex(index)
            else:
                self._xliff_source_lang.setEditText(source_lang)
                
        if hasattr(self._file_data, 'target_language'):
            target_lang = self._file_data.target_language
            index = self._xliff_target_lang.findData(target_lang)
            if index >= 0:
                self._xliff_target_lang.setCurrentIndex(index)
            else:
                self._xliff_target_lang.setEditText(target_lang)
                
        if hasattr(self._file_data, 'version'):
            self._xliff_version.setCurrentText(str(self._file_data.version))
            
        if hasattr(self._file_data, 'original'):
            self._xliff_original.setText(self._file_data.original)
            
    def _load_generic_data(self):
        """Load generic metadata.""" 
        # For other file formats, metadata might be stored differently
        pass
        
    def _set_defaults(self):
        """Set default values for all fields."""
        now = QDateTime.currentDateTime()
        
        if self._file_type == "po":
            self._po_pot_date.setDateTime(now)
            self._po_revision_date.setDateTime(now) 
            self._po_charset.setCurrentText("UTF-8")
            self._po_encoding.setCurrentText("8bit")
            self._po_plural_forms.setText("nplurals=2; plural=(n != 1);")
            
        elif self._file_type == "ts":
            self._ts_version.setText("2.1")
            self._ts_source_language.setCurrentText("English (en)")
            
        elif self._file_type in ("xliff", "xlf"):
            self._xliff_version.setCurrentText("1.2")
            self._xliff_datatype.setCurrentText("plaintext")
            self._xliff_tool_name.setText("LinguaEdit")
            self._xliff_tool_id.setText("LinguaEdit")
            
    def _restore_defaults(self):
        """Restore default values."""
        reply = QMessageBox.question(
            self,
            self.tr("Restore Defaults"),
            self.tr("Restore all fields to default values?"),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._set_defaults()
            
    def _save_changes(self):
        """Save changes back to the file data."""
        if not self._file_data:
            self.reject()
            return
            
        if self._file_type == "po":
            self._save_po_changes()
        elif self._file_type == "ts":
            self._save_ts_changes()
        elif self._file_type in ("xliff", "xlf"):
            self._save_xliff_changes()
            
        self.accept()
        
    def _save_po_changes(self):
        """Save PO file changes."""
        if not hasattr(self._file_data, 'metadata'):
            self._file_data.metadata = {}
            
        metadata = self._file_data.metadata
        
        # Project information
        metadata["Project-Id-Version"] = self._po_project_id.text()
        metadata["Report-Msgid-Bugs-To"] = self._po_bugs_address.text()
        
        # Translation information
        metadata["Last-Translator"] = self._po_translator.text()
        metadata["Language-Team"] = self._po_team.text()
        
        # Language
        lang_data = self._po_language.currentData()
        if lang_data:
            metadata["Language"] = lang_data
        else:
            metadata["Language"] = self._po_language.currentText()
            
        # Dates
        pot_date = self._po_pot_date.dateTime().toString("yyyy-MM-dd hh:mm")
        metadata["POT-Creation-Date"] = pot_date
        
        revision_date = self._po_revision_date.dateTime().toString("yyyy-MM-dd hh:mm")
        metadata["PO-Revision-Date"] = revision_date
        
        # Content type
        charset = self._po_charset.currentText()
        metadata["Content-Type"] = f"text/plain; charset={charset}"
        metadata["Content-Transfer-Encoding"] = self._po_encoding.currentText()
        
        # Plural forms
        metadata["Plural-Forms"] = self._po_plural_forms.text()
        
    def _save_ts_changes(self):
        """Save TS file changes."""
        # Set language attributes
        lang_data = self._ts_language.currentData()
        if lang_data:
            self._file_data.language = lang_data
        else:
            self._file_data.language = self._ts_language.currentText()
            
        source_lang_data = self._ts_source_language.currentData()
        if source_lang_data:
            self._file_data.source_language = source_lang_data
        else:
            self._file_data.source_language = self._ts_source_language.currentText()
            
        self._file_data.version = self._ts_version.text()
        
    def _save_xliff_changes(self):
        """Save XLIFF file changes.""" 
        # Set language attributes
        source_lang_data = self._xliff_source_lang.currentData()
        if source_lang_data:
            self._file_data.source_language = source_lang_data
        else:
            self._file_data.source_language = self._xliff_source_lang.currentText()
            
        target_lang_data = self._xliff_target_lang.currentData()
        if target_lang_data:
            self._file_data.target_language = target_lang_data
        else:
            self._file_data.target_language = self._xliff_target_lang.currentText()
            
        self._file_data.version = self._xliff_version.currentText()
        self._file_data.original = self._xliff_original.text()
        
    def get_modified_data(self) -> Optional[Dict[str, Any]]:
        """Get the modified data (if any changes were made)."""
        # This method could be used to return just the changed fields
        # For now, changes are applied directly to the file_data object
        return None