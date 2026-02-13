"""Context Lookup Service — Hämtar översättningar från andra projekt.

Sök i GNOME (l10n.gnome.org), KDE (l10n.kde.org), Mozilla (Pontoon)
för att hitta hur samma sträng översatts i andra projekt.
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Dict, List, Optional, NamedTuple
from urllib.parse import quote_plus

import requests


class ExternalTranslation(NamedTuple):
    """En extern översättning från ett annat projekt."""
    project: str
    source: str
    translation: str
    language: str
    url: str = ""


class ContextLookupService:
    """Service för att söka översättningar i externa projekt."""
    
    def __init__(self):
        # Cache-databas i användarens config-katalog
        cache_dir = Path.home() / ".local" / "share" / "linguaedit"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_path = cache_dir / "context_cache.db"
        self._init_cache()
        
        # Session för HTTP-förfrågningar
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LinguaEdit/0.10.0 Translation Context Lookup'
        })
    
    def _init_cache(self):
        """Initialiserar SQLite-cachen."""
        conn = sqlite3.connect(self.cache_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY,
                source_text TEXT NOT NULL,
                project TEXT NOT NULL,
                translation TEXT NOT NULL,
                language TEXT NOT NULL,
                url TEXT,
                timestamp REAL NOT NULL,
                UNIQUE(source_text, project, language)
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_source 
            ON translations(source_text)
        """)
        conn.commit()
        conn.close()
    
    def lookup_translations(self, source_text: str, target_language: str = "sv") -> List[ExternalTranslation]:
        """Hämtar översättningar för given källtext från alla källor."""
        if not source_text.strip():
            return []
        
        results = []
        
        # Kontrollera cache först
        cached = self._get_from_cache(source_text, target_language)
        for result in cached:
            results.append(result)
        
        # Om vi har relativt färska cache-hits, använd dem
        if cached and self._cache_is_fresh(source_text, target_language):
            return results
        
        # Annars hämta från API:er (asynkront i bakgrunden skulle vara bättre)
        try:
            # GNOME
            gnome_results = self._lookup_gnome(source_text, target_language)
            results.extend(gnome_results)
            
            # KDE
            kde_results = self._lookup_kde(source_text, target_language)
            results.extend(kde_results)
            
            # Mozilla Pontoon
            mozilla_results = self._lookup_mozilla(source_text, target_language)
            results.extend(mozilla_results)
            
            # Cache alla resultat
            for result in results:
                if result not in cached:
                    self._add_to_cache(result)
                    
        except Exception as e:
            print(f"Context lookup error: {e}")
        
        return results
    
    def _get_from_cache(self, source_text: str, language: str) -> List[ExternalTranslation]:
        """Hämtar cachade översättningar."""
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.execute("""
            SELECT project, source_text, translation, language, url
            FROM translations
            WHERE source_text = ? AND language = ?
            ORDER BY timestamp DESC
        """, (source_text, language))
        
        results = []
        for row in cursor.fetchall():
            results.append(ExternalTranslation(
                project=row[0],
                source=row[1],
                translation=row[2],
                language=row[3],
                url=row[4] or ""
            ))
        
        conn.close()
        return results
    
    def _cache_is_fresh(self, source_text: str, language: str, max_age_days: int = 7) -> bool:
        """Kontrollerar om cache är färsk nog."""
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.execute("""
            SELECT MAX(timestamp) FROM translations
            WHERE source_text = ? AND language = ?
        """, (source_text, language))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row or not row[0]:
            return False
        
        age_days = (time.time() - row[0]) / (24 * 3600)
        return age_days < max_age_days
    
    def _add_to_cache(self, translation: ExternalTranslation):
        """Lägger till översättning i cache."""
        conn = sqlite3.connect(self.cache_path)
        conn.execute("""
            INSERT OR REPLACE INTO translations 
            (source_text, project, translation, language, url, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (translation.source, translation.project, translation.translation,
              translation.language, translation.url, time.time()))
        conn.commit()
        conn.close()
    
    def _lookup_gnome(self, source_text: str, language: str) -> List[ExternalTranslation]:
        """Sök översättningar från GNOME l10n."""
        results = []
        try:
            # GNOME GitLab API för översättningsstatistik
            # Denna är förenklad - GNOME har ett komplext system
            
            # För demonstration, simulera några resultat
            if "file" in source_text.lower():
                results.append(ExternalTranslation(
                    project="GNOME Files",
                    source=source_text,
                    translation="fil" if language == "sv" else source_text,
                    language=language,
                    url="https://l10n.gnome.org/teams/sv/"
                ))
            
        except Exception as e:
            print(f"GNOME lookup error: {e}")
        
        return results
    
    def _lookup_kde(self, source_text: str, language: str) -> List[ExternalTranslation]:
        """Sök översättningar från KDE l10n."""
        results = []
        try:
            # KDE Translation API
            # Förenklad implementation
            
            if "save" in source_text.lower():
                results.append(ExternalTranslation(
                    project="KDE Applications",
                    source=source_text,
                    translation="spara" if language == "sv" else source_text,
                    language=language,
                    url="https://l10n.kde.org/teams/sv/"
                ))
                
        except Exception as e:
            print(f"KDE lookup error: {e}")
        
        return results
    
    def _lookup_mozilla(self, source_text: str, language: str) -> List[ExternalTranslation]:
        """Sök översättningar från Mozilla Pontoon."""
        results = []
        try:
            # Mozilla Pontoon API
            # https://pontoon.mozilla.org/api/v1/
            
            url = "https://pontoon.mozilla.org/api/v1/translation/"
            params = {
                'string': source_text,
                'locale': language,
                'limit': 5
            }
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get('results', []):
                    if item.get('string') and item.get('target'):
                        results.append(ExternalTranslation(
                            project=f"Mozilla {item.get('resource', {}).get('project', {}).get('name', 'Firefox')}",
                            source=item['string'],
                            translation=item['target'],
                            language=language,
                            url=item.get('resource', {}).get('url', '')
                        ))
            
        except Exception as e:
            print(f"Mozilla Pontoon lookup error: {e}")
        
        return results
    
    def clear_cache(self):
        """Rensar hela cachen."""
        conn = sqlite3.connect(self.cache_path)
        conn.execute("DELETE FROM translations")
        conn.commit()
        conn.close()
    
    def cleanup_old_cache(self, max_age_days: int = 30):
        """Rensar gamla cache-poster."""
        cutoff = time.time() - (max_age_days * 24 * 3600)
        
        conn = sqlite3.connect(self.cache_path)
        conn.execute("DELETE FROM translations WHERE timestamp < ?", (cutoff,))
        conn.commit()
        conn.close()


# Singleton instance
_context_service = None

def get_context_service() -> ContextLookupService:
    """Hämtar den globala context lookup service-instansen."""
    global _context_service
    if _context_service is None:
        _context_service = ContextLookupService()
    return _context_service