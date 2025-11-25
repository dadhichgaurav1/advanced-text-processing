"""
Example: Canonicalization Functions

Demonstrates all canonicalization functions:
- canonicalize_entity()
- canonicalize_relationship()
- canonicalize_property_name()
- canonicalize_property_value()
"""

from ner_lib import (
    canonicalize_entity,
    canonicalize_relationship,
    canonicalize_property_name,
    canonicalize_property_value
)

print("=" * 80)
print("Canonicalization Examples")
print("=" * 80)

# Example 1: Entity Canonicalization
print("\n" + "=" * 80)
print("1. Entity Canonicalization")
print("=" * 80)

entities = [
    ("apple inc", "progressive"),
    ("Microsoft Corporation", "complete"),
    ("IBM", "progressive")
]

for entity, mode in entities:
    print(f"\nEntity: '{entity}' (Mode: {mode})")
    result = canonicalize_entity(entity, mode=mode)
    
    if result['success']:
        print(f"  Canonical Name: {result['canonical_name']}")
        print(f"  Normalized: {result['normalized_name']}")
        print(f"  Aliases: {', '.join(result['aliases'][:5]) if result['aliases'] else 'Fetching...'}")
        print(f"  Confidence: {result['confidence']:.3f}")
    else:
        print(f"  Note: {result.get('error', 'Entity not in knowledge base')}")

# Example 2: Relationship Canonicalization
print("\n" + "=" * 80)
print("2. Relationship Canonicalization (Verbs)")
print("=" * 80)

relationships = [
    "is running",
    "was executed",
    "are creating",
    "has analyzed",
    "will develop"
]

for rel in relationships:
    print(f"\nRelationship: '{rel}'")
    result = canonicalize_relationship(rel)
    
    if result['success']:
        print(f"  Canonical: {result['canonical_name']}")
        print(f"  Lemma: {result['lemma']}")
        print(f"  POS/Tense: {result['pos_tag']} / {result['tense_tag']}")
        print(f"  Aliases: {', '.join(result['aliases']) if result['aliases'] else 'None'}")
    else:
        print(f"  Error: {result.get('error', 'Unknown error')}")

# Example 3: Property Name Canonicalization
print("\n" + "=" * 80)
print("3. Property Name Canonicalization (Adjectives)")
print("=" * 80)

properties = [
    "largest",
    "very fast",
    "most beautiful",
    "important",
    "extremely complex"
]

for prop in properties:
    print(f"\nProperty: '{prop}'")
    result = canonicalize_property_name(prop)
    
    if result['success']:
        print(f"  Canonical: {result['canonical_name']}")
        print(f"  Lemma: {result['lemma']}")
        print(f"  Synonyms: {', '.join(result['aliases']) if result['aliases'] else 'None'}")
    else:
        print(f"  Error: {result.get('error', 'Unknown error')}")

# Example 4: Property Value Canonicalization
print("\n" + "=" * 80)
print("4. Property Value Canonicalization (Nouns)")
print("=" * 80)

values = [
    "automobiles",
    "tall buildings",
    "many people",
    "computers",
    "old books"
]

for val in values:
    print(f"\nValue: '{val}'")
    result = canonicalize_property_value(val)
    
    if result['success']:
        print(f"  Canonical: {result['canonical_name']}")
        print(f"  Lemma: {result['lemma']}")
        print(f"  Synonyms: {', '.join(result['aliases']) if result['aliases'] else 'None'}")
    else:
        print(f"  Error: {result.get('error', 'Unknown error')}")

print("\n" + "=" * 80)
print("All Canonicalization Examples Complete!")
print("=" * 80)
