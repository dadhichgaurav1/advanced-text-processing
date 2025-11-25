"""
Demo script for semantic matching in canonicalization.

This demonstrates how to use the new semantic matching feature to map
input text to canonical schema terms using embeddings.
"""

import logging
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from ner_lib.canonicalization.relationship_canonicalization import canonicalize_relationship
from ner_lib.canonicalization.property_canonicalization import canonicalize_property_name
from ner_lib.config import Config

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def demo_without_semantic_matching():
    """Demo canonicalization without semantic matching (WordNet only)."""
    print("=" * 80)
    print("DEMO 1: Canonicalization WITHOUT Semantic Matching (WordNet only)")
    print("=" * 80)
    
    # Test relationships
    print("\n--- Relationships ---")
    relationships = [
        "relies on",
        "depends upon",
        "gave up",
        "surrendered",
        "is running"
    ]
    
    for rel in relationships:
        result = canonicalize_relationship(rel)
        print(f"'{rel}' -> '{result['canonical_name']}' (aliases: {result['aliases'][:3]})")
    
    # Test properties
    print("\n--- Properties ---")
    properties = [
        "date of birth",
        "birth date",
        "created at",
        "creation time"
    ]
    
    for prop in properties:
        result = canonicalize_property_name(prop)
        print(f"'{prop}' -> '{result['canonical_name']}' (aliases: {result['aliases'][:3]})")


def demo_with_semantic_matching():
    """Demo canonicalization WITH semantic matching."""
    print("\n" + "=" * 80)
    print("DEMO 2: Canonicalization WITH Semantic Matching")
    print("=" * 80)
    
    # Define canonical schema for a graph database
    canonical_relationships = [
        "depends_on",
        "created_by",
        "part_of",
        "assigned_to",
        "related_to"
    ]
    
    canonical_properties = [
        "date_of_birth",
        "created_at",
        "updated_at",
        "first_name",
        "last_name",
        "email_address"
    ]
    
    # Create config with semantic matching enabled
    config = Config()
    config.semantic_matching.enabled = True
    config.semantic_matching.canonical_relationships = canonical_relationships
    config.semantic_matching.canonical_properties = canonical_properties
    config.semantic_matching.similarity_threshold = 0.6  # Lower threshold for demo
    
    print(f"\nCanonical Relationships: {canonical_relationships}")
    print(f"Canonical Properties: {canonical_properties}")
    print(f"Similarity Threshold: {config.semantic_matching.similarity_threshold}")
    
    # Test relationships
    print("\n--- Relationships ---")
    test_relationships = [
        "relies on",           # Should match "depends_on"
        "depends upon",        # Should match "depends_on"
        "made by",             # Should match "created_by"
        "is part of",          # Should match "part_of"
        "assigned to",         # Exact match
        "gave up"              # No good match (should keep original)
    ]
    
    for rel in test_relationships:
        result = canonicalize_relationship(rel, config=config)
        print(f"'{rel}' -> '{result['canonical_name']}'")
    
    # Test properties
    print("\n--- Properties ---")
    test_properties = [
        "birth date",          # Should match "date_of_birth"
        "date of birth",       # Should match "date_of_birth"
        "creation time",       # Should match "created_at"
        "first name",          # Should match "first_name"
        "email",               # Should match "email_address"
        "random property"      # No good match (should keep original)
    ]
    
    for prop in test_properties:
        result = canonicalize_property_name(prop, config=config)
        print(f"'{prop}' -> '{result['canonical_name']}'")


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("SEMANTIC MATCHING DEMO FOR CANONICALIZATION")
    print("=" * 80)
    
    # Demo 1: Without semantic matching
    demo_without_semantic_matching()
    
    # Demo 2: With semantic matching
    try:
        demo_with_semantic_matching()
    except ImportError as e:
        print(f"\n⚠️  Semantic matching requires sentence-transformers: {e}")
        print("Install with: pip install sentence-transformers")
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
