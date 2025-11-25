"""Named entity canonicalization integrating with Mode A/B resolvers."""

from typing import Dict, List, Optional
import logging
import re
from ner_lib.normalization.text import normalize_entity_name
from ner_lib.aliases.alias_retrieval import get_aliases
from ner_lib.config import DEFAULT_CONFIG

logger = logging.getLogger(__name__)


def canonicalize_entity(
    entity: str,
    mode: str = "progressive",
    entity_type: Optional[str] = None,
    description: Optional[str] = None,
    aliases: Optional[List[str]] = None,
    config: Optional[Dict] = None
) -> Dict:
    """
    Canonicalize a named entity using Mode A (progressive) or Mode B (complete).
    
    Args:
        entity: Entity name to canonicalize
        mode: "progressive" (Mode A) or "complete" (Mode B)
        entity_type: Optional entity type (PERSON, ORG, GPE, etc.)
        description: Optional entity description
        aliases: Optional list of known aliases (if None, will fetch from Wikidata)
        config: Optional configuration override
    
    Returns:
        Dictionary containing:
        - canonical_name: Canonicalized entity name
        - normalized_name: Normalized form (lowercase, no punctuation)
        - aliases: List of aliases
        - entity_type: Entity type (if provided)
        - confidence: Confidence score from resolver
        - matched_entity: Full entity object if found in knowledge base
        - resolution_mode: Mode used for resolution
    
    Example:
        >>> result = canonicalize_entity("apple inc", mode="progressive")
        >>> print(result['canonical_name'])
        "Apple Inc."
        >>> print(result['aliases'])
        ['Apple', 'AAPL', 'Apple Computer']
    """
    # Use default config if not provided
    if config is None:
        config = DEFAULT_CONFIG
    
    # Validate mode
    if mode not in ["progressive", "complete"]:
        return {
            "canonical_name": entity,
            "normalized_name": normalize_entity_name(entity),
            "aliases": aliases or [],
            "entity_type": entity_type,
            "confidence": 0.0,
            "matched_entity": None,
            "resolution_mode": mode,
            "success": False,
            "error": "Invalid mode. Must be 'progressive' or 'complete'"
        }
    
    try:
        # Step 1: Normalize the entity name
        # Strip leading/trailing spaces, underscores, convert to lowercase
        normalized = normalize_entity_name(entity)
        
        # Step 2: Get aliases if not provided
        entity_aliases = aliases
        if entity_aliases is None:
            logger.info(f"Fetching aliases for '{entity}' from Wikidata")
            alias_result = get_aliases(
                input_text=entity,
                input_type="named-entity",
                config=config
            )
            if alias_result["success"]:
                entity_aliases = alias_result.get("aliases", [])
                if not description and alias_result.get("description"):
                    description = alias_result["description"]
            else:
                entity_aliases = []
                logger.warning(f"Could not fetch aliases for '{entity}': {alias_result.get('error')}")
        
        # Step 3: Use EntityResolver for resolution  
        from ner_lib import EntityResolver
        from ner_lib.models.entity import Mention
        
        # Map mode to resolver mode
        resolver_mode = 'A' if mode == "progressive" else 'B'
        
        # Initialize resolver with appropriate mode
        resolver = EntityResolver(mode=resolver_mode, config=config)
        
        # Create mention object
        mention = Mention(
            text=entity,
            metadata={
                "entity_type": entity_type,
                "description": description
            } if entity_type or description else {}
        )
        
        # Resolve the entity
        result = resolver.resolve(mention)
        
        # Build response
        canonical_name = entity  # Default to original
        confidence = 0.0
        matched_entity = None
        
        if result.matched_entity:
            canonical_name = result.matched_entity.canonical_name
            confidence = result.confidence
            matched_entity = {
                "id": result.matched_entity.id,
                "canonical_name": result.matched_entity.canonical_name,
                "aliases": result.matched_entity.aliases,
                "metadata": result.matched_entity.metadata
            }
        
        return {
            "canonical_name": canonical_name,
            "normalized_name": normalized,
            "aliases": entity_aliases,
            "entity_type": entity_type,
            "description": description,
            "confidence": confidence,
            "matched_entity": matched_entity,
            "resolution_mode": mode,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error canonicalizing entity '{entity}': {e}")
        return {
            "canonical_name": entity,
            "normalized_name": normalize_entity_name(entity),
            "aliases": aliases or [],
            "entity_type": entity_type,
            "confidence": 0.0,
            "matched_entity": None,
            "resolution_mode": mode,
            "success": False,
            "error": str(e)
        }
