"""Acronym detection and token containment."""

from typing import Optional, Tuple
from ner_lib.normalization.text import create_acronym, token_containment, get_tokens
from ner_lib.models.candidate import Citation


def is_acronym_match(mention: str, canonical_name: str) -> bool:
    """
    Check if mention is an acronym of the canonical name.
    
    Args:
        mention: Mention text (potentially an acronym)
        canonical_name: Canonical entity name
    
    Returns:
        True if mention matches acronym of canonical name
    
    Example:
        is_acronym_match("IBM", "International Business Machines") -> True
    """
    # Generate acronym from canonical name
    acronym = create_acronym(canonical_name)
    
    # Check if mention (uppercased) matches acronym
    mention_upper = mention.upper().strip()
    
    return mention_upper == acronym


def check_token_containment(text1: str, text2: str) -> bool:
    """
    Check if tokens of one text are contained in the other.
    
    Args:
        text1: First text
        text2: Second text
    
    Returns:
        True if one text's tokens are subset of the other
    
    Example:
        check_token_containment("maximem", "maximem ai") -> True
    """
    return token_containment(text1, text2)


def acronym_score(
    mention: str,
    canonical_name: str,
    threshold: float = 0.5
) -> Tuple[float, Optional[Citation]]:
    """
    Compute acronym/containment score.
    
    Returns high score if:
    - Mention is acronym of canonical name
    - Token containment exists
    
    Args:
        mention: Mention text
        canonical_name: Canonical entity name
        threshold: Minimum threshold for positive match
    
    Returns:
        Tuple of (score, citation)
    """
    score = 0.0
    reason = None
    
    # Check acronym match (highest confidence)
    if is_acronym_match(mention, canonical_name):
        score = 0.95
        reason = "acronym_match"
    
    # Check token containment
    elif check_token_containment(mention, canonical_name):
        # Calculate how much overlap
        tokens1 = set(get_tokens(mention))
        tokens2 = set(get_tokens(canonical_name))
        
        if tokens1.issubset(tokens2):
            # Mention tokens all in canonical
            score = 0.85
            reason = "token_subset"
        elif tokens2.issubset(tokens1):
            # Canonical tokens all in mention
            score = 0.80
            reason = "token_superset"
    
    # Check partial acronym (first letters match some words)
    elif len(mention.strip()) >= 2:
        mention_clean = mention.upper().strip().replace(' ', '')
        canonical_words = [w for w in canonical_name.split() if w.isalpha()]
        
        if len(canonical_words) >= len(mention_clean):
            # Check if mention letters match first letters of consecutive words
            matches = 0
            for i, char in enumerate(mention_clean):
                if i < len(canonical_words) and canonical_words[i][0].upper() == char:
                    matches += 1
            
            if matches == len(mention_clean) and matches >= 2:
                score = 0.70
                reason = "partial_acronym"
    
    # Create citation if score above threshold
    citation = None
    if score >= threshold:
        citation = Citation(
            source="Custom",
            method=reason or "acronym_detection",
            component="acronym",
            confidence_contribution=score
        )
    
    return score, citation


def quick_acronym_check(mention: str, canonical_name: str, threshold: float = 0.9) -> bool:
    """
    Quick check for high-confidence acronym match (for Mode A early stopping).
    
    Args:
        mention: Mention text
        canonical_name: Canonical entity name
        threshold: High confidence threshold
    
    Returns:
        True if high confidence match
    """
    score, _ = acronym_score(mention, canonical_name)
    return score >= threshold
