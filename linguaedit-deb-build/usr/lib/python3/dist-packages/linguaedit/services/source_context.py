"""Source code context lookup service."""

from __future__ import annotations

import re
import requests
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal


@dataclass
class SourceReference:
    """A reference to source code location."""
    file_path: str
    line_number: int
    context_before: List[str]
    context_after: List[str]
    target_line: str
    language: str = "text"


class SourceContextService(QObject):
    """Service for fetching source code context from references."""
    
    context_loaded = Signal(str, object)  # reference_string, SourceReference
    
    def __init__(self):
        super().__init__()
        self._cache = {}  # reference -> SourceReference
        
    def parse_reference(self, reference: str) -> Optional[Tuple[str, int]]:
        """Parse a source reference string like 'file.py:123' or 'src/main.c:45'."""
        # Common patterns:
        # file.py:123
        # src/main.c:45
        # /path/to/file.js:67
        # https://github.com/user/repo/blob/main/file.py#L123
        
        # GitHub URL pattern
        github_pattern = r'https://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/([^#]+)#L(\d+)'
        github_match = re.match(github_pattern, reference)
        if github_match:
            user, repo, branch, file_path, line_num = github_match.groups()
            return f"github:{user}/{repo}/{branch}/{file_path}", int(line_num)
        
        # Local file pattern
        local_pattern = r'^([^:]+):(\d+)$'
        local_match = re.match(local_pattern, reference)
        if local_match:
            file_path, line_num = local_match.groups()
            return file_path, int(line_num)
        
        return None
    
    def get_context(self, reference: str, context_lines: int = 5) -> Optional[SourceReference]:
        """Get source code context for a reference."""
        if reference in self._cache:
            return self._cache[reference]
        
        parsed = self.parse_reference(reference)
        if not parsed:
            return None
        
        file_path, line_number = parsed
        
        try:
            if file_path.startswith('github:'):
                context = self._fetch_github_context(file_path, line_number, context_lines)
            else:
                context = self._fetch_local_context(file_path, line_number, context_lines)
            
            if context:
                self._cache[reference] = context
                self.context_loaded.emit(reference, context)
                return context
                
        except Exception as e:
            print(f"Error fetching context for {reference}: {e}")
        
        return None
    
    def _fetch_local_context(self, file_path: str, line_number: int, context_lines: int) -> Optional[SourceReference]:
        """Fetch context from a local file."""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                # Try to find relative to common locations
                for base in [Path.cwd(), Path.cwd() / "src", Path.cwd().parent]:
                    full_path = base / file_path
                    if full_path.exists():
                        path = full_path
                        break
            
            if not path.exists():
                return None
            
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            if line_number < 1 or line_number > len(lines):
                return None
            
            # Extract context
            start_line = max(0, line_number - context_lines - 1)
            end_line = min(len(lines), line_number + context_lines)
            
            target_line = lines[line_number - 1].rstrip()
            context_before = [lines[i].rstrip() for i in range(start_line, line_number - 1)]
            context_after = [lines[i].rstrip() for i in range(line_number, end_line)]
            
            # Determine language from file extension
            language = self._detect_language(path.suffix)
            
            return SourceReference(
                file_path=str(path),
                line_number=line_number,
                context_before=context_before,
                context_after=context_after,
                target_line=target_line,
                language=language
            )
            
        except Exception as e:
            print(f"Error reading local file {file_path}: {e}")
            return None
    
    def _fetch_github_context(self, github_path: str, line_number: int, context_lines: int) -> Optional[SourceReference]:
        """Fetch context from GitHub API."""
        try:
            # Parse github:user/repo/branch/file/path
            parts = github_path[7:].split('/', 3)  # Remove 'github:' prefix
            if len(parts) < 4:
                return None
            
            user, repo, branch, file_path = parts
            
            # GitHub API URL
            api_url = f"https://api.github.com/repos/{user}/{repo}/contents/{file_path}"
            params = {'ref': branch}
            
            response = requests.get(api_url, params=params, timeout=10)
            if response.status_code != 200:
                return None
            
            data = response.json()
            if data.get('type') != 'file':
                return None
            
            # Decode content (it's base64 encoded)
            import base64
            content = base64.b64decode(data['content']).decode('utf-8')
            lines = content.splitlines()
            
            if line_number < 1 or line_number > len(lines):
                return None
            
            # Extract context
            start_line = max(0, line_number - context_lines - 1)
            end_line = min(len(lines), line_number + context_lines)
            
            target_line = lines[line_number - 1]
            context_before = lines[start_line:line_number - 1]
            context_after = lines[line_number:end_line]
            
            # Determine language from file extension
            language = self._detect_language(Path(file_path).suffix)
            
            return SourceReference(
                file_path=f"https://github.com/{user}/{repo}/blob/{branch}/{file_path}",
                line_number=line_number,
                context_before=context_before,
                context_after=context_after,
                target_line=target_line,
                language=language
            )
            
        except Exception as e:
            print(f"Error fetching from GitHub {github_path}: {e}")
            return None
    
    def _detect_language(self, file_extension: str) -> str:
        """Detect programming language from file extension."""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.xml': 'xml',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.ini': 'ini',
            '.cfg': 'ini',
            '.sh': 'bash',
            '.bash': 'bash',
            '.zsh': 'bash',
            '.fish': 'fish',
            '.ps1': 'powershell',
            '.sql': 'sql',
            '.md': 'markdown',
            '.rst': 'rst',
            '.tex': 'latex',
        }
        
        return ext_map.get(file_extension.lower(), 'text')


# Global instance
_source_context_service = None

def get_source_context_service() -> SourceContextService:
    """Get the global source context service instance."""
    global _source_context_service
    if _source_context_service is None:
        _source_context_service = SourceContextService()
    return _source_context_service