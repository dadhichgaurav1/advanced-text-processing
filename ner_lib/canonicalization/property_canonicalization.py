"""Canonicalization for property names and values."""

from typing import Dict, Optional
import logging
from ner_lib.config import DEFAULT_CONFIG
from ner_lib.aliases.alias_retrieval import get_aliases
from ner_lib.utils.nlp import get_spacy_model

logger = logging.getLogger(__name__)

# Global semantic matcher instances (lazy loaded)
_relationship_matcher = None
_property_matcher = None


def canonicalize_property_name(
    property_name: str,
    config: Optional[Dict] = None
) -> Dict:
    """
    Canonicalize a property name using syntax-aware parsing (noun chunks).
    
    Process:
    1. Parse using spaCy
    2. Identify noun chunks (e.g., "date of birth")
    3. Normalize to snake_case (e.g., "date_of_birth")
    4. Get synonyms for the canonical form or head noun
    
    Args:
        property_name: Property name (e.g., "date of birth", "first name")
        config: Optional configuration override
    
    Returns:
        Dictionary containing canonical form and metadata.
    """
    return _canonicalize_noun_phrase(property_name, "property-name", config)


def canonicalize_property_value(
    property_value: str,
    config: Optional[Dict] = None
) -> Dict:
    """
    Canonicalize a property value using syntax-aware parsing.
    
    Process:
    1. Parse using spaCy
    2. Identify noun chunks
    3. Normalize to snake_case
    4. Get synonyms for the canonical form or head noun
    
    Args:
        property_value: Property value (e.g., "United States", "blue cars")
        config: Optional configuration override
    
    Returns:
        Dictionary containing canonical form and metadata.
    """
    return _canonicalize_noun_phrase(property_value, "property-value", config)


def _canonicalize_noun_phrase(
    text: str,
    input_type: str,
    config: Optional[Dict] = None
) -> Dict:
    """Shared logic for noun phrase canonicalization."""
    
    # Use default config if not provided
    if config is None:
        config = DEFAULT_CONFIG
    
    # Check if semantic matching is enabled
    use_semantic = (config.semantic_matching.enabled and 
                    config.semantic_matching.canonical_properties)
        
    try:
        nlp = get_spacy_model()
        doc = nlp(text)
        
        # Step 1: Identify best noun chunk or use subtree of root noun
        root = None
        for token in doc:
            if token.dep_ == "ROOT":
                root = token
                break
        
        # If root is a noun/propn, use its subtree to capture full phrase
        if root and root.pos_ in ("NOUN", "PROPN"):
            # Take the subtree of the root noun
            subtree_tokens = list(root.subtree)
            subtree_tokens.sort(key=lambda t: t.i)
            canonical_text = " ".join([t.text for t in subtree_tokens])
            head_token = root
        else:
            # Fallback: try to find a noun chunk
            chosen_chunk = None
            if root:
                for chunk in doc.noun_chunks:
                    if root in chunk:
                        chosen_chunk = chunk
                        break
            
            # Or use longest chunk
            if not chosen_chunk and list(doc.noun_chunks):
                chosen_chunk = max(doc.noun_chunks, key=lambda c: len(c.text))
                
            if chosen_chunk:
                canonical_text = chosen_chunk.text
                head_token = chosen_chunk.root
            else:
                # Last resort: use whole text
                canonical_text = text
                head_token = root if root else doc[0]
            
        # Step 2: Normalize to snake_case
        canonical_name = canonical_text.lower().strip().replace(" ", "_")
        
        # Step 2.5: Try semantic matching if enabled
        if use_semantic:
            semantic_match = _get_semantic_match(
                canonical_name,
                "property",
                config
            )
            if semantic_match:
                # Found a semantic match - use it as canonical
                logger.debug(f"Semantic match: '{canonical_name}' -> '{semantic_match}'")
                canonical_name = semantic_match
        
        # Step 3: Get synonyms
        lemma = head_token.lemma_.lower() if head_token else canonical_name
        pos_tag = head_token.pos_ if head_token else "UNKNOWN"
        
        # Try canonical name first (e.g. date_of_birth, first_name)
        synonym_result = get_aliases(
            input_text=canonical_name,
            input_type=input_type,
            config=config
        )
        aliases = synonym_result.get("aliases", [])
        
        # If no synonyms found for multi-word phrase, try lemma
        # We avoid fallback for multi-word to prevent bad matches (e.g. "date" for "date of birth")
        if not aliases and "_" not in canonical_name:
            synonym_result = get_aliases(
                input_text=lemma,
                input_type=input_type,
                config=config
            )
            aliases = synonym_result.get("aliases", [])
             
        aliases = aliases[:5]
        
        return {
            "canonical_name": canonical_name,
            "lemma": lemma,
            "aliases": aliases,
            "original_text": text,
            "pos_tag": pos_tag,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error canonicalizing {input_type} '{text}': {e}")
        return {
            "canonical_name": text,
            "lemma": text,
            "aliases": [],
            "original_text": text,
            "pos_tag": "UNKNOWN",
            "success": False,
            "error": str(e)
        }


def _get_semantic_match(text: str, match_type: str, config) -> Optional[str]:
    """
    Get semantic match for text using embeddings.
    
    Args:
        text: Text to match
        match_type: Type of match ('relationship' or 'property')
        config: Configuration object
        
    Returns:
        Best matching canonical term, or None
    """
    global _relationship_matcher, _property_matcher
    
    try:
        # Determine which canonical terms and matcher to use
        if match_type == "relationship":
            canonical_terms = config.semantic_matching.canonical_relationships
            matcher = _relationship_matcher
        else:
            canonical_terms = config.semantic_matching.canonical_properties
            matcher = _property_matcher
        
        if not canonical_terms:
            return None
        
        # Lazy load semantic matcher if not initialized
        if matcher is None:
            from ner_lib.canonicalization.semantic_matcher import SemanticMatcher
            
            matcher = SemanticMatcher(
                canonical_terms=canonical_terms,
                model_name=config.semantic_matching.model_name,
                similarity_threshold=config.semantic_matching.similarity_threshold,
                cache_embeddings=config.semantic_matching.cache_embeddings
            )
            
            # Store in global variable
            if match_type == "relationship":
                _relationship_matcher = matcher
            else:
                _property_matcher = matcher
        
        # Find best match
        return matcher.find_best_match(text)
        
    except Exception as e:
        logger.error(f"Error in semantic matching: {e}")
        return None

