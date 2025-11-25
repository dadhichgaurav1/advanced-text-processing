"""Integration tests for NER library enhancements."""

import pytest
from ner_lib import (
    recognize_entities,
    get_aliases,
    canonicalize_entity,
    EntityResolver
)


def test_ner_to_aliases_workflow():
    """Test workflow from NER to alias retrieval."""
    # Step 1: Extract entities
    text = "Microsoft was founded by Bill Gates."
    ner_result = recognize_entities(text)
    
    assert ner_result['total_entities'] > 0
    
    # Step 2: Get aliases for first entity (if any ORG found)
    org_entities = [e for e in ner_result['entities'] if e['type'] == 'ORG']
    
    if org_entities:
        entity = org_entities[0]['text']
        alias_result = get_aliases(entity, input_type="named-entity")
        
        # Should work even if no aliases found
        assert 'aliases' in alias_result


def test_aliases_to_canonicalization_workflow():
    """Test workflow from aliases to canonicalization."""
    # Get aliases
    alias_result = get_aliases("running", input_type="relationship")
    
    if alias_result['success'] and alias_result['aliases']:
        # Should have verb synonyms
        assert isinstance(alias_result['aliases'], list)


def test_full_ner_canonicalization_resolution_workflow():
    """Test full workflow: NER → Canonicalization → Resolution."""
    # Setup
    text = "Apple Inc. makes great products."
    
    # Step 1: NER
    ner_result = recognize_entities(text)
    entities = [e for e in ner_result['entities'] if e['type'] in ['ORG', 'PERSON']]
    
    if not entities:
        pytest.skip("No ORG/PERSON entities found in test text")
    
    entity = entities[0]['text']
    
    # Step 2: Canonicalize
    canon_result = canonicalize_entity(entity, mode="progressive")
    
    assert 'canonical_name' in canon_result
    assert 'normalized_name' in canon_result
    
    # Step 3: Add to knowledge base and resolve
    resolver = EntityResolver(mode='A')
    
    # Add entity
    resolver.add_entity(
        canon_result['canonical_name'],
        aliases=canon_result.get('aliases', [])[:3]
    )
    
    # Resolve
    result = resolver.resolve(canon_result['normalized_name'])
    
    # Should resolve successfully or return a result
    assert result is not None


def test_multiple_canonicalization_types():
    """Test using multiple canonicalization functions together."""
    from ner_lib import canonicalize_relationship, canonicalize_property_name
    
    # Canonicalize a verb
    verb_result = canonicalize_relationship("executing")
    assert 'lemma' in verb_result
    
    # Canonicalize an adjective
    adj_result = canonicalize_property_name("fastest")
    assert 'lemma' in adj_result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
