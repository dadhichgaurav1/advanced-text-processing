"""In-memory storage implementation."""

from typing import Dict, List, Optional
from ner_lib.storage.interface import StorageBackend
from ner_lib.models.entity import Entity, Alias, Mention
from ner_lib.models.candidate import SameCandidate
from ner_lib.normalization.text import normalize_entity_name


class MemoryStorage(StorageBackend):
    """In-memory storage using Python dictionaries."""
    
    def __init__(self):
        """Initialize storage."""
        self.entities: Dict[str, Entity] = {}
        self.aliases: Dict[str, List[Alias]] = {}  # entity_id -> List[Alias]
        self.alias_map: Dict[str, str] = {}  # normalized_alias -> entity_id
        self.review_queue: List[SameCandidate] = []
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID."""
        return self.entities.get(entity_id)
    
    def get_all_entities(self) -> List[Entity]:
        """Get all entities."""
        return list(self.entities.values())
    
    def create_entity(self, entity: Entity) -> str:
        """Create new entity."""
        self.entities[entity.id] = entity
        
        # Add to alias map
        normalized = normalize_entity_name(entity.canonical_name)
        self.alias_map[normalized] = entity.id
        
        # Add provided aliases
        if entity.aliases:
            for alias_text in entity.aliases:
                alias = Alias(
                    name=alias_text,
                    entity_id=entity.id,
                    source="initial"
                )
                self.add_alias(alias)
        
        return entity.id
    
    def update_entity(self, entity: Entity):
        """Update existing entity."""
        if entity.id in self.entities:
            self.entities[entity.id] = entity
        else:
            raise ValueError(f"Entity {entity.id} not found")
    
    def delete_entity(self, entity_id: str):
        """Delete entity."""
        if entity_id in self.entities:
            del self.entities[entity_id]
            
            # Remove from alias map
            self.alias_map = {
                k: v for k, v in self.alias_map.items()
                if v != entity_id
            }
            
            # Remove aliases
            if entity_id in self.aliases:
                del self.aliases[entity_id]
    
    def get_aliases(self, entity_id: str) -> List[Alias]:
        """Get all aliases for an entity."""
        return self.aliases.get(entity_id, [])
    
    def add_alias(self, alias: Alias):
        """Add alias for an entity."""
        if alias.entity_id not in self.entities:
            raise ValueError(f"Entity {alias.entity_id} not found")
        
        # Add to aliases list
        if alias.entity_id not in self.aliases:
            self.aliases[alias.entity_id] = []
        
        self.aliases[alias.entity_id].append(alias)
        
        # Add to alias map
        normalized = normalize_entity_name(alias.name)
        self.alias_map[normalized] = alias.entity_id
    
    def get_entity_by_alias(self, alias_name: str) -> Optional[Entity]:
        """Find entity by alias name."""
        normalized = normalize_entity_name(alias_name)
        entity_id = self.alias_map.get(normalized)
        
        if entity_id:
            return self.entities.get(entity_id)
        
        return None
    
    def save_review_item(self, review_item: SameCandidate):
        """Save item to review queue."""
        self.review_queue.append(review_item)
    
    def get_review_queue(self, status: str = "pending") -> List[SameCandidate]:
        """Get review queue items by status."""
        return [item for item in self.review_queue if item.status == status]
    
    def clear(self):
        """Clear all data (useful for testing)."""
        self.entities.clear()
        self.aliases.clear()
        self.alias_map.clear()
        self.review_queue.clear()
