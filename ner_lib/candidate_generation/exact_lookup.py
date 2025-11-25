"""Exact lookup for candidate generation."""

from typing import Dict, List, Optional, Set
from ner_lib.normalization.text import normalize_entity_name


class HashMapLookup:
    """Fast exact lookup using in-memory hashmap."""
    
    def __init__(self):
        """Initialize lookup."""
        self.name_to_ids: Dict[str, Set[str]] = {}  # normalized_name -> set of entity_ids
    
    def add_entity(self, entity_id: str, canonical_name: str, aliases: List[str] = None):
        """
        Add entity to lookup index.
        
        Args:
            entity_id: Entity ID
            canonical_name: Canonical name
            aliases: Optional list of aliases
        """
        # Add canonical name
        normalized = normalize_entity_name(canonical_name)
        if normalized not in self.name_to_ids:
            self.name_to_ids[normalized] = set()
        self.name_to_ids[normalized].add(entity_id)
        
        # Add aliases
        if aliases:
            for alias in aliases:
                normalized_alias = normalize_entity_name(alias)
                if normalized_alias not in self.name_to_ids:
                    self.name_to_ids[normalized_alias] = set()
                self.name_to_ids[normalized_alias].add(entity_id)
    
    def lookup(self, mention: str) -> Optional[List[str]]:
        """
        Lookup entity IDs by mention.
        
        Args:
            mention: Mention text
        
        Returns:
            List of matching entity IDs, or None if no match
        """
        normalized = normalize_entity_name(mention)
        entity_ids = self.name_to_ids.get(normalized)
        
        if entity_ids:
            return list(entity_ids)
        
        return None
    
    def clear(self):
        """Clear all data."""
        self.name_to_ids.clear()
