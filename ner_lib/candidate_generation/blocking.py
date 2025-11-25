"""Blocking strategies for candidate generation."""

from typing import Dict, List, Set
from collections import defaultdict
from ner_lib.normalization.text import normalize_entity_name, get_tokens


class PrefixBlocker:
    """Block candidates by prefix matching."""
    
    def __init__(self, prefix_len: int = 3):
        """
        Initialize prefix blocker.
        
        Args:
            prefix_len: Length of prefix to use
        """
        self.prefix_len = prefix_len
        self.prefix_map: Dict[str, Set[str]] = defaultdict(set)  # prefix -> entity_ids
    
    def add_entity(self, entity_id: str, canonical_name: str, aliases: List[str] = None):
        """
        Add entity to prefix index.
        
        Args:
            entity_id: Entity ID
            canonical_name: Canonical name
            aliases: Optional aliases
        """
        # Add canonical name
        normalized = normalize_entity_name(canonical_name)
        if len(normalized) >= self.prefix_len:
            prefix = normalized[:self.prefix_len]
            self.prefix_map[prefix].add(entity_id)
        
        # Add aliases
        if aliases:
            for alias in aliases:
                normalized_alias = normalize_entity_name(alias)
                if len(normalized_alias) >= self.prefix_len:
                    prefix = normalized_alias[:self.prefix_len]
                    self.prefix_map[prefix].add(entity_id)
    
    def get_candidates(self, mention: str) -> List[str]:
        """
        Get candidate entity IDs by prefix matching.
        
        Args:
            mention: Mention text
        
        Returns:
            List of candidate entity IDs
        """
        normalized = normalize_entity_name(mention)
        
        if len(normalized) < self.prefix_len:
            return []
        
        prefix = normalized[:self.prefix_len]
        candidate_ids = self.prefix_map.get(prefix, set())
        
        return list(candidate_ids)


class TokenBlocker:
    """Block candidates by shared tokens."""
    
    def __init__(self, min_shared_tokens: int = 1):
        """
        Initialize token blocker.
        
        Args:
            min_shared_tokens: Minimum number of shared tokens required
        """
        self.min_shared_tokens = min_shared_tokens
        self.token_map: Dict[str, Set[str]] = defaultdict(set)  # token -> entity_ids
    
    def add_entity(self, entity_id: str, canonical_name: str, aliases: List[str] = None):
        """
        Add entity to token index.
        
        Args:
            entity_id: Entity ID
            canonical_name: Canonical name  
            aliases: Optional aliases
        """
        # Add canonical name tokens
        tokens = get_tokens(canonical_name)
        for token in tokens:
            if len(token) >= 2:  # Skip very short tokens
                self.token_map[token].add(entity_id)
        
        # Add alias tokens
        if aliases:
            for alias in aliases:
                tokens = get_tokens(alias)
                for token in tokens:
                    if len(token) >= 2:
                        self.token_map[token].add(entity_id)
    
    def get_candidates(self, mention: str) -> List[str]:
        """
        Get candidate entity IDs by shared tokens.
        
        Args:
            mention: Mention text
        
        Returns:
            List of candidate entity IDs
        """
        tokens = get_tokens(mention)
        
        if not tokens:
            return []
        
        # Count entity IDs by shared tokens
        entity_token_counts: Dict[str, int] = defaultdict(int)
        
        for token in tokens:
            if token in self.token_map:
                for entity_id in self.token_map[token]:
                    entity_token_counts[entity_id] += 1
        
        # Filter by minimum shared tokens
        candidates = [
            entity_id for entity_id, count in entity_token_counts.items()
            if count >= self.min_shared_tokens
        ]
        
        return candidates


class CombinedBlocker:
    """Combine multiple blocking strategies."""
    
    def __init__(self, prefix_len: int = 3, min_shared_tokens: int = 1):
        """
        Initialize combined blocker.
        
        Args:
            prefix_len: Prefix length for PrefixBlocker
            min_shared_tokens: Min shared tokens for TokenBlocker
        """
        self.prefix_blocker = PrefixBlocker(prefix_len)
        self.token_blocker = TokenBlocker(min_shared_tokens)
    
    def add_entity(self, entity_id: str, canonical_name: str, aliases: List[str] = None):
        """Add entity to all blockers."""
        self.prefix_blocker.add_entity(entity_id, canonical_name, aliases)
        self.token_blocker.add_entity(entity_id, canonical_name, aliases)
    
    def get_candidates(self, mention: str) -> List[str]:
        """
        Get union of candidates from all blockers.
        
        Args:
            mention: Mention text
        
        Returns:
            Deduplicated list of candidate entity IDs
        """
        prefix_candidates = set(self.prefix_blocker.get_candidates(mention))
        token_candidates = set(self.token_blocker.get_candidates(mention))
        
        # Union
        all_candidates = prefix_candidates | token_candidates
        
        return list(all_candidates)
