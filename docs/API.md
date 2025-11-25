# API Reference

This document provides a reference for the public API of the **Advanced Text Processing** library.

## Core Functions

### `recognize_entities`

Extracts named entities from the input text using spaCy.

```python
def recognize_entities(text: str) -> Dict[str, Any]
```

**Parameters:**
- `text` (str): The input text to analyze.

**Returns:**
- `Dict[str, Any]`: A dictionary containing:
  - `entities` (List[Dict]): List of detected entities with `text`, `type`, `start_char`, `end_char`.
  - `total_entities` (int): Count of entities found.
  - `entity_types` (List[str]): List of unique entity types found.

**Example:**
```python
result = recognize_entities("Apple Inc. is in California.")
# {'entities': [{'text': 'Apple Inc.', 'type': 'ORG', ...}, ...], ...}
```

---

### `get_aliases`

Retrieves aliases or synonyms for a given term based on the input type.

```python
def get_aliases(
    input_text: str, 
    input_type: str, 
    properties: Optional[Dict] = None
) -> Dict[str, Any]
```

**Parameters:**
- `input_text` (str): The text to find aliases for.
- `input_type` (str): The type of input. Options:
  - `"named-entity"`: Queries Wikidata.
  - `"relationship"`: Queries WordNet (verbs).
  - `"property-name"`: Queries WordNet (adjectives).
  - `"property-value"`: Queries WordNet (nouns).
- `properties` (Optional[Dict]): Additional properties for context (unused currently).

**Returns:**
- `Dict[str, Any]`: Dictionary containing:
  - `aliases` (List[str]): List of aliases/synonyms.
  - `description` (str): Description of the entity (for named entities).
  - `source` (str): Source of the data ("Wikidata" or "WordNet").

---

### `canonicalize_entity`

Canonicalizes a named entity using the configured resolution mode (A or B).

```python
def canonicalize_entity(
    entity: str, 
    mode: str = "progressive", 
    candidates: Optional[List[str]] = None
) -> Dict[str, Any]
```

**Parameters:**
- `entity` (str): The entity mention to canonicalize.
- `mode` (str): Resolution mode. "progressive" (Mode A) or "complete" (Mode B).
- `candidates` (Optional[List[str]]): Optional list of candidate strings to match against.

**Returns:**
- `Dict[str, Any]`: Dictionary containing:
  - `canonical_name` (str): The resolved canonical name.
  - `normalized_name` (str): The normalized input string.
  - `aliases` (List[str]): List of aliases for the canonical entity.
  - `confidence` (float): Confidence score of the match.

---

### `canonicalize_relationship`

Canonicalizes a relationship (verb phrase) to its base form and finds synonyms.

```python
def canonicalize_relationship(
    relationship: str,
    config: Optional[Config] = None
) -> Dict[str, Any]
```

**Parameters:**
- `relationship` (str): The relationship phrase (e.g., "is running", "relies on").
- `config` (Optional[Config]): Configuration object (required for semantic matching).

**Returns:**
- `Dict[str, Any]`: Dictionary containing:
  - `canonical_name` (str): The canonical form (e.g., "run", "depends_on").
  - `lemma` (str): The lemma of the main verb.
  - `aliases` (List[str]): Inflected synonyms.

---

### `canonicalize_property_name`

Canonicalizes a property name (typically adjective-based).

```python
def canonicalize_property_name(
    property_name: str,
    config: Optional[Config] = None
) -> Dict[str, Any]
```

**Parameters:**
- `property_name` (str): The property name (e.g., "biggest", "birth date").
- `config` (Optional[Config]): Configuration object.

**Returns:**
- `Dict[str, Any]`: Dictionary containing:
  - `canonical_name` (str): The canonical form.
  - `lemma` (str): The lemma.
  - `aliases` (List[str]): Synonyms.

---

### `canonicalize_property_value`

Canonicalizes a property value (typically noun-based).

```python
def canonicalize_property_value(property_value: str) -> Dict[str, Any]
```

**Parameters:**
- `property_value` (str): The value to canonicalize (e.g., "automobiles").

**Returns:**
- `Dict[str, Any]`: Dictionary containing:
  - `canonical_name` (str): The canonical form.
  - `lemma` (str): The lemma.
  - `aliases` (List[str]): Synonyms.

## Configuration

### `Config`

Main configuration class for the library.

```python
from ner_lib import Config

config = Config()
```

**Key Attributes:**

- `semantic_matching`: Configuration for semantic matching.
  - `enabled` (bool): Enable/disable semantic matching.
  - `similarity_threshold` (float): Threshold for cosine similarity (0.0-1.0).
  - `canonical_relationships` (List[str]): List of canonical relationship names.
  - `canonical_properties` (List[str]): List of canonical property names.

- `wikidata`: Configuration for Wikidata API.
  - `requests_per_minute` (int): Rate limit.
  - `cache_ttl_seconds` (int): Cache duration.

- `synonyms`: Configuration for synonym retrieval.
  - `max_synonyms` (int): Max synonyms to return.

## Classes

### `EntityResolver`

The main class for entity resolution logic.

```python
class EntityResolver:
    def __init__(self, config: Optional[Config] = None, mode: str = 'A'):
        ...
        
    def add_entity(self, canonical_name: str, aliases: List[str] = None, ...):
        """Register a known entity."""
        
    def resolve(self, mention_text: str) -> MatchResult:
        """Resolve a mention to a known entity."""
```

### `SemanticMatcher`

Handles embedding-based semantic matching.

```python
class SemanticMatcher:
    def __init__(self, config: SemanticMatchingConfig):
        ...
        
    def match(self, text: str, candidates: List[str]) -> Optional[Tuple[str, float]]:
        """Find best match for text among candidates using embeddings."""
```
