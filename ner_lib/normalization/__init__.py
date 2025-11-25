"""Normalization package."""

from ner_lib.normalization.text import (
    normalize_entity_name,
    strip_legal_suffixes,
    collapse_whitespace,
    create_acronym,
    get_tokens,
    token_containment,
)

__all__ = [
    "normalize_entity_name",
    "strip_legal_suffixes",
    "collapse_whitespace",
    "create_acronym",
    "get_tokens",
    "token_containment",
]
