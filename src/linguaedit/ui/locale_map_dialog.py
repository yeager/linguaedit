"""Locale Map Dialog - World map showing translation progress by region."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QGroupBox, QListWidget, QListWidgetItem,
    QProgressBar, QTextEdit, QSplitter, QFrame, QComboBox
)
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPolygonF
from PySide6.QtSvg import QSvgRenderer


class WorldMapWidget(QWidget):
    """Widget that displays a world map with color-coded translation progress."""
    
    country_clicked = Signal(str, dict)  # country_code, stats
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 500)
        self._country_stats = {}  # country_code -> {'progress': 0-100, 'files': [], 'total': 0, 'translated': 0}
        self._svg_renderer = None
        self._country_regions = self._load_country_regions()
        
        # Load world map SVG (simplified)
        self._load_world_map()
        
    def _load_world_map(self):
        """Load or create a simple world map SVG."""
        # For now, create a simple SVG programmatically
        # In a real implementation, you'd load a proper world map SVG
        svg_content = self._create_simple_world_map_svg()
        
        self._svg_renderer = QSvgRenderer()
        self._svg_renderer.load(svg_content.encode('utf-8'))
    
    def _create_simple_world_map_svg(self) -> str:
        """Create a simple world map SVG with basic country shapes."""
        # This is a very simplified representation
        # In practice, you'd use a proper world map SVG file
        return '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="500" xmlns="http://www.w3.org/2000/svg">
  <!-- Simplified world map -->
  <!-- North America -->
  <rect id="US" x="100" y="100" width="200" height="150" fill="#cccccc" stroke="#333"/>
  <rect id="CA" x="100" y="50" width="200" height="50" fill="#cccccc" stroke="#333"/>
  <rect id="MX" x="100" y="250" width="150" height="80" fill="#cccccc" stroke="#333"/>
  
  <!-- South America -->
  <rect id="BR" x="250" y="300" width="120" height="180" fill="#cccccc" stroke="#333"/>
  <rect id="AR" x="230" y="420" width="80" height="60" fill="#cccccc" stroke="#333"/>
  
  <!-- Europe -->
  <rect id="GB" x="420" y="80" width="40" height="60" fill="#cccccc" stroke="#333"/>
  <rect id="FR" x="460" y="100" width="50" height="60" fill="#cccccc" stroke="#333"/>
  <rect id="DE" x="480" y="80" width="50" height="60" fill="#cccccc" stroke="#333"/>
  <rect id="ES" x="440" y="140" width="60" height="50" fill="#cccccc" stroke="#333"/>
  <rect id="IT" x="500" y="120" width="40" height="80" fill="#cccccc" stroke="#333"/>
  <rect id="RU" x="540" y="50" width="200" height="100" fill="#cccccc" stroke="#333"/>
  
  <!-- Asia -->
  <rect id="CN" x="600" y="120" width="120" height="100" fill="#cccccc" stroke="#333"/>
  <rect id="JP" x="720" y="130" width="60" height="80" fill="#cccccc" stroke="#333"/>
  <rect id="IN" x="580" y="180" width="80" height="80" fill="#cccccc" stroke="#333"/>
  <rect id="KR" x="680" y="140" width="30" height="40" fill="#cccccc" stroke="#333"/>
  
  <!-- Africa -->
  <rect id="ZA" x="500" y="350" width="80" height="60" fill="#cccccc" stroke="#333"/>
  <rect id="NG" x="460" y="250" width="60" height="60" fill="#cccccc" stroke="#333"/>
  
  <!-- Australia -->
  <rect id="AU" x="650" y="350" width="120" height="80" fill="#cccccc" stroke="#333"/>
  
  <!-- Labels -->
  <text x="200" y="175" font-family="Arial" font-size="12" fill="#333">US</text>
  <text x="200" y="75" font-family="Arial" font-size="12" fill="#333">CA</text>
  <text x="175" y="290" font-family="Arial" font-size="12" fill="#333">MX</text>
  <text x="310" y="390" font-family="Arial" font-size="12" fill="#333">BR</text>
  <text x="440" y="110" font-family="Arial" font-size="12" fill="#333">GB</text>
  <text x="485" y="130" font-family="Arial" font-size="12" fill="#333">FR</text>
  <text x="505" y="110" font-family="Arial" font-size="12" fill="#333">DE</text>
  <text x="660" y="170" font-family="Arial" font-size="12" fill="#333">CN</text>
  <text x="745" y="170" font-family="Arial" font-size="12" fill="#333">JP</text>
  <text x="620" y="220" font-family="Arial" font-size="12" fill="#333">IN</text>
  <text x="710" y="380" font-family="Arial" font-size="12" fill="#333">AU</text>
</svg>'''
    
    def _load_country_regions(self) -> Dict[str, QRectF]:
        """Load country regions for click detection."""
        # This would normally be loaded from a proper mapping file
        return {
            'US': QRectF(100, 100, 200, 150),
            'CA': QRectF(100, 50, 200, 50),
            'MX': QRectF(100, 250, 150, 80),
            'BR': QRectF(250, 300, 120, 180),
            'AR': QRectF(230, 420, 80, 60),
            'GB': QRectF(420, 80, 40, 60),
            'FR': QRectF(460, 100, 50, 60),
            'DE': QRectF(480, 80, 50, 60),
            'ES': QRectF(440, 140, 60, 50),
            'IT': QRectF(500, 120, 40, 80),
            'RU': QRectF(540, 50, 200, 100),
            'CN': QRectF(600, 120, 120, 100),
            'JP': QRectF(720, 130, 60, 80),
            'IN': QRectF(580, 180, 80, 80),
            'KR': QRectF(680, 140, 30, 40),
            'ZA': QRectF(500, 350, 80, 60),
            'NG': QRectF(460, 250, 60, 60),
            'AU': QRectF(650, 350, 120, 80),
        }
    
    def set_country_stats(self, stats: Dict[str, Dict]):
        """Set translation statistics for countries."""
        self._country_stats = stats
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), QColor(240, 248, 255))  # Light blue (ocean)
        
        # Draw base map
        if self._svg_renderer:
            # Draw the SVG but override colors based on stats
            for country_code, rect in self._country_regions.items():
                # Get color based on translation progress
                color = self._get_country_color(country_code)
                
                # Draw country
                painter.fillRect(rect, QBrush(color))
                painter.setPen(QPen(QColor(51, 51, 51), 1))
                painter.drawRect(rect)
                
                # Draw country label
                painter.setPen(QPen(QColor(51, 51, 51)))
                painter.setFont(QFont("Arial", 10))
                painter.drawText(rect, Qt.AlignCenter, country_code)
        
        # Draw legend
        self._draw_legend(painter)
    
    def _get_country_color(self, country_code: str) -> QColor:
        """Get color for country based on translation progress."""
        if country_code not in self._country_stats:
            return QColor(200, 200, 200)  # Gray for no data
        
        progress = self._country_stats[country_code].get('progress', 0)
        
        if progress >= 95:
            return QColor(46, 125, 50)    # Dark green (complete)
        elif progress >= 75:
            return QColor(102, 187, 106)  # Light green (mostly done)
        elif progress >= 50:
            return QColor(255, 193, 7)    # Yellow (partial)
        elif progress >= 25:
            return QColor(255, 152, 0)    # Orange (started)
        elif progress > 0:
            return QColor(244, 67, 54)    # Red (minimal)
        else:
            return QColor(158, 158, 158)  # Gray (not started)
    
    def _draw_legend(self, painter: QPainter):
        """Draw legend showing color meanings."""
        legend_x = 20
        legend_y = self.height() - 150
        
        painter.fillRect(legend_x - 10, legend_y - 10, 140, 130, QColor(255, 255, 255, 200))
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.drawRect(legend_x - 10, legend_y - 10, 140, 130)
        
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(legend_x, legend_y, self.tr("Translation Progress"))
        
        legend_items = [
            (QColor(46, 125, 50), "95-100% (Complete)"),
            (QColor(102, 187, 106), "75-94% (Nearly done)"),
            (QColor(255, 193, 7), "50-74% (Partial)"),
            (QColor(255, 152, 0), "25-49% (Started)"),
            (QColor(244, 67, 54), "1-24% (Minimal)"),
            (QColor(158, 158, 158), "0% (Not started)"),
        ]
        
        painter.setFont(QFont("Arial", 8))
        for i, (color, text) in enumerate(legend_items):
            y = legend_y + 20 + i * 16
            painter.fillRect(legend_x, y - 8, 12, 12, color)
            painter.drawRect(legend_x, y - 8, 12, 12)
            painter.drawText(legend_x + 18, y + 2, text)
    
    def mousePressEvent(self, event):
        """Handle mouse clicks on countries."""
        if event.button() == Qt.LeftButton:
            pos = event.position()
            
            # Find clicked country
            for country_code, rect in self._country_regions.items():
                if rect.contains(pos):
                    stats = self._country_stats.get(country_code, {})
                    self.country_clicked.emit(country_code, stats)
                    break


class LocaleMapDialog(QDialog):
    """Dialog showing translation progress on a world map."""
    
    def __init__(self, parent=None, project_path: str = ""):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Translation Map"))
        self.setModal(True)
        self.resize(1200, 800)
        
        self._project_path = Path(project_path) if project_path else Path.cwd()
        self._locale_stats = {}
        
        self._setup_ui()
        self._scan_project_files()
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        
        # Left side: Map
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Project selector
        project_layout = QHBoxLayout()
        project_layout.addWidget(QLabel(self.tr("Project:")))
        
        self._project_combo = QComboBox()
        self._project_combo.addItem(str(self._project_path))
        self._project_combo.currentTextChanged.connect(self._on_project_changed)
        project_layout.addWidget(self._project_combo)
        
        browse_btn = QPushButton(self.tr("Browse..."))
        browse_btn.clicked.connect(self._browse_project)
        project_layout.addWidget(browse_btn)
        
        project_layout.addStretch()
        left_layout.addLayout(project_layout)
        
        # World map
        map_group = QGroupBox(self.tr("Translation Progress by Region"))
        map_layout = QVBoxLayout(map_group)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self._world_map = WorldMapWidget()
        self._world_map.country_clicked.connect(self._on_country_clicked)
        scroll_area.setWidget(self._world_map)
        
        map_layout.addWidget(scroll_area)
        left_layout.addWidget(map_group)
        
        layout.addWidget(left_widget, 2)
        
        # Right side: Details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Country details
        details_group = QGroupBox(self.tr("Country Details"))
        details_layout = QVBoxLayout(details_group)
        
        self._country_label = QLabel(self.tr("Click on a country to see details"))
        self._country_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        details_layout.addWidget(self._country_label)
        
        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        details_layout.addWidget(self._progress_bar)
        
        self._stats_text = QTextEdit()
        self._stats_text.setMaximumHeight(150)
        self._stats_text.setVisible(False)
        details_layout.addWidget(self._stats_text)
        
        right_layout.addWidget(details_group)
        
        # File list
        files_group = QGroupBox(self.tr("Locale Files"))
        files_layout = QVBoxLayout(files_group)
        
        self._files_list = QListWidget()
        self._files_list.itemDoubleClicked.connect(self._on_file_double_clicked)
        files_layout.addWidget(self._files_list)
        
        right_layout.addWidget(files_group)
        
        # Summary
        summary_group = QGroupBox(self.tr("Project Summary"))
        summary_layout = QVBoxLayout(summary_group)
        
        self._summary_text = QTextEdit()
        self._summary_text.setMaximumHeight(120)
        summary_layout.addWidget(self._summary_text)
        
        right_layout.addWidget(summary_group)
        
        layout.addWidget(right_widget, 1)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        refresh_btn = QPushButton(self.tr("Refresh"))
        refresh_btn.clicked.connect(self._scan_project_files)
        button_layout.addWidget(refresh_btn)
        
        close_btn = QPushButton(self.tr("Close"))
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def _browse_project(self):
        """Browse for project directory."""
        from PySide6.QtWidgets import QFileDialog
        
        directory = QFileDialog.getExistingDirectory(
            self, self.tr("Select Project Directory"), str(self._project_path)
        )
        
        if directory:
            self._project_path = Path(directory)
            self._project_combo.clear()
            self._project_combo.addItem(directory)
            self._scan_project_files()
    
    def _on_project_changed(self, path: str):
        """Handle project path change."""
        if path:
            self._project_path = Path(path)
            self._scan_project_files()
    
    def _scan_project_files(self):
        """Scan project directory for translation files."""
        if not self._project_path.exists():
            return
        
        locale_files = {}
        
        # Scan for translation files
        patterns = ['*.po', '*.ts', '*.json', '*.properties', '*.strings', '*.resx', '*.asset']
        
        for pattern in patterns:
            for file_path in self._project_path.rglob(pattern):
                # Try to extract locale from file name/path
                locale = self._extract_locale_from_path(file_path)
                if locale:
                    country_code = self._locale_to_country(locale)
                    if country_code not in locale_files:
                        locale_files[country_code] = []
                    locale_files[country_code].append(file_path)
        
        # Calculate statistics for each country
        self._locale_stats = {}
        for country_code, files in locale_files.items():
            stats = self._calculate_file_stats(files)
            self._locale_stats[country_code] = {
                'progress': stats['progress'],
                'files': files,
                'total': stats['total'],
                'translated': stats['translated'],
                'fuzzy': stats.get('fuzzy', 0)
            }
        
        # Update map
        self._world_map.set_country_stats(self._locale_stats)
        
        # Update summary
        self._update_summary()
    
    def _extract_locale_from_path(self, file_path: Path) -> Optional[str]:
        """Extract locale code from file path."""
        # Common patterns:
        # lang/de_DE/messages.po
        # locales/fr/LC_MESSAGES/app.po
        # i18n/es.json
        # strings/ja.strings
        
        path_parts = file_path.parts
        filename = file_path.stem
        
        # Check filename for locale (e.g., messages_de.po -> de)
        if '_' in filename:
            parts = filename.split('_')
            for part in parts:
                if len(part) == 2 and part.isalpha():
                    return part.lower()
                elif len(part) == 5 and '_' in part:
                    return part.lower()
        
        # Check path components
        for part in path_parts:
            # Two-letter language codes
            if len(part) == 2 and part.isalpha():
                return part.lower()
            # Full locale codes like en_US
            elif len(part) == 5 and '_' in part:
                return part.lower()
            # Special directories
            elif part in ['de_DE', 'en_US', 'fr_FR', 'es_ES', 'ja_JP', 'zh_CN']:
                return part.lower()
        
        return None
    
    def _locale_to_country(self, locale: str) -> str:
        """Convert locale code to country code."""
        # Map locale codes to country codes for map display
        locale_map = {
            'en': 'US', 'en_us': 'US', 'en_gb': 'GB', 'en_ca': 'CA', 'en_au': 'AU',
            'de': 'DE', 'de_de': 'DE',
            'fr': 'FR', 'fr_fr': 'FR', 'fr_ca': 'CA',
            'es': 'ES', 'es_es': 'ES', 'es_mx': 'MX',
            'it': 'IT', 'it_it': 'IT',
            'ja': 'JP', 'ja_jp': 'JP',
            'ko': 'KR', 'ko_kr': 'KR',
            'zh': 'CN', 'zh_cn': 'CN', 'zh_tw': 'CN',
            'pt': 'BR', 'pt_br': 'BR', 'pt_pt': 'ES',
            'ru': 'RU', 'ru_ru': 'RU',
            'ar': 'NG', 'ar_sa': 'NG',
            'hi': 'IN', 'hi_in': 'IN',
            'nl': 'DE', 'nl_nl': 'DE',
            'sv': 'DE', 'sv_se': 'DE',
            'no': 'DE', 'nb_no': 'DE',
            'da': 'DE', 'da_dk': 'DE',
            'fi': 'DE', 'fi_fi': 'DE',
            'pl': 'DE', 'pl_pl': 'DE',
            'cs': 'DE', 'cs_cz': 'DE',
            'hu': 'DE', 'hu_hu': 'DE',
        }
        
        return locale_map.get(locale, 'US')  # Default to US if not found
    
    def _calculate_file_stats(self, files: List[Path]) -> Dict[str, int]:
        """Calculate translation statistics for files."""
        total_strings = 0
        translated_strings = 0
        fuzzy_strings = 0
        
        for file_path in files:
            try:
                # This is simplified - in practice you'd use the actual parsers
                if file_path.suffix == '.po':
                    stats = self._analyze_po_file(file_path)
                elif file_path.suffix == '.json':
                    stats = self._analyze_json_file(file_path)
                else:
                    stats = {'total': 1, 'translated': 1, 'fuzzy': 0}  # Assume translated
                
                total_strings += stats['total']
                translated_strings += stats['translated']
                fuzzy_strings += stats.get('fuzzy', 0)
                
            except Exception:
                # If file can't be analyzed, assume it's complete
                total_strings += 1
                translated_strings += 1
        
        progress = (translated_strings / total_strings * 100) if total_strings > 0 else 0
        
        return {
            'total': total_strings,
            'translated': translated_strings,
            'fuzzy': fuzzy_strings,
            'progress': round(progress, 1)
        }
    
    def _analyze_po_file(self, file_path: Path) -> Dict[str, int]:
        """Quick analysis of PO file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count msgid/msgstr pairs
            msgids = content.count('msgid ')
            translated = content.count('msgstr ') - content.count('msgstr ""')
            fuzzy = content.count('#, fuzzy')
            
            return {'total': max(msgids - 1, 0), 'translated': max(translated, 0), 'fuzzy': fuzzy}
        except Exception:
            return {'total': 1, 'translated': 0, 'fuzzy': 0}
    
    def _analyze_json_file(self, file_path: Path) -> Dict[str, int]:
        """Quick analysis of JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                total = len(data)
                translated = len([v for v in data.values() if v and str(v).strip()])
                return {'total': total, 'translated': translated, 'fuzzy': 0}
        except Exception:
            pass
        
        return {'total': 1, 'translated': 1, 'fuzzy': 0}
    
    def _on_country_clicked(self, country_code: str, stats: Dict):
        """Handle country click on map."""
        if not stats:
            self._country_label.setText(f"{country_code}: {self.tr('No translation data')}")
            self._progress_bar.setVisible(False)
            self._stats_text.setVisible(False)
            self._files_list.clear()
            return
        
        self._country_label.setText(f"{country_code}: {stats.get('progress', 0):.1f}% {self.tr('Complete')}")
        
        self._progress_bar.setVisible(True)
        self._progress_bar.setValue(int(stats.get('progress', 0)))
        
        # Show detailed stats
        self._stats_text.setVisible(True)
        stats_html = f"""
        <b>{self.tr("Translation Statistics")}</b><br>
        {self.tr("Total strings")}: {stats.get('total', 0)}<br>
        {self.tr("Translated")}: {stats.get('translated', 0)}<br>
        {self.tr("Fuzzy")}: {stats.get('fuzzy', 0)}<br>
        {self.tr("Missing")}: {stats.get('total', 0) - stats.get('translated', 0)}<br>
        """
        self._stats_text.setHtml(stats_html)
        
        # Show files
        self._files_list.clear()
        for file_path in stats.get('files', []):
            item = QListWidgetItem(str(file_path.relative_to(self._project_path)))
            item.setData(Qt.UserRole, str(file_path))
            self._files_list.addItem(item)
    
    def _on_file_double_clicked(self, item: QListWidgetItem):
        """Handle double-click on file item."""
        file_path = item.data(Qt.UserRole)
        if file_path:
            # Emit signal to open file (would be connected by parent)
            # For now, just show a message
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, self.tr("Open File"), 
                                  self.tr("Would open: {}").format(file_path))
    
    def _update_summary(self):
        """Update project summary."""
        if not self._locale_stats:
            self._summary_text.setHtml(self.tr("No translation files found in project."))
            return
        
        total_countries = len(self._locale_stats)
        avg_progress = sum(stats['progress'] for stats in self._locale_stats.values()) / total_countries
        
        complete_countries = len([s for s in self._locale_stats.values() if s['progress'] >= 95])
        partial_countries = len([s for s in self._locale_stats.values() if 5 <= s['progress'] < 95])
        empty_countries = len([s for s in self._locale_stats.values() if s['progress'] < 5])
        
        summary_html = f"""
        <b>{self.tr("Project Summary")}</b><br><br>
        {self.tr("Countries with translations")}: {total_countries}<br>
        {self.tr("Average progress")}: {avg_progress:.1f}%<br><br>
        
        {self.tr("Complete")} (≥95%): {complete_countries}<br>
        {self.tr("Partial")} (5-94%): {partial_countries}<br>
        {self.tr("Minimal")} (<5%): {empty_countries}<br>
        """
        
        self._summary_text.setHtml(summary_html)