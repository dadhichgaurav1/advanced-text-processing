"""
Example: Mode B - Parallel Signal Aggregation
"""

from ner_lib import EntityResolver
from ner_lib.models.candidate import NextSteps

# Initialize resolver in Mode B
resolver = EntityResolver(mode='B')

# Add known entities with more metadata
companies = [
    {
        "canonical_name": "Apple Inc.",
        "aliases": ["Apple", "AAPL", "Apple Computer"],
        "metadata": {
            "domain": "apple.com",
            "industry": "Technology",
            "founded": "1976",
            "location": "Cupertino, CA"
        }
    },
    {
        "canonical_name": "Microsoft Corporation",
        "aliases": ["Microsoft", "MSFT", "MS"],
        "metadata": {
            "domain": "microsoft.com",
            "industry": "Technology",
            "founded": "1975",
            "location": "Redmond, WA"
        }
    },
    {
        "canonical_name": "International Business Machines",
        "aliases": ["IBM", "Big Blue"],
        "metadata": {
            "domain": "ibm.com",
            "industry": "Technology",
            "founded": "1911",
            "location": "Armonk, NY"
        }
    },
    {
        "canonical_name": "Apple Records",
        "aliases": ["Apple Corps"],
        "metadata": {
            "domain": "applerecords.com",
            "industry": "Music",
            "founded": "1968",
            "location": "London, UK"
        }
    },
]

for company in companies:
    resolver.add_entity(
        canonical_name=company["canonical_name"],
        aliases=company["aliases"],
        metadata=company["metadata"]
    )

# Build semantic index
print("Building semantic index...")
try:
    resolver.build_semantic_index()
    print("Semantic index built successfully!\n")
    semantic_available = True
except ImportError as e:
    print(f"⚠ Semantic matching not available: {e}")
    print("Continuing with exact/fuzzy/acronym matching only...\n")
    semantic_available = False

# Test mentions with varying similarity
test_cases = [
    {
        "mention": "apple inc",
        "metadata": {"domain": "apple.com"},
        "description": "Exact match with domain boost"
    },
    {
        "mention": "apple",
        "metadata": {"industry": "Technology"},
        "description": "Ambiguous - could be Apple Inc. or Apple Records"
    },
    {
        "mention": "apple",
        "metadata": {"industry": "Music"},
        "description": "Ambiguous - contextual signal helps"
    },
    {
        "mention": "IBM",
        "metadata": {},
        "description": "Acronym match"
    },
    {
        "mention": "microsoft corporation",
        "metadata": {},
        "description": "Full name match"
    },
]

print("Mode B: Parallel Signal Aggregation")
print("=" * 80)

for test_case in test_cases:
    from ner_lib.models.entity import Mention
    
    mention = Mention(
        text=test_case["mention"],
        metadata=test_case["metadata"]
    )
    
    result = resolver.resolve(mention)
    
    print(f"\nTest: {test_case['description']}")
    print(f"Mention: '{mention.text}'")
    if mention.metadata:
        print(f"Context: {mention.metadata}")
    
    if result.matched_entity:
        print(f"  ✓ Matched: {result.matched_entity.canonical_name}")
        print(f"  Confidence: {result.confidence:.3f}")
        
        # Show signal breakdown
        if result.candidates:
            best = result.candidates[0]
            print(f"  Signal Breakdown:")
            for signal_name, signal_value in best.signals.items():
                if signal_value > 0:
                    print(f"    - {signal_name}: {signal_value:.3f}")
        
        print(f"  Next Steps: {result.next_steps.value}")
        
        # Show top 3 candidates
        if len(result.candidates) > 1:
            print(f"  Other Candidates:")
            for i, candidate in enumerate(result.candidates[1:4], 1):
                entity = resolver.get_entity(candidate.entity_id)
                if entity:
                    print(f"    {i}. {entity.canonical_name} ({candidate.final_score:.3f})")
    else:
        print(f"  ✗ No match found")
        print(f"  Next Steps: {result.next_steps.value}")

print("\n" + "=" * 80)
print("Review Queue:")
print("=" * 80)

# Check review queue
review_items = resolver.get_review_queue()
if review_items:
    for item in review_items:
        print(f"Mention: {item.mention.text}")
        print(f"Top candidates: {[resolver.get_entity(c.entity_id).canonical_name for c in item.candidates[:3]]}")
else:
    print("No items in review queue")
