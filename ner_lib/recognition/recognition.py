"""Named Entity Recognition using spaCy."""

from typing import Dict, List
from collections import Counter
import logging

logger = logging.getLogger(__name__)


def recognize_entities(text: str, model_name: str = "en_core_web_lg") -> Dict:
    """
    Extract named entities from text using spaCy.
    
    Args:
        text: Input text to extract named entities from
        model_name: spaCy model to use (default: en_core_web_lg)
    
    Returns:
        Dictionary containing:
        - entities: List of dicts with entity info (text, type, count)
        - total_entities: Total number of entities found
        - entity_types: Count of entities by type
    
    Example:
        >>> result = recognize_entities("Apple Inc. was founded by Steve Jobs in Cupertino")
        >>> print(result['entities'])
        [
            {'text': 'Apple Inc.', 'type': 'ORG', 'count': 1},
            {'text': 'Steve Jobs', 'type': 'PERSON', 'count': 1},
            {'text': 'Cupertino', 'type': 'GPE', 'count': 1}
        ]
    """
    try:
        import spacy
    except ImportError:
        raise ImportError(
            "spaCy is required for Named Entity Recognition. "
            "Install it with: pip install spacy && python -m spacy download en_core_web_lg"
        )
    
    # Load spaCy model - prioritize larger models for better NER
    nlp = None
    # Try models in order of quality for NER: lg > md > sm
    models_to_try = ["en_core_web_lg", "en_core_web_md", "en_core_web_sm"]
    
    # If user specified a model, try it first
    if model_name not in models_to_try:
        models_to_try.insert(0, model_name)
    
    loaded_model = None
    for model in models_to_try:
        try:
            nlp = spacy.load(model)
            loaded_model = model
            logger.info(f"Loaded spaCy model: {model}")
            break
        except OSError:
            logger.debug(f"Model {model} not available, trying next...")
            continue
    
    if nlp is None:
        raise OSError(
            "Could not load any spaCy model. Please install one manually:\n"
            "python -m spacy download en_core_web_lg"
        )
    
    # Log which model we're using
    print(f"[NER] Using spaCy model: {loaded_model}")
    
    # Process text
    doc = nlp(text)
    
    # Count occurrences of each entity
    entity_counter = Counter()
    entity_types_map = {}
    
    for ent in doc.ents:
        entity_counter[ent.text] += 1
        entity_types_map[ent.text] = ent.label_
    
    # Build entity list
    entities = []
    for entity_text, count in entity_counter.items():
        entities.append({
            "text": entity_text,
            "type": entity_types_map[entity_text],
            "count": count
        })
    
    # Sort by occurrence count (descending), then alphabetically
    entities.sort(key=lambda x: (-x['count'], x['text']))
    
    # Count entities by type
    entity_type_counts = Counter([e['type'] for e in entities])
    
    return {
        "entities": entities,
        "total_entities": len(entities),
        "entity_types": dict(entity_type_counts)
    }


def get_entity_types() -> List[str]:
    """
    Get list of entity types recognized by spaCy.
    
    Returns:
        List of entity type labels
    
    Common entity types:
        - PERSON: People, including fictional characters
        - ORG: Companies, agencies, institutions
        - GPE: Countries, cities, states (Geo-Political Entity)
        - LOC: Non-GPE locations, mountain ranges, bodies of water
        - PRODUCT: Objects, vehicles, foods, etc.
        - EVENT: Named hurricanes, battles, wars, sports events
        - WORK_OF_ART: Titles of books, songs, etc.
        - LAW: Named documents made into laws
        - LANGUAGE: Any named language
        - DATE: Absolute or relative dates or periods
        - TIME: Times smaller than a day
        - PERCENT: Percentage, including "%"
        - MONEY: Monetary values, including unit
        - QUANTITY: Measurements, as of weight or distance
        - ORDINAL: "first", "second", etc.
        - CARDINAL: Numerals that do not fall under another type
        - FAC: Buildings, airports, highways, bridges, etc.
        - NORP: Nationalities or religious or political groups
    """
    return [
        "PERSON", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "WORK_OF_ART",
        "LAW", "LANGUAGE", "DATE", "TIME", "PERCENT", "MONEY", "QUANTITY",
        "ORDINAL", "CARDINAL", "FAC", "NORP"
    ]
