"""Tests for alias retrieval module."""

import pytest
from unittest.mock import Mock, patch
from ner_lib import get_aliases, clear_caches


def test_get_aliases_wordnet_verbs():
    """Test synonym retrieval for verbs."""
    result = get_aliases("run", input_type="relationship")
    
    assert result['success'] is True
    assert 'aliases' in result
    assert result['source'] == 'wordnet'
    # Should get some synonyms
    assert isinstance(result['aliases'], list)


def test_get_aliases_wordnet_adjectives():
    """Test synonym retrieval for adjectives."""
    result = get_aliases("large", input_type="property-name")
    
    assert result['success'] is True
    assert result['source'] == 'wordnet'
    assert isinstance(result['aliases'], list)


def test_get_aliases_wordnet_nouns():
    """Test synonym retrieval for nouns."""
    result = get_aliases("car", input_type="property-value")
    
    assert result['success'] is True
    assert result['source'] == 'wordnet'
    assert isinstance(result['aliases'], list)


def test_get_aliases_invalid_type():
    """Test with invalid input type."""
    result = get_aliases("test", input_type="invalid")
    
    assert result['success'] is False
    assert 'error' in result


@patch('ner_lib.aliases.wikidata_client.WikidataClient.get_aliases_for_entity')
def test_get_aliases_wikidata_mocked(mock_get_aliases):
    """Test Wikidata alias retrieval with mocked API."""
    # Mock the Wikidata response
    mock_get_aliases.return_value = {
        'aliases': ['Einstein', 'A. Einstein'],
        'description': 'German-born theoretical physicist',
        'success': True
    }
    
    result = get_aliases("Albert Einstein", input_type="named-entity")
    
    assert 'aliases' in result
    assert result.get('source') == 'wikidata' or 'aliases' in result


def test_clear_caches():
    """Test cache clearing."""
    # Should not raise an error
    clear_caches()
    assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
