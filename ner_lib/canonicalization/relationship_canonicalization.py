"""Canonicalization for relationships/verbs."""

from typing import Dict, Optional
import logging
from ner_lib.config import DEFAULT_CONFIG
from ner_lib.aliases.alias_retrieval import get_aliases
from ner_lib.utils.nlp import get_spacy_model

logger = logging.getLogger(__name__)

# Global semantic matcher instances (lazy loaded)
_relationship_matcher = None
_property_matcher = None


def canonicalize_relationship(
    relationship: str,
    config: Optional[Dict] = None
) -> Dict:
    """
    Canonicalize a relationship/verb using syntax-aware parsing.
    
    Process:
    1. Parse using spaCy dependency parser
    2. Identify root verb/auxiliary
    3. Collect particles and prepositions to form phrasal verbs (e.g., "rely on")
    4. Normalize to snake_case (e.g., "relies on" -> "rely_on")
    5. Get synonyms for the canonical form or root verb
    
    Args:
        relationship: Relationship text (e.g., "is running", "relies on")
        config: Optional configuration override
    
    Returns:
        Dictionary containing:
        - canonical_name: Canonical form (snake_case lemma)
        - lemma: Root verb lemma
        - aliases: List of inflected synonyms
        - original_text: Original input
        - pos_tag: POS tag of the root
        - tense_tag: Detailed tense tag
    """
    
    # Use default config if not provided
    if config is None:
        config = DEFAULT_CONFIG
    
    # Check if semantic matching is enabled
    use_semantic = (config.semantic_matching.enabled and 
                    config.semantic_matching.canonical_relationships)
    
    try:
        nlp = get_spacy_model()
        
        # Step 1: Tokenize and Parse
        doc = nlp(relationship)
        
        # Step 2: Find root verb or auxiliary
        # Priority: ROOT verb > First Verb > First Aux > ROOT
        root = None
        
        # Check if ROOT is a verb or aux
        for token in doc:
            if token.dep_ == "ROOT" and token.pos_ in ("VERB", "AUX"):
                root = token
                break
        
        # If ROOT isn't a verb/aux (e.g. "dependencies of"), look for any verb/aux
        if not root:
            for token in doc:
                if token.pos_ in ("VERB", "AUX"):
                    root = token
                    break
        
        # Fallback to ROOT regardless of POS if nothing else found
        if not root:
            for token in doc:
                if token.dep_ == "ROOT":
                    root = token
                    break
                    
        if not root:
            # Should rarely happen with spaCy
            return _error_result(relationship, "No root token found")

        # Step 3: Collect particles and prepositions
        # We want to capture "rely on", "give up", "account for"
        parts = [(root.i, root)]
        
        for child in root.children:
            # Capture particles (give UP), prepositions (rely ON), and agents (by)
            if child.dep_ in ("prt", "prep", "agent"):
                parts.append((child.i, child))
            # Special case for "is a": "a" might be an attribute or det
            elif child.text.lower() in ("a", "an") and root.lemma_ == "be":
                parts.append((child.i, child))
        
        # Sort by position to maintain order
        parts.sort(key=lambda x: x[0])
        
        # Step 4: Construct canonical name
        canonical_parts = []
        for _, token in parts:
            if token == root:
                # Use lemma for the root (normalize tense)
                canonical_parts.append(token.lemma_.lower())
            else:
                # Use text for particles/preps (usually keep as is)
                canonical_parts.append(token.text.lower())
        
        canonical_name = "_".join(canonical_parts)
        lemma = root.lemma_.lower()
        pos_tag = root.pos_
        tense_tag = root.tag_
        
        # Step 5: Try semantic matching first if enabled
        if use_semantic:
            semantic_match = _get_semantic_match(
                canonical_name,
                "relationship",
                config
            )
            if semantic_match:
                # Found a semantic match - use it as canonical
                logger.debug(f"Semantic match: '{canonical_name}' -> '{semantic_match}'")
                canonical_name = semantic_match
        
        # Step 6: Get synonyms
        # Try canonical name first (e.g. rely_on) for phrasal verbs
        synonym_result = get_aliases(
            input_text=canonical_name,
            input_type="relationship",
            config=config
        )
        synonyms = synonym_result.get("aliases", [])
        
        # If no synonyms found for phrase, try lemma
        if not synonyms and "_" not in canonical_name:
            synonym_result = get_aliases(
                input_text=lemma,
                input_type="relationship",
                config=config
            )
            synonyms = synonym_result.get("aliases", [])
        
        # Inflect synonyms
        inflected_aliases = []
        for synonym in synonyms:
            inflected = _inflect_verb(synonym, tense_tag)
            if inflected and inflected != lemma:
                inflected_aliases.append(inflected)
        
        return {
            "canonical_name": canonical_name,
            "lemma": lemma,
            "aliases": inflected_aliases[:5],
            "original_text": relationship,
            "pos_tag": pos_tag,
            "tense_tag": tense_tag,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error canonicalizing relationship '{relationship}': {e}")
        return _error_result(relationship, str(e))


def _error_result(text: str, error: str) -> Dict:
    """Helper for error returns."""
    return {
        "canonical_name": text,
        "lemma": text,
        "aliases": [],
        "original_text": text,
        "pos_tag": "UNKNOWN",
        "tense_tag": "UNKNOWN",
        "success": False,
        "error": error
    }


def _inflect_verb(verb: str, tense_tag: str) -> str:
    """
    Inflect a verb to match the given tense tag.
    Simple heuristic implementation.
    """
    if tense_tag == "VBG":
        if verb.endswith('e') and not verb.endswith('ee'):
            return verb[:-1] + "ing"
        elif verb.endswith(('p', 't', 'n', 'm', 'g')) and len(verb) >= 3:
            if _should_double_consonant(verb):
                return verb + verb[-1] + "ing"
        return verb + "ing"
    return verb


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


def _should_double_consonant(verb: str) -> bool:
    """Determine if the final consonant should be doubled."""
    if len(verb) < 3:
        return False
    vowels = set('aeiou')
    if (verb[-3] not in vowels and verb[-2] in vowels and verb[-1] not in vowels and verb[-1] not in 'wxy'):
        common_doublers = {'run', 'sit', 'plan', 'stop', 'shop', 'drop', 'hit', 'get', 'cut'}
        if verb in common_doublers or len(verb) <= 4:
            return True
    return False
