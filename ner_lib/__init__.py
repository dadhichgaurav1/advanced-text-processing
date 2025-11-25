"""NER Library - Named Entity Recognition and Resolution."""

from ner_lib.resolver import EntityResolver
from ner_lib.models.entity import Entity, Mention, Alias
from ner_lib.models.candidate import MatchResult, Candidate, NextSteps
from ner_lib.config import Config, DEFAULT_CONFIG

# New functions - Job 1: Named Entity Recognition
from ner_lib.recognition import recognize_entities

# New functions - Job 2: Get Aliases
from ner_lib.aliases import get_aliases, clear_caches

# New functions - Jobs 3-6: Canonicalization
from ner_lib.canonicalization import (
    canonicalize_entity,
    canonicalize_relationship,
    canonicalize_property_name,
    canonicalize_property_value
)

__version__ = "0.2.0"
__author__ = "Gaurav Dadhich"
__license__ = "MIT"
__url__ = "https://github.com/dadhichgaurav1/advanced-text-processing"

__all__ = [
    # Core resolver
    "EntityResolver",
    
    # Models
    "Entity",
    "Mention",
    "Alias",
    "MatchResult",
    "Candidate",
    "NextSteps",
    
    # Configuration
    "Config",
    "DEFAULT_CONFIG",
    
    # New functions
    "recognize_entities",
    "get_aliases",
    "clear_caches",
    "canonicalize_entity",
    "canonicalize_relationship",
    "canonicalize_property_name",
    "canonicalize_property_value",
]
