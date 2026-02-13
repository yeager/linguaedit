"""Confidence scoring service for translations."""

from __future__ import annotations

import re
import threading
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from PySide6.QtCore import QObject, Signal


@dataclass
class ConfidenceFactors:
    """Individual factors contributing to confidence score."""
    tm_match: float = 0.0  # Translation memory match percentage
    length_ratio: float = 0.0  # How reasonable is the length compared to source
    format_strings: float = 0.0  # Format strings preserved correctly
    glossary_terms: float = 0.0  # Glossary terms used correctly
    ai_score: float = 0.0  # AI-based quality assessment
    consistency: float = 0.0  # Consistency with similar translations
    
    @property
    def overall_score(self) -> float:
        """Calculate overall confidence score (0-100)."""
        weights = {
            'tm_match': 0.25,
            'length_ratio': 0.15,
            'format_strings': 0.20,
            'glossary_terms': 0.15,
            'ai_score': 0.15,
            'consistency': 0.10
        }
        
        score = (
            self.tm_match * weights['tm_match'] +
            self.length_ratio * weights['length_ratio'] +
            self.format_strings * weights['format_strings'] +
            self.glossary_terms * weights['glossary_terms'] +
            self.ai_score * weights['ai_score'] +
            self.consistency * weights['consistency']
        )
        
        return min(100.0, max(0.0, score))


