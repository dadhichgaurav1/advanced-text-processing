"""
Example: Mode A - Without Semantic Matching
(Works even without sentence-transformers)
"""

from ner_lib import EntityResolver

# Initialize resolver in Mode A
resolver = EntityResolver(mode='A')

# Add known entities
resolver.add_entity(
    canonical_name="Apple Inc.",
    aliases=["Apple", "AAPL", "Apple Computer"],
    metadata={"domain": "apple.com", "industry": "Technology"}
)

resolver.add_entity(
    canonical_name="Microsoft Corporation",
    aliases=["Microsoft", "MSFT", "MS"],
    metadata={"domain": "microsoft.com", "industry": "Technology"}
)

resolver.add_entity(
    canonical_name="International Business Machines",
    aliases=["IBM", "Big Blue"],
    metadata={"domain": "ibm.com", "industry": "Technology"}
)

resolver.add_entity(
    canonical_name="Amazon.com, Inc.",
    aliases=["Amazon", "AMZN"],
    metadata={"domain": "amazon.com", "industry": "E-commerce"}
)

# NOTE: Skip build_semantic_index() when semantic dependencies are not available
# The library will still work using exact matching, fuzzy matching, and acronyms

print("Mode A: Sequential Pipeline (No Semantic Matching)")
print("=" * 60)

# Test different matching scenarios
test_mentions = [
    "apple inc",  # Exact match (normalized)
    "IBM",  # Acronym match
    "microsoft corp",  # Fuzzy match
    "amazon",  # Alias match
    "AAPL",  # Ticker symbol (alias)
    "big blue",  # Nickname (alias)
]

for mention_text in test_mentions:
    result = resolver.resolve(mention_text)
    
    print(f"\nMention: '{mention_text}'")
    
    if result.matched_entity:
        print(f"  ✓ Matched: {result.matched_entity.canonical_name}")
        print(f"  Confidence: {result.confidence:.3f}")
        print(f"  Citations: {[f'{c.source}/{c.method}' for c in result.citations]}")
        print(f"  Next Steps: {result.next_steps.value}")
    else:
        print(f"  ✗ No match found")
        print(f"  Next Steps: {result.next_steps.value}")

# Batch resolution
print("\n" + "=" * 60)
print("Batch Resolution:")
print("=" * 60)

batch_mentions = ["apple", "msft", "big blue", "amzn"]
results = resolver.resolve_batch(batch_mentions)

for result in results:
    if result.matched_entity:
        print(f"{result.mention.text:15} -> {result.matched_entity.canonical_name}")
    else:
        print(f"{result.mention.text:15} -> No match")

print("\n✓ Mode A working successfully without semantic matching!")
print("Add entities, resolve mentions using exact/fuzzy/acronym matching.")
