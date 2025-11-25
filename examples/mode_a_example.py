"""
Example: Mode A - Sequential Pipeline with Early Stopping
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

# Build semantic index for better matching (optional - requires torch/transformers)
print("Building semantic index...")
try:
    resolver.build_semantic_index()
    print("Semantic index built successfully!\n")
    semantic_available = True
except ImportError as e:
    print(f"⚠ Semantic matching not available: {e}")
    print("Continuing with exact/fuzzy/acronym matching only...\n")
    semantic_available = False

# Test different matching scenarios
test_mentions = [
    "apple inc",  # Exact match (normalized)
    "IBM",  # Acronym match
    "microsoft corp",  # Fuzzy match
    "amazon",  # Alias match
    "AAPL",  # Ticker symbol (alias)
]

header = "Mode A: Sequential Pipeline with Early Stopping"
if not semantic_available:
    header += " (No Semantic Matching)"
    
print(header)
print("=" * 60)

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

batch_mentions = ["apple", "msft", "big blue"]
results = resolver.resolve_batch(batch_mentions)

for result in results:
    if result.matched_entity:
        print(f"{result.mention.text:15} -> {result.matched_entity.canonical_name}")