class ConfidenceCalculator(QObject):
    """Calculate confidence scores for translations."""
    
    score_updated = Signal(str, float, object)  # entry_id, score, factors
    
    def __init__(self):
        super().__init__()
        self._cache = {}  # entry_id -> ConfidenceFactors
        self._executor = ThreadPoolExecutor(max_workers=2)
        
    def calculate_confidence(self, entry_id: str, source: str, target: str, 
                           context: Dict[str, Any] = None) -> ConfidenceFactors:
        """Calculate confidence score for a translation entry."""
        if not target or not target.strip():
            return ConfidenceFactors()
        
        cache_key = f"{entry_id}:{hash(source + target)}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        factors = ConfidenceFactors()
        
        # Calculate each factor
        factors.tm_match = self._calculate_tm_match(source, target, context)
        factors.length_ratio = self._calculate_length_ratio(source, target)
        factors.format_strings = self._calculate_format_strings_score(source, target)
        factors.glossary_terms = self._calculate_glossary_score(source, target, context)
        factors.ai_score = self._calculate_ai_score(source, target, context)
        factors.consistency = self._calculate_consistency_score(source, target, context)
        
        self._cache[cache_key] = factors
        return factors
    
    def calculate_confidence_async(self, entry_id: str, source: str, target: str,
                                 context: Dict[str, Any] = None):
        """Calculate confidence score asynchronously."""
        future = self._executor.submit(
            self.calculate_confidence, entry_id, source, target, context
        )
        
        def on_complete(fut):
            try:
                factors = fut.result()
                self.score_updated.emit(entry_id, factors.overall_score, factors)
            except Exception as e:
                print(f"Error calculating confidence: {e}")
                self.score_updated.emit(entry_id, 0.0, ConfidenceFactors())
        
        future.add_done_callback(on_complete)
    
    def _calculate_tm_match(self, source: str, target: str, context: Dict[str, Any]) -> float:
        """Calculate TM match contribution (0-100)."""
        if not context or 'tm_match' not in context:
            return 50.0  # Default moderate score
        
        tm_percentage = context.get('tm_match', 0)
        
        # High TM match gives high confidence
        if tm_percentage >= 100:
            return 100.0
        elif tm_percentage >= 95:
            return 90.0
        elif tm_percentage >= 85:
            return 80.0
        elif tm_percentage >= 70:
            return 70.0
        elif tm_percentage >= 50:
            return 60.0
        else:
            return 40.0
    
    def _calculate_length_ratio(self, source: str, target: str) -> float:
        """Calculate length ratio score (0-100)."""
        if not source.strip():
            return 100.0
        
        source_len = len(source.strip())
        target_len = len(target.strip())
        
        ratio = target_len / source_len
        
        # Reasonable ratios get higher scores
        if 0.5 <= ratio <= 2.0:  # Within 50%-200% is very good
            return 100.0
        elif 0.3 <= ratio <= 3.0:  # Within 30%-300% is good
            return 80.0
        elif 0.2 <= ratio <= 4.0:  # Within 20%-400% is acceptable
            return 60.0
        elif 0.1 <= ratio <= 5.0:  # Within 10%-500% is suspicious
            return 40.0
        else:  # Beyond this is very suspicious
            return 20.0
    
    def _calculate_format_strings_score(self, source: str, target: str) -> float:
        """Calculate format strings preservation score (0-100)."""
        # Find format strings in source
        format_patterns = [
            r'%[sd%]',           # C-style
            r'{\d+}',            # Positional
            r'{\w+}',            # Named
            r'\$\{\w+\}',        # Variable
            r'@\w+@',            # Token
            r'<[^>]+>',          # XML tags
            r'\[[^\]]+\]',       # Brackets
        ]
        
        source_formats = set()
        target_formats = set()
        
        for pattern in format_patterns:
            source_formats.update(re.findall(pattern, source))
            target_formats.update(re.findall(pattern, target))
        
        if not source_formats:
            return 100.0  # No format strings to worry about
        
        # Check if all source formats are preserved in target
        missing = source_formats - target_formats
        extra = target_formats - source_formats
        
        if not missing and not extra:
            return 100.0  # Perfect match
        elif not missing:
            return 80.0   # All source formats preserved, but some extra
        elif len(missing) <= len(source_formats) * 0.5:
            return 60.0   # Most formats preserved
        else:
            return 20.0   # Many formats missing
    
    def _calculate_glossary_score(self, source: str, target: str, context: Dict[str, Any]) -> float:
        """Calculate glossary terms usage score (0-100)."""
        if not context or 'glossary_terms' not in context:
            return 70.0  # Default good score when no glossary available
        
        terms = context.get('glossary_terms', [])
        if not terms:
            return 70.0
        
        # Check if glossary terms are used correctly
        # This would need integration with the glossary service
        # For now, return a placeholder score
        found_terms = 0
        expected_terms = 0
        
        for term in terms:
            source_term = term.get('source', '')
            target_term = term.get('target', '')
            
            if source_term.lower() in source.lower():
                expected_terms += 1
                if target_term.lower() in target.lower():
                    found_terms += 1
        
        if expected_terms == 0:
            return 70.0
        
        usage_ratio = found_terms / expected_terms
        return usage_ratio * 100
    
    def _calculate_ai_score(self, source: str, target: str, context: Dict[str, Any]) -> float:
        """Calculate AI-based quality score (0-100)."""
        # This would integrate with an AI quality assessment service
        # For now, use some heuristics
        
        # Basic quality indicators
        score = 70.0  # Start with moderate score
        
        # Penalize very short translations for longer source
        if len(source) > 50 and len(target) < 10:
            score -= 30
        
        # Penalize identical source and target (likely untranslated)
        if source.strip() == target.strip():
            score -= 40
        
        # Bonus for proper sentence structure
        if target.strip().endswith(('.', '!', '?')):
            score += 5
        
        # Penalize all caps (likely placeholder)
        if target.isupper() and len(target) > 3:
            score -= 20
        
        return max(0.0, min(100.0, score))
    
    def _calculate_consistency_score(self, source: str, target: str, context: Dict[str, Any]) -> float:
        """Calculate consistency with similar translations (0-100)."""
        if not context or 'similar_translations' not in context:
            return 60.0  # Default score when no comparison data
        
        similar = context.get('similar_translations', [])
        if not similar:
            return 60.0
        
        # Compare with similar translations
        # This would need a proper similarity service
        # For now, return a placeholder score
        return 70.0
    
    def get_color_for_score(self, score: float) -> str:
        """Get color name for score visualization."""
        if score >= 80:
            return "green"
        elif score >= 60:
            return "orange"
        else:
            return "red"
    
    def get_badge_text(self, score: float) -> str:
        """Get badge text for score display."""
        return f"{score:.0f}%"


# Global instance
_confidence_calculator = None

def get_confidence_calculator() -> ConfidenceCalculator:
    """Get the global confidence calculator instance."""
    global _confidence_calculator
    if _confidence_calculator is None:
        _confidence_calculator = ConfidenceCalculator()
    return _confidence_calculator