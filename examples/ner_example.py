"""
Example: Named Entity Recognition

Demonstrates how to extract named entities from text using recognize_entities().
"""

from ner_lib import recognize_entities

# Sample text with various entity types
text = """
Apple Inc. was founded by Steve Jobs and Steve Wozniak in Cupertino, California.
The company released the iPhone in 2007, revolutionizing the smartphone industry.
Tim Cook became CEO in 2011, succeeding Steve Jobs. Apple's headquarters, Apple Park,
opened in 2017 in Cupertino. The company is now worth over $2 trillion.
"""

print("=" * 80)
print("Named Entity Recognition Example")
print("=" * 80)

print(f"\nInput Text:\n{text}")

# Recognize entities
result = recognize_entities(text)

print(f"\n{'=':=^80}")
print(f"Results")
print(f"{'=':=^80}")

print(f"\nTotal Entities Found: {result['total_entities']}")

print(f"\nEntity Types Distribution:")
for entity_type, count in result['entity_types'].items():
    print(f"  {entity_type:15} : {count}")

print(f"\n{'Detailed Entity List':-^80}")
print(f"{'Entity':<30} {'Type':<15} {'Count':<10}")
print("-" * 80)

for entity in result['entities']:
    print(f"{entity['text']:<30} {entity['type']:<15} {entity['count']:<10}")

print("\n" + "=" * 80)

# Example with shorter text
print("\n" + "=" * 80)
print("Short Text Example")
print("=" * 80)

short_text = "Microsoft and Google compete in the AI space. Satya Nadella leads Microsoft."
result2 = recognize_entities(short_text)

print(f"\nInput: {short_text}")
print(f"\nEntities:")
for entity in result2['entities']:
    print(f"  - {entity['text']} ({entity['type']})")
