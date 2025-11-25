"""Signals package."""

from ner_lib.signals.deterministic import (
    ExactMatcher,
    PhraseMatcherLookup,
    FlashTextLookup,
    DomainMatcher,
)
from ner_lib.signals.string_similarity import (
    token_set_ratio,
    partial_ratio,
    levenshtein_similarity,
    jaro_winkler_similarity,
    combined_fuzzy_score,
    quick_fuzzy_score,
)
from ner_lib.signals.acronym import (
    is_acronym_match,
    check_token_containment,
    acronym_score,
    quick_acronym_check,
)

# Semantic imports (may fail with dependency issues)
try:
    from ner_lib.signals.semantic import (
        EmbeddingModel,
        cosine_similarity,
        batch_cosine_similarity,
        semantic_similarity_score,
    )
    SEMANTIC_AVAILABLE = True
except (ImportError, AttributeError) as e:
    SEMANTIC_AVAILABLE = False
    EmbeddingModel = None
    cosine_similarity = None
    batch_cosine_similarity = None
    semantic_similarity_score = None

from ner_lib.signals.contextual import (
    recency_boost,
    domain_consistency_boost,
    shared_context_boost,
)

__all__ = [
    # Deterministic
    "ExactMatcher",
    "PhraseMatcherLookup",
    "FlashTextLookup",
    "DomainMatcher",
    # String similarity
    "token_set_ratio",
    "partial_ratio",
    "levenshtein_similarity",
    "jaro_winkler_similarity",
    "combined_fuzzy_score",
    "quick_fuzzy_score",
    # Acronym
    "is_acronym_match",
    "check_token_containment",
    "acronym_score",
    "quick_acronym_check",
    # Semantic
    "EmbeddingModel",
    "cosine_similarity",
    "batch_cosine_similarity",
    "semantic_similarity_score",
    # Contextual
    "recency_boost",
    "domain_consistency_boost",
    "shared_context_boost",
    # Status flags
    "SEMANTIC_AVAILABLE",
]
