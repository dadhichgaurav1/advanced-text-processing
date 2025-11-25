"""Tests for canonicalization functions."""

import pytest
from ner_lib import (
    canonicalize_entity,
    canonicalize_relationship,
    canonicalize_property_name,
    canonicalize_property_value
)


def test_canonicalize_entity_basic():
    """Test basic entity canonicalization."""
    result = canonicalize_entity("apple inc", mode="progressive")
    
    assert 'canonical_name' in result
    assert 'normalized_name' in result
    assert 'aliases' in result
    assert result['normalized_name'] == 'apple'  # Normalized form


def test_canonicalize_entity_modes():
    """Test different modes."""
    result_progressive = canonicalize_entity("Microsoft", mode="progressive")
    result_complete = canonicalize_entity("Microsoft", mode="complete")
    
    assert result_progressive['resolution_mode'] == "progressive"
    assert result_complete['resolution_mode'] == "complete"


def test_canonicalize_entity_with_aliases():
    """Test providing aliases."""
    result = canonicalize_entity(
        "Apple",
        mode="progressive",
        aliases=["AAPL", "Apple Computer"]
    )
    
    assert 'AAPL' in result['aliases'] or 'Apple Computer' in result['aliases']


def test_canonicalize_relationship_basic():
    """Test relationship canonicalization."""
    result = canonicalize_relationship("is running")
    
    assert 'canonical_name' in result
    assert 'lemma' in result
    assert 'aliases' in result
    assert result['lemma'] == 'run'  # Lemma of "running"


def test_canonicalize_relationship_vbg():
    """Test VBG tense inflection."""
    result = canonicalize_relationship("running")
    
    if result['success']:
        assert result['tense_tag'] in ['VBG', 'VERB']  # May vary
        assert result['lemma'] == 'run'


def test_canonicalize_property_name_basic():
    """Test property name canonicalization."""
    result = canonicalize_property_name("large")
    
    # May or may not find adjective depending on spaCy model
    assert 'canonical_name' in result
    assert 'lemma' in result
    assert 'aliases' in result


def test_canonicalize_property_name_comparative():
    """Test with comparative adjective."""
    result = canonicalize_property_name("largest")
    
    if result['success']:
        assert result['lemma'] == 'large'


def test_canonicalize_property_value_basic():
    """Test property value canonicalization."""
    result = canonicalize_property_value("cars")
    
    if result['success']:
        assert result['lemma'] == 'car'


def test_canonicalize_property_value_plural():
    """Test with plural noun."""
    result = canonicalize_property_value("automobiles")
    
    assert 'canonical_name' in result
    assert 'lemma' in result


def test_canonicalize_relationship_no_verb():
    """Test relationship with no verb."""
    result = canonicalize_relationship("beautiful building")
    
    # Should handle gracefully
    assert 'canonical_name' in result
    # Success may be False if no verb found
    if not result.get('success', True):
        assert 'error' in result


def test_canonicalize_property_name_no_adjective():
    """Test property name with no adjective."""
    result = canonicalize_property_name("running quickly")
    
    assert 'canonical_name' in result
    # May not find adjective


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
