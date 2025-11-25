"""Basic tests for NER library."""

import pytest
from ner_lib import EntityResolver, Entity, Mention
from ner_lib.models.candidate import NextSteps
from ner_lib.normalization.text import normalize_entity_name, create_acronym, token_containment


def test_normalization():
    """Test text normalization."""
    # Test basic normalization
    assert normalize_entity_name("Apple Inc.") == "apple inc"
    assert normalize_entity_name("Microsoft, Ltd.") == "microsoft"
    assert normalize_entity_name("  IBM  Corp  ") == "ibm"
    
    # Test legal suffix stripping
    assert normalize_entity_name("Google LLC") == "google"
    assert normalize_entity_name("Meta Platforms, Inc.") == "meta platforms"


def test_acronym_generation():
    """Test acronym generation."""
    assert create_acronym("International Business Machines") == "IBM"
    assert create_acronym("The United States of America") == "USA"
    assert create_acronym("Apple Inc") == "AI"


def test_token_containment():
    """Test token containment."""
    assert token_containment("apple", "apple inc") == True
    assert token_containment("ibm", "international business machines") == False
    assert token_containment("microsoft corp", "microsoft") == True


def test_mode_a_exact_match():
    """Test Mode A with exact match."""
    resolver = EntityResolver(mode='A')
    
    # Add entity
    resolver.add_entity("Apple Inc.", aliases=["Apple", "AAPL"])
    
    # Test exact match (normalized)
    result = resolver.resolve("apple inc")
    assert result.matched_entity is not None
    assert result.matched_entity.canonical_name == "Apple Inc."
    assert result.confidence == 1.0
    assert result.next_steps == NextSteps.NONE


def test_mode_a_alias_match():
    """Test Mode A with alias match."""
    resolver = EntityResolver(mode='A')
    
    resolver.add_entity("Apple Inc.", aliases=["AAPL"])
    
    result = resolver.resolve("aapl")
    assert result.matched_entity is not None
    assert result.matched_entity.canonical_name == "Apple Inc."
    assert result.confidence == 1.0


def test_mode_a_no_match():
    """Test Mode A with no match."""
    resolver = EntityResolver(mode='A')
    
    resolver.add_entity("Apple Inc.")
    
    result = resolver.resolve("microsoft")
    assert result.matched_entity is None
    assert result.next_steps == NextSteps.NEW_ENTITY


def test_mode_b_signal_aggregation():
    """Test Mode B with multiple signals."""
    resolver = EntityResolver(mode='B')
    
    # Add entities
    resolver.add_entity(
        "Apple Inc.",
        aliases=["Apple", "AAPL"],
        metadata={"domain": "apple.com"}
    )
    
    # Build semantic index
    resolver.build_semantic_index()
    
    # Test with metadata boost
    from ner_lib.models.entity import Mention
    mention = Mention(
        text="apple inc",
        metadata={"domain": "apple.com"}
    )
    
    result = resolver.resolve(mention)
    assert result.matched_entity is not None
    assert result.matched_entity.canonical_name == "Apple Inc."
    assert result.confidence > 0.7  # Should be high with exact match + domain boost


def test_batch_resolution():
    """Test batch resolution."""
    resolver = EntityResolver(mode='A')
    
    resolver.add_entity("Apple Inc.", aliases=["Apple"])
    resolver.add_entity("Microsoft Corporation", aliases=["Microsoft"])
    resolver.add_entity("IBM", aliases=["International Business Machines"])
    
    mentions = ["apple", "microsoft", "ibm"]
    results = resolver.resolve_batch(mentions)
    
    assert len(results) == 3
    assert all(r.matched_entity is not None for r in results)
    assert results[0].matched_entity.canonical_name == "Apple Inc."
    assert results[1].matched_entity.canonical_name == "Microsoft Corporation"
    assert results[2].matched_entity.canonical_name == "IBM"


def test_add_and_retrieve_entity():
    """Test entity storage."""
    resolver = EntityResolver()
    
    entity_id = resolver.add_entity(
        "Test Company",
        aliases=["TC"],
        metadata={"domain": "test.com"}
    )
    
    entity = resolver.get_entity(entity_id)
    assert entity is not None
    assert entity.canonical_name == "Test Company"
    assert "TC" in entity.aliases
    assert entity.metadata["domain"] == "test.com"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
