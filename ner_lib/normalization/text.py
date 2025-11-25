"""Text normalization utilities."""

import re
import string
from typing import List


def normalize_entity_name(text: str, config=None) -> str:
    """
    Normalize an entity name for matching.
    
    Args:
        text: Input text to normalize
        config: Optional NormalizationConfig (uses defaults if None)
    
    Returns:
        Normalized text
    
    Citation: Custom implementation
    """
    if not text:
        return ""
    
    # Get config or use defaults
    if config is None:
        from ner_lib.config import DEFAULT_CONFIG
        config = DEFAULT_CONFIG.normalization
    
    result = text
    
    # Strip legal suffixes
    result = strip_legal_suffixes(result, config.legal_suffixes)
    
    # Lowercase
    if config.lowercase:
        result = result.lower()
    
    # Strip punctuation
    if config.strip_punctuation:
        # Keep spaces and alphanumeric
        result = re.sub(r'[^\w\s]', ' ', result)
    
    # Collapse whitespace
    if config.collapse_whitespace:
        result = collapse_whitespace(result)
    
    return result.strip()


def strip_legal_suffixes(text: str, suffixes: List[str]) -> str:
    """
    Remove common legal suffixes from entity names.
    
    Args:
        text: Input text
        suffixes: List of suffixes to remove (case-insensitive)
    
    Returns:
        Text with suffixes removed
    """
    # Create pattern that matches suffixes at end of string
    # Match with optional punctuation and whitespace before
    for suffix in suffixes:
        # Match suffix at end, potentially with comma, period, spaces
        pattern = r'\s*[,.]?\s*\b' + re.escape(suffix) + r'\b\.?\s*$'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text


def collapse_whitespace(text: str) -> str:
    """
    Collapse multiple whitespace characters into single space.
    
    Args:
        text: Input text
    
    Returns:
        Text with normalized whitespace
    """
    return re.sub(r'\s+', ' ', text)


def create_acronym(text: str) -> str:
    """
    Create an acronym from entity name.
    
    Takes first letter of each word (ignoring common stop words).
    
    Args:
        text: Input text
    
    Returns:
        Acronym (uppercase)
    
    Example:
        "International Business Machines" -> "IBM"
        "The United States of America" -> "USA"
    """
    # Common stop words to ignore
    stop_words = {'the', 'of', 'and', 'a', 'an', 'in', 'on', 'at', 'to', 'for'}
    
    # Split into words and filter
    words = text.lower().split()
    words = [w for w in words if w not in stop_words and w.isalpha()]
    
    # Take first letter of each word
    acronym = ''.join(w[0] for w in words if w)
    
    return acronym.upper()


def get_tokens(text: str) -> List[str]:
    """
    Extract tokens from text.
    
    Args:
        text: Input text
    
    Returns:
        List of lowercase tokens
    """
    # Remove punctuation and split
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    return [t for t in text.split() if t]


def token_containment(text1: str, text2: str) -> bool:
    """
    Check if tokens of one text are fully contained in the other.
    
    Args:
        text1: First text
        text2: Second text
    
    Returns:
        True if one text's tokens are subset of the other
    """
    tokens1 = set(get_tokens(text1))
    tokens2 = set(get_tokens(text2))
    
    if not tokens1 or not tokens2:
        return False
    
    return tokens1.issubset(tokens2) or tokens2.issubset(tokens1)
