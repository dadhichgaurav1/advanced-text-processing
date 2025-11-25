"""Main alias retrieval function coordinating all sources."""

from typing import Dict, List, Optional
import logging
from ner_lib.config import DEFAULT_CONFIG
from ner_lib.aliases.wikidata_client import WikidataClient
from ner_lib.aliases.synonym_provider import SynonymProvider

logger = logging.getLogger(__name__)

# Global instances (lazy loaded)
_wikidata_client: Optional[WikidataClient] = None
_synonym_provider: Optional[SynonymProvider] = None


def get_aliases(
    input_text: str,
    input_type: str,
    properties: Optional[Dict] = None,
    config: Optional[Dict] = None
) -> Dict:
    """
    Get aliases for entities, relationships, or properties.
    
    Args:
        input_text: Text to get aliases for
        input_type: Type of input - one of:
            - "named-entity": Query Wikidata for entity aliases
            - "relationship": Get verb synonyms from WordNet
            - "property-name": Get noun synonyms from WordNet (e.g., "name", "preferences")
            - "property-value": Get noun synonyms from WordNet
        properties: Optional properties of the input (reserved for future use)
        config: Optional configuration override
    
    Returns:
        Dictionary containing:
        - aliases: List of aliases/synonyms
        - description: Short description (for named entities)
        - source: Source of aliases ("wikidata" or "wordnet")
        - success: Whether the operation was successful
    
    Example:
        >>> # Get aliases for a named entity
        >>> result = get_aliases("Apple Inc.", "named-entity")
        >>> print(result['aliases'])
        ['Apple', 'AAPL', 'Apple Computer']
        
        >>> # Get synonyms for a verb
        >>> result = get_aliases("running", "relationship")
        >>> print(result['aliases'])
        ['executing', 'operating', 'functioning', 'working']
    """
    global _wikidata_client, _synonym_provider
    
    # Use default config if not provided
    if config is None:
        config = DEFAULT_CONFIG
    
    # Validate input type
    valid_types = ["named-entity", "relationship", "property-name", "property-value"]
    if input_type not in valid_types:
        return {
            "aliases": [],
            "description": "",
            "source": "none",
            "success": False,
            "error": f"Invalid input_type. Must be one of: {valid_types}"
        }
    
    try:
        if input_type == "named-entity":
            # Initialize Wikidata client lazily
            if _wikidata_client is None:
                _wikidata_client = WikidataClient(
                    api_endpoint=config.wikidata.api_endpoint,
                    search_limit=config.wikidata.search_limit,
                    requests_per_minute=config.wikidata.requests_per_minute,
                    cache_ttl_seconds=config.wikidata.cache_ttl_seconds,
                    cache_maxsize=config.wikidata.cache_maxsize,
                    timeout_seconds=config.wikidata.timeout_seconds
                )
            
            # Get aliases from Wikidata
            result = _wikidata_client.get_aliases_for_entity(input_text)
            result["source"] = "wikidata"
            return result
            
        else:
            # Initialize synonym provider lazily
            if _synonym_provider is None:
                _synonym_provider = SynonymProvider(
                    use_spacy_wordnet=config.synonyms.use_spacy_wordnet,
                    use_nltk_fallback=config.synonyms.use_nltk_fallback,
                    filter_by_pos=config.synonyms.filter_by_pos
                )
            
            # Determine POS tag based on input type
            pos_tag_map = {
                "relationship": "VERB",
                "property-name": "NOUN",  # Changed from ADJ to NOUN
                "property-value": "NOUN"
            }
            pos_tag = pos_tag_map.get(input_type)
            
            # Get synonyms from WordNet
            synonyms = _synonym_provider.get_synonyms(
                word=input_text,
                pos_tag=pos_tag,
                max_synonyms=config.synonyms.max_synonyms
            )
            
            return {
                "aliases": synonyms,
                "description": f"Synonyms for {input_type.replace('-', ' ')}",
                "source": "wordnet",
                "success": True
            }
            
    except Exception as e:
        logger.error(f"Error getting aliases for '{input_text}' ({input_type}): {e}")
        return {
            "aliases": [],
            "description": "",
            "source": "none",
            "success": False,
            "error": str(e)
        }


def clear_caches():
    """Clear all caches for Wikidata and synonym providers."""
    global _wikidata_client, _synonym_provider
    
    if _wikidata_client:
        _wikidata_client.cache.clear()
        logger.info("Cleared Wikidata cache")
    
    # Synonym provider doesn't have a cache, but we can reinitialize
    _synonym_provider = None
    
    logger.info("Cleared all caches")
