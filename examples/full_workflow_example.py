"""
Example: Full Workflow

Demonstrates end-to-end workflow:
NER → Get Aliases → Canonicalize → Resolve
"""

from ner_lib import (
    recognize_entities,
    get_aliases,
    canonicalize_entity,
    canonicalize_relationship,
    EntityResolver
)

print("=" * 80)
print("Full Workflow Example: From Text to Canonical Entities")
print("=" * 80)

# Sample text
text = """
Apple Inc. was founded by Steve Jobs in Cupertino. Microsoft was created by Bill Gates.
Apple is running several projects while Microsoft is developing new AI tools.
"""

print(f"\nInput Text:\n{text}\n")

# Step 1: Named Entity Recognition
print("="*80)
print("Step 1: Extract Named Entities")
print("="*80)

ner_result = recognize_entities(text)

print(f"\nFound {ner_result['total_entities']} unique entities:")
for entity in ner_result['entities']:
    print(f"  - {entity['text']} ({entity['type']})")

# Step 2: Get Aliases for Each Entity
print("\n" + "="*80)
print("Step 2: Get Aliases from Wikidata")
print("="*80)

entity_aliases = {}
for entity_info in ner_result['entities']:
    if entity_info['type'] in ['ORG', 'PERSON', 'GPE']:  # Focus on key types
        entity = entity_info['text']
        print(f"\nEntity: {entity}")
        
        alias_result = get_aliases(entity, input_type="named-entity")
        if alias_result['success'] and alias_result['aliases']:
            entity_aliases[entity] = alias_result['aliases'][:3]  # Keep top 3
            print(f"  Aliases: {', '.join(entity_aliases[entity])}")
            if alias_result.get('description'):
                print(f"  Description: {alias_result['description'][:80]}...")
        else:
            entity_aliases[entity] = []
            print(f"  No aliases found")

# Step 3: Canonicalize Entities
print("\n" + "="*80)
print("Step 3: Canonicalize Entities")
print("="*80)

for entity in list(entity_aliases.keys())[:2]:  # Process first 2 entities
    print(f"\nCanonicalizing: {entity}")
    
    canon_result = canonicalize_entity(
        entity,
        mode="progressive",
        aliases=entity_aliases.get(entity)
    )
    
    if canon_result['success']:
        print(f"  Canonical Name: {canon_result['canonical_name']}")
        print(f"  Normalized: {canon_result['normalized_name']}")
        print(f"  Confidence: {canon_result['confidence']:.3f}")

# Step 4: Extract and Canonicalize Relationships
print("\n" + "="*80)
print("Step 4: Extract and Canonicalize Relationships")
print("="*80)

# For demonstration, extract some verbs from the text
relationships = ["is running", "is developing"]

for rel in relationships:
    print(f"\nRelationship: '{rel}'")
    
    rel_result = canonicalize_relationship(rel)
    if rel_result['success']:
        print(f"  Canonical: {rel_result['canonical_name']}")
        print(f"  Lemma: {rel_result['lemma']}")
        print(f"  Inflected Synonyms: {', '.join(rel_result['aliases'][:3]) if rel_result['aliases'] else 'None'}")

# Step 5: Build Knowledge Base and Resolve
print("\n" + "="*80)
print("Step 5: Build Knowledge Base and Resolve Entity Mentions")
print("="*80)

# Create a small knowledge base
resolver = EntityResolver(mode='A')

# Add some entities
resolver.add_entity(
    "Apple Inc.",
    aliases=["Apple", "AAPL", "Apple Computer"],
    metadata={"domain": "apple.com", "industry": "Technology"}
)

resolver.add_entity(
    "Microsoft Corporation",
    aliases=["Microsoft", "MSFT", "MS"],
    metadata={"domain": "microsoft.com", "industry": "Technology"}
)

resolver.add_entity(
    "Steve Jobs",
    aliases=["Steven Jobs", "Jobs"],
    metadata={"role": "Founder", "company": "Apple"}
)

# Test resolution
test_mentions = ["apple inc", "microsoft", "steve jobs", "AAPL"]

print("\nResolving mentions:")
for mention in test_mentions:
    result = resolver.resolve(mention)
    if result.matched_entity:
        print(f"  '{mention}' → {result.matched_entity.canonical_name} (confidence: {result.confidence:.3f})")
    else:
        print(f"  '{mention}' → No match")

print("\n" + "="*80)
print("Full Workflow Complete!")
print("="*80)
print("\nThis example demonstrated:")
print("  1. Extracting entities from text")
print("  2. Getting aliases from Wikidata")
print("  3. Canonicalizing entities")
print("  4. Canonicalizing relationships")
print("  5. Building a knowledge base and resolving mentions")
