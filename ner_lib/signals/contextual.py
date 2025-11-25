"""Contextual signals (recency, shared neighbors, domain consistency)."""

from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

from ner_lib.models.candidate import Citation
from ner_lib.models.entity import Entity


def recency_boost(
    entity: Entity,
    current_time: Optional[datetime] = None,
    recency_window_days: int = 30,
    max_boost: float = 0.15
) -> float:
    """
    Boost score if entity was seen recently.
    
    Args:
        entity: Entity to check
        current_time: Current time (defaults to now)
        recency_window_days: Window in days for recency
        max_boost: Maximum boost to apply
    
    Returns:
        Boost score 0-max_boost
    """
    if entity.last_seen is None:
        return 0.0
    
    if current_time is None:
        current_time = datetime.now()
    
    # Calculate time since last seen
    time_delta = current_time - entity.last_seen
    
    # Apply exponential decay
    if time_delta.days <= recency_window_days:
        # More recent = higher boost
        decay_factor = 1.0 - (time_delta.days / recency_window_days)
        boost = max_boost * decay_factor
        return boost
    
    return 0.0


def domain_consistency_boost(
    mention_metadata: Dict,
    entity_metadata: Dict,
    boost_value: float = 0.2
) -> Tuple[float, Optional[Citation]]:
    """
    Boost if domain/website/email matches.
    
    Args:
        mention_metadata: Mention metadata
        entity_metadata: Entity metadata
        boost_value: Boost to apply on match
    
    Returns:
        Tuple of (boost, citation)
    """
    # Check domain match
    mention_domain = mention_metadata.get('domain', '').lower()
    entity_domain = entity_metadata.get('domain', '').lower()
    
    if mention_domain and entity_domain and mention_domain == entity_domain:
        citation = Citation(
            source="Custom",
            method="domain_match",
            component="contextual",
            confidence_contribution=boost_value
        )
        return boost_value, citation
    
    # Check email domain match
    mention_email = mention_metadata.get('email', '')
    entity_email = entity_metadata.get('email', '')
    
    if mention_email and entity_email:
        if '@' in mention_email and '@' in entity_email:
            mention_email_domain = mention_email.split('@')[1].lower()
            entity_email_domain = entity_email.split('@')[1].lower()
            
            if mention_email_domain == entity_email_domain:
                citation = Citation(
                    source="Custom",
                    method="email_domain_match",
                    component="contextual",
                    confidence_contribution=boost_value
                )
                return boost_value, citation
    
    return 0.0, None


def shared_context_boost(
    mention_metadata: Dict,
    entity_metadata: Dict,
    boost_value: float = 0.1
) -> float:
    """
    Boost if entities share contextual information.
    
    Examples: same industry, same location, same category
    
    Args:
        mention_metadata: Mention metadata
        entity_metadata: Entity metadata
        boost_value: Boost per matching field
    
    Returns:
        Total boost
    """
    boost = 0.0
    shared_fields = ['industry', 'location', 'category', 'type']
    
    for field in shared_fields:
        mention_value = mention_metadata.get(field, '').lower()
        entity_value = entity_metadata.get(field, '').lower()
        
        if mention_value and entity_value and mention_value == entity_value:
            boost += boost_value
    
    return min(boost, boost_value * 2)  # Cap at 2x boost
