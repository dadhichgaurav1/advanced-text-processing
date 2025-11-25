"""Canonicalization module for NER library."""

from ner_lib.canonicalization.entity_canonicalization import canonicalize_entity
from ner_lib.canonicalization.relationship_canonicalization import canonicalize_relationship
from ner_lib.canonicalization.property_canonicalization import (
    canonicalize_property_name,
    canonicalize_property_value
)

__all__ = [
    "canonicalize_entity",
    "canonicalize_relationship",
    "canonicalize_property_name",
    "canonicalize_property_value"
]
