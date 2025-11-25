"""Citation tracking for transparency."""

from dataclasses import dataclass
from typing import List


@dataclass
class Citation:
    """Citation for a signal or method used."""
    
    source: str  # Library name
    method: str  # Method/component name
    component: str  # Signal component
    confidence_contribution: float = 0.0


class CitationTracker:
    """Tracks citations during pipeline execution."""
    
    def __init__(self):
        self.citations: List[Citation] = []
    
    def add(self, source: str, method: str, component: str, contribution: float = 0.0):
        """Add a citation."""
        citation = Citation(
            source=source,
            method=method,
            component=component,
            confidence_contribution=contribution
        )
        self.citations.append(citation)
        return citation
    
    def get_all(self) -> List[Citation]:
        """Get all citations."""
        return self.citations.copy()
    
    def clear(self):
        """Clear all citations."""
        self.citations.clear()


# Pre-defined citation templates
CITATIONS = {
    "spacy_phrase_matcher": lambda: Citation("spaCy", "PhraseMatcher", "exact_lookup"),
    "rapidfuzz_token_set": lambda: Citation("RapidFuzz", "token_set_ratio", "fuzzy_matching"),
    "rapidfuzz_partial": lambda: Citation("RapidFuzz", "partial_ratio", "fuzzy_matching"),
    "jellyfish_levenshtein": lambda: Citation("jellyfish", "levenshtein_distance", "string_similarity"),
    "jellyfish_jaro_winkler": lambda: Citation("jellyfish", "jaro_winkler_similarity", "string_similarity"),
    "sentence_transformers": lambda: Citation("SentenceTransformers", "embedding_cosine", "semantic_similarity"),
    "faiss_ann": lambda: Citation("Faiss", "ANN_search", "candidate_generation"),
    "hnswlib_ann": lambda: Citation("hnswlib", "ANN_search", "candidate_generation"),
    "flashtext": lambda: Citation("FlashText", "KeywordProcessor", "exact_lookup"),
    "custom_acronym": lambda: Citation("Custom", "acronym_detection", "string_similarity"),
    "custom_normalization": lambda: Citation("Custom", "text_normalization", "preprocessing"),
}
