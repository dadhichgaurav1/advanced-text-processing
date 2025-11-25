"""
Example: Get Aliases

Demonstrates how to get aliases for different types of inputs using get_aliases().
"""

from ner_lib import get_aliases

print("=" * 80)
print("Get Aliases Example")
print("=" * 80)

# Example 1: Get aliases for a named entity from Wikidata
print("\n" + "=" * 80)
print("1. Named Entity Aliases (from Wikidata)")
print("=" * 80)

entities = ["Albert Einstein", "Microsoft", "New York City", "Python"]

for entity in entities:
    print(f"\nEntity: '{entity}'")
    result = get_aliases(entity, input_type="named-entity")
    
    if result['success']:
        print(f"  Description: {result.get('description', 'N/A')}")
        print(f"  Aliases: {', '.join(result['aliases'][:5]) if result['aliases'] else 'None found'}")
    else:
        print(f"  Error: {result.get('error', 'Unknown error')}")

# Example 2: Get synonyms for relationships (verbs)
print("\n" + "=" * 80)
print("2. Relationship Synonyms (Verbs from WordNet)")
print("=" * 80)

relationships = ["run", "execute", "create", "analyze", "develop"]

for rel in relationships:
    print(f"\nRelationship: '{rel}'")
    result = get_aliases(rel, input_type="relationship")
    
    if result['success']:
        print(f"  Synonyms: {', '.join(result['aliases']) if result['aliases'] else 'None found'}")
    else:
        print(f"  Error: {result.get('error', 'Unknown error')}")

# Example 3: Get synonyms for property names (adjectives)
print("\n" + "=" * 80)
print("3. Property Name Synonyms (Adjectives from WordNet)")
print("=" * 80)

properties = ["large", "fast", "beautiful", "important", "complex"]

for prop in properties:
    print(f"\nProperty: '{prop}'")
    result = get_aliases(prop, input_type="property-name")
    
    if result['success']:
        print(f"  Synonyms: {', '.join(result['aliases']) if result['aliases'] else 'None found'}")
    else:
        print(f"  Error: {result.get('error', 'Unknown error')}")

# Example 4: Get synonyms for property values (nouns)
print("\n" + "=" * 80)
print("4. Property Value Synonyms (Nouns from WordNet)")
print("=" * 80)

values = ["car", "building", "person", "computer", "book"]

for val in values:
    print(f"\nValue: '{val}'")
    result = get_aliases(val, input_type="property-value")
    
    if result['success']:
        print(f"  Synonyms: {', '.join(result['aliases']) if result['aliases'] else 'None found'}")
    else:
        print(f"  Error: {result.get('error', 'Unknown error')}")

print("\n" + "=" * 80)
print("Example Complete!")
print("=" * 80)
