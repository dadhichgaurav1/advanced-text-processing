"""NLP utilities for shared model loading."""

import logging
from typing import Optional
import spacy

logger = logging.getLogger(__name__)

_NLP_MODEL: Optional[spacy.language.Language] = None

def get_spacy_model(model_name: str = "en_core_web_lg") -> spacy.language.Language:
    """
    Get a shared spaCy model instance.
    
    Args:
        model_name: Name of the spaCy model to load
        
    Returns:
        Loaded spaCy language model
    """
    global _NLP_MODEL
    
    if _NLP_MODEL is None:
        try:
            logger.info(f"Loading spaCy model: {model_name}")
            _NLP_MODEL = spacy.load(model_name)
        except OSError:
            logger.warning(f"{model_name} not found, falling back to en_core_web_sm")
            _NLP_MODEL = spacy.load("en_core_web_sm")
            
    return _NLP_MODEL
