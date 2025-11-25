"""Storage interface and in-memory implementation."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from ner_lib.models.entity import Entity, Alias, Mention
from ner_lib.models.candidate import SameCandidate


class StorageBackend(ABC):
    """Abstract storage interface for entities and candidates."""
    
    @abstractmethod
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    def get_all_entities(self) -> List[Entity]:
        """Get all entities."""
        pass
    
    @abstractmethod
    def create_entity(self, entity: Entity) -> str:
        """Create new entity, return ID."""
        pass
    
    @abstractmethod
    def update_entity(self, entity: Entity):
        """Update existing entity."""
        pass
    
    @abstractmethod
    def delete_entity(self, entity_id: str):
        """Delete entity."""
        pass
    
    @abstractmethod
    def get_aliases(self, entity_id: str) -> List[Alias]:
        """Get all aliases for an entity."""
        pass
    
    @abstractmethod
    def add_alias(self, alias: Alias):
        """Add alias for an entity."""
        pass
    
    @abstractmethod
    def get_entity_by_alias(self, alias_name: str) -> Optional[Entity]:
        """Find entity by alias name."""
        pass
    
    @abstractmethod
    def save_review_item(self, review_item: SameCandidate):
        """Save item to review queue."""
        pass
    
    @abstractmethod
    def get_review_queue(self, status: str = "pending") -> List[SameCandidate]:
        """Get review queue items by status."""
        pass
