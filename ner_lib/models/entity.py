"""Data models for entities and aliases."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import uuid


@dataclass
class Entity:
    """Represents a canonical entity."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    canonical_name: str = ""
    normalized_name: str = ""
    aliases: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_seen: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate and normalize."""
        if not self.canonical_name:
            raise ValueError("canonical_name is required")
        
        # Auto-generate normalized_name if not provided
        if not self.normalized_name:
            from ner_lib.normalization.text import normalize_entity_name
            self.normalized_name = normalize_entity_name(self.canonical_name)


@dataclass
class Alias:
    """Represents an alias for an entity."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    normalized_name: str = ""
    entity_id: str = ""
    confidence: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)
    source: str = "manual"  # manual, matched, imported
    
    def __post_init__(self):
        """Validate."""
        if not self.name:
            raise ValueError("name is required")
        if not self.entity_id:
            raise ValueError("entity_id is required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        
        # Auto-generate normalized_name if not provided
        if not self.normalized_name:
            from ner_lib.normalization.text import normalize_entity_name
            self.normalized_name = normalize_entity_name(self.name)


@dataclass
class Mention:
    """Represents an incoming entity mention to be resolved."""
    
    text: str
    context: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    normalized_text: str = field(default="", init=False)
    
    def __post_init__(self):
        """Normalize the mention text."""
        if not self.text:
            raise ValueError("text is required")
        
        from ner_lib.normalization.text import normalize_entity_name
        self.normalized_text = normalize_entity_name(self.text)
