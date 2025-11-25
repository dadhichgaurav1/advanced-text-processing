"""String similarity signals using RapidFuzz and jellyfish."""

from typing import Dict
from rapidfuzz import fuzz
from rapidfuzz.distance import Levenshtein, JaroWinkler

from ner_lib.models.candidate import Citation


def token_set_ratio(text1: str, text2: str) -> float:
    """
    Compute token set ratio using RapidFuzz.
    
    Ignores word order and duplicates.
    
    Args:
        text1: First text
        text2: Second text
    
    Returns:
        Similarity score 0-1
    
    Citation: RapidFuzz
    """
    score = fuzz.token_set_ratio(text1, text2)
    return score / 100.0  # Normalize to 0-1


def partial_ratio(text1: str, text2: str) -> float:
    """
    Compute partial ratio using RapidFuzz.
    
    Finds best matching substring.
    
    Args:
        text1: First text
        text2: Second text
    
    Returns:
        Similarity score 0-1
    
    Citation: RapidFuzz
    """
    score = fuzz.partial_ratio(text1, text2)
    return score / 100.0


def levenshtein_similarity(text1: str, text2: str) -> float:
    """
    Compute normalized Levenshtein similarity.
    
    Args:
        text1: First text
        text2: Second text
    
    Returns:
        Similarity score 0-1
    
    Citation: RapidFuzz (Levenshtein)
    """
    if not text1 or not text2:
        return 0.0
    
    distance = Levenshtein.distance(text1, text2)
    max_len = max(len(text1), len(text2))
    
    if max_len == 0:
        return 1.0
    
    return 1.0 - (distance / max_len)


def jaro_winkler_similarity(text1: str, text2: str) -> float:
    """
    Compute Jaro-Winkler similarity.
    
    Gives more weight to common prefixes.
    
    Args:
        text1: First text
        text2: Second text
    
    Returns:
        Similarity score 0-1
    
    Citation: RapidFuzz (JaroWinkler)
    """
    if not text1 or not text2:
        return 0.0
    
    return JaroWinkler.similarity(text1, text2) / 100.0


def combined_fuzzy_score(
    text1: str,
    text2: str,
    weights: Dict[str, float] = None
) -> tuple[float, list[Citation]]:
    """
    Compute combined fuzzy similarity score.
    
    Args:
        text1: First text
        text2: Second text
        weights: Optional weights for each metric
    
    Returns:
        Tuple of (combined_score, citations)
    """
    if weights is None:
        weights = {
            'token_set': 0.4,
            'partial': 0.2,
            'levenshtein': 0.2,
            'jaro_winkler': 0.2,
        }
    
    citations = []
    
    # Compute individual scores
    token_set_score = token_set_ratio(text1, text2)
    partial_score = partial_ratio(text1, text2)
    lev_score = levenshtein_similarity(text1, text2)
    jw_score = jaro_winkler_similarity(text1, text2)
    
    # Create citations
    citations.append(Citation(
        source="RapidFuzz",
        method="token_set_ratio",
        component="fuzzy_matching",
        confidence_contribution=token_set_score * weights['token_set']
    ))
    
    citations.append(Citation(
        source="RapidFuzz",
        method="partial_ratio",
        component="fuzzy_matching",
        confidence_contribution=partial_score * weights['partial']
    ))
    
    citations.append(Citation(
        source="RapidFuzz",
        method="levenshtein_similarity",
        component="fuzzy_matching",
        confidence_contribution=lev_score * weights['levenshtein']
    ))
    
    citations.append(Citation(
        source="RapidFuzz",
        method="jaro_winkler",
        component="fuzzy_matching",
        confidence_contribution=jw_score * weights['jaro_winkler']
    ))
    
    # Weighted combination
    combined = (
        token_set_score * weights['token_set'] +
        partial_score * weights['partial'] +
        lev_score * weights['levenshtein'] +
        jw_score * weights['jaro_winkler']
    )
    
    return combined, citations


def quick_fuzzy_score(text1: str, text2: str) -> float:
    """
    Quick fuzzy score using just token_set_ratio.
    
    Fast for Mode A early stopping.
    
    Args:
        text1: First text
        text2: Second text
    
    Returns:
        Similarity score 0-1
    """
    return token_set_ratio(text1, text2)
