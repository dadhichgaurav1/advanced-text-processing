"""Quick test without sentence transformers to verify basic functionality."""

from ner_lib.normalization.text import normalize_entity_name, create_acronym, token_containment
from ner_lib.storage import MemoryStorage
from ner_lib.models.entity import Entity, Mention
from ner_lib.signals.deterministic import ExactMatcher
from ner_lib.signals.string_similarity import token_set_ratio, quick_fuzzy_score
from ner_lib.signals.acronym import is_acronym_match

print("=" * 60)
print("NER Library - Basic Component Verification")
print("=" * 60)

# Test 1: Normalization
print("\n1. Testing text normalization...")
result1 = normalize_entity_name("Apple Inc.")
result2 = normalize_entity_name("Microsoft, Ltd.")
result3 = normalize_entity_name("Google LLC")
print(f"  'Apple Inc.' -> '{result1}'")
print(f"  'Microsoft, Ltd.' -> '{result2}'")
print(f"  'Google LLC' -> '{result3}'")
assert result1 == "apple"  # Inc is stripped
assert result2 == "microsoft"  # Ltd is stripped
assert result3 == "google"  # LLC is stripped
print("✓ Text normalization working (legal suffixes stripped correctly)")

# Test 2: Acronym generation
print("\n2. Testing acronym generation...")
assert create_acronym("International Business Machines") == "IBM"
assert create_acronym("United States of America") == "USA"
print("✓ Acronym generation working")
print(f"  'International Business Machines' -> '{create_acronym('International Business Machines')}'")

# Test 3: Token containment
print("\n3. Testing token containment...")
assert token_containment("apple", "apple inc") == True
assert token_containment("microsoft corp", "microsoft") == True
print("✓ Token containment working")

# Test 4: Storage
print("\n4. Testing storage...")
storage = MemoryStorage()
entity = Entity(
    canonical_name="Apple Inc.",
    aliases=["Apple", "AAPL"]
)
entity_id = storage.create_entity(entity)
retrieved = storage.get_entity(entity_id)
assert retrieved is not None
assert retrieved.canonical_name == "Apple Inc."
print("✓ Storage working")
print(f"  Stored and retrieved: {retrieved.canonical_name}")

# Test 5: Exact matcher
print("\n5. Testing exact matcher...")
matcher = ExactMatcher()
matcher.add_entity("entity1", "Apple Inc.", ["Apple", "AAPL"])
matcher.add_entity("entity2", "Microsoft Corporation", ["Microsoft"])

result = matcher.match("apple inc")
assert result is not None
assert result[0] == "entity1"
print("✓ Exact matcher working")
print(f"  'apple inc' -> entity1 (Apple Inc.)")

# Test 6: Fuzzy matching
print("\n6. Testing fuzzy matching...")
score1 = token_set_ratio("apple inc", "apple inc.")
score2 = token_set_ratio("microsoft corp", "microsoft corporation")
assert score1 > 0.9
assert score2 > 0.7
print("✓ Fuzzy matching working")
print(f"  'apple inc' vs 'apple inc.' -> {score1:.3f}")
print(f"  'microsoft corp' vs 'microsoft corporation' -> {score2:.3f}")

# Test 7: Acronym detection
print("\n7. Testing acronym detection...")
assert is_acronym_match("IBM", "International Business Machines") == True
assert is_acronym_match("USA", "United States of America") == True
assert is_acronym_match("XYZ", "International Business Machines") == False
print("✓ Acronym detection working")
print(f"  'IBM' matches 'International Business Machines': True")

print("\n" + "=" * 60)
print("All core components verified! ✓")
print("=" * 60)

print("\n✓ Core NER library components are working correctly!")
print("\nNote: Full test with semantic embeddings requires fixing")
print("torch/transformers dependency compatibility.")
print("\nThe library is functional for:")
print("  - Exact matching")
print("  - Fuzzy matching (RapidFuzz)")
print("  - Acronym detection")
print("  - Entity storage")
print("\nTo use semantic matching, ensure compatible versions of:")
print("  - torch")
print("  - transformers")
print("  - sentence-transformers")
