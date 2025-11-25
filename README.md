# Advanced Text Processing

[![PyPI version](https://img.shields.io/pypi/v/advanced-text-processing.svg)](https://pypi.org/project/advanced-text-processing/)
[![Python Versions](https://img.shields.io/pypi/pyversions/advanced-text-processing.svg)](https://pypi.org/project/advanced-text-processing/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful **Named Entity Recognition (NER)** and **Entity Resolution** library designed for complex text processing tasks. It combines state-of-the-art NLP models (spaCy, Transformers) with robust knowledge bases (Wikidata, WordNet) to provide accurate entity extraction, canonicalization, and semantic matching.

## 🚀 Features

- **Advanced Entity Resolution**:
  - **Mode A (Sequential)**: Fast, early-stopping pipeline for high-confidence matches.
  - **Mode B (Parallel)**: Aggregates multiple signals (fuzzy, semantic, contextual) for difficult cases.
- **Semantic Matching**: Maps inputs to canonical schemas using sentence embeddings (SentenceTransformers).
- **Alias Retrieval**: Automatically fetches aliases from Wikidata and synonyms from WordNet.
- **Canonicalization**:
  - Entities (e.g., "Apple" -> "Apple Inc.")
  - Relationships (e.g., "relies on" -> "depends_on")
  - Properties (e.g., "birth date" -> "date_of_birth")
- **Flexible Candidate Generation**: Supports exact lookup, fulltext blocking, and ANN search (FAISS/hnswlib).

## 📦 Installation

```bash
pip install advanced-text-processing
```

After installation, download the required models:

```bash
# Download spaCy model
python -m spacy download en_core_web_lg

# Download NLTK data
python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"
```

See [Installation Guide](docs/INSTALLATION.md) for detailed instructions.

## ⚡ Quick Start

### Named Entity Recognition

```python
from ner_lib import recognize_entities

text = "Apple Inc. was founded by Steve Jobs in Cupertino."
result = recognize_entities(text)

for entity in result['entities']:
    print(f"{entity['text']} ({entity['type']})")
# Output:
# Apple Inc. (ORG)
# Steve Jobs (PERSON)
# Cupertino (GPE)
```

### Entity Canonicalization

```python
from ner_lib import canonicalize_entity

# Canonicalize an entity mention
result = canonicalize_entity("apple inc", mode="progressive")
print(f"Canonical: {result['canonical_name']}")
print(f"Aliases: {result['aliases']}")
# Output: 
# Canonical: Apple Inc.
# Aliases: ['Apple', 'AAPL', 'Apple Computer', ...]
```

### Relationship Canonicalization

```python
from ner_lib import Config, canonicalize_relationship

# Configure semantic matching
config = Config()
config.semantic_matching.enabled = True
config.semantic_matching.canonical_relationships = ["depends_on", "created_by"]

# Canonicalize a relationship phrase
result = canonicalize_relationship("relies heavily on", config=config)
print(f"Canonical: {result['canonical_name']}")
# Output: Canonical: depends_on
```

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [API Reference](docs/API.md)
- [System Architecture](docs/ARCHITECTURE.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to get started.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

This library stands on the shoulders of giants. We gratefully acknowledge the following open-source projects:

- **[spaCy](https://spacy.io/)**: For industrial-strength NLP.
- **[Sentence Transformers](https://www.sbert.net/)**: For state-of-the-art text embeddings.
- **[Wikidata](https://www.wikidata.org/)**: For the comprehensive knowledge base.
- **[NLTK](https://www.nltk.org/)** & **[WordNet](https://wordnet.princeton.edu/)**: For lexical database support.

See [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md) for the full list of dependencies and credits.
