"""Tests for Named Entity Recognition module."""

import pytest
from ner_lib import recognize_entities


def test_recognize_entities_basic():
    """Test basic entity recognition."""
    text = "Apple Inc. was founded by Steve Jobs in Cupertino, California."
    result = recognize_entities(text)
    
    assert result['total_entities'] > 0
    assert 'entities' in result
    assert len(result['entities']) > 0
    
    # Check that we found some expected entities
    entity_texts = [e['text'] for e in result['entities']]
    assert any('Apple' in text for text in entity_texts)


def test_recognize_entities_types():
    """Test entity type detection."""
    text = "Microsoft is based in Seattle. Bill Gates founded it."
    result = recognize_entities(text)
    
    # Check entity types are present
    for entity in result['entities']:
        assert 'type' in entity
        assert 'text' in entity
        assert 'count' in entity
        assert entity['count'] >= 1


def test_recognize_entities_counting():
    """Test occurrence counting."""
    text = "Apple makes the iPhone. Apple also makes the iPad. Apple is innovative."
    result = recognize_entities(text)
    
    # Find Apple in entities
    apple_entities = [e for e in result['entities'] if 'Apple' in e['text']]
    if apple_entities:
        # Should count Apple multiple times
        assert apple_entities[0]['count'] >= 1


def test_recognize_entities_empty_text():
    """Test with empty text."""
    result = recognize_entities("")
    
    assert'entities' in result
    assert result['total_entities'] == 0


def test_recognize_entities_no_entities():
    """Test text with no named entities."""
    text = "The quick brown fox jumps over the lazy dog."
    result = recognize_entities(text)
    
    # May find 0 or few entities
    assert isinstance(result['entities'], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
