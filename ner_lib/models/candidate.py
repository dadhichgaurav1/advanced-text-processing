"""Data models for candidates and match results."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

from ner_lib.models.entity import Entity, Mention


class NextSteps(Enum):
    """Next steps after resolution."""
    NONE = "none"  # High confidence match found
    HUMAN_REVIEW = "human_review"  # Low confidence, needs review
    NEW_ENTITY = "new_entity"  # No match, create as new entity


@dataclass
class Citation:
    """Citation for a signal or method used."""
    
    source: str  # Library name (e.g., "spaCy", "RapidFuzz")
    method: str  # Method name (e.g., "PhraseMatcher", "token_set_ratio")
    component: str  # Component name (e.g., "exact_lookup", "fuzzy_matching")
    confidence_contribution: float = 0.0  # How much this contributed to final score


@dataclass
class Candidate:
    """Represents a candidate match for an entity mention."""
    
    entity_id: str
    entity: Optional[Entity] = None
    signals: Dict[str, float] = field(default_factory=dict)
    final_score: float = 0.0
    citations: List[Citation] = field(default_factory=list)
    
    def add_signal(self, signal_name: str, score: float, citation: Optional[Citation] = None):
        """Add a signal score."""
        self.signals[signal_name] = score
        if citation:
            citation.confidence_contribution = score
            self.citations.append(citation)


@dataclass
class MatchResult:
    """Result of entity resolution."""
    
    mention: Mention
    matched_entity: Optional[Entity] = None
    confidence: float = 0.0
    citations: List[Citation] = field(default_factory=list)
    next_steps: NextSteps = NextSteps.NONE
    candidates: List[Candidate] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Determine next steps based on confidence and matched entity."""
        if self.matched_entity and self.confidence >= 0.7:
            self.next_steps = NextSteps.NONE
        elif self.matched_entity and self.confidence >= 0.45:
            self.next_steps = NextSteps.HUMAN_REVIEW
        elif not self.matched_entity:
            self.next_steps = NextSteps.NEW_ENTITY


@dataclass
class SameCandidate:
    """Represents a potential match that needs human review."""
    
    mention: Mention
    candidates: List[Candidate]
    status: str = "pending"  # pending, approved, rejected
    reviewed_at: Optional[str] = None
    reviewed_by: Optional[str] = None
    final_entity_id: Optional[str] = None
