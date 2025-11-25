# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2025-11-26

### Fixed
- **Critical Dependency Fix**: Constrained nltk version to `>=3.3,<3.6` to resolve installation conflict with spacy-wordnet 0.1.0
  - Previously, the open-ended `nltk>=3.3` requirement caused pip installation failures
  - This fix ensures compatibility across all dependencies

## [0.2.0] - 2025-11-25

### Added
- **Semantic Matching**: In-memory semantic matching using sentence embeddings for canonicalization
  - Configurable similarity threshold
  - Support for custom canonical schemas (relationships and properties)
  - Embedding caching for performance
  - Integration with relationship and property canonicalization
- New `SemanticMatchingConfig` class for configuration
- New `SemanticMatcher` class for embedding-based matching
- Comprehensive semantic matching documentation in `SEMANTIC_MATCHING_README.md`

### Changed
- Enhanced `canonicalize_relationship()` to support semantic matching
- Enhanced `canonicalize_property_name()` to support semantic matching
- Updated configuration system to include semantic matching options
- Improved canonicalization accuracy with hybrid approach (syntax-aware + semantic + WordNet)

### Fixed
- Property canonicalization now correctly processes nouns instead of adjectives for property values
- Improved handling of multi-word expressions in canonicalization

## [0.1.0] - 2025-11-22

### Added
- **Core Entity Resolution**:
  - Mode A: Sequential pipeline with early stopping for high-confidence matches
  - Mode B: Parallel signal aggregation for comprehensive analysis
  - Multiple signal types: deterministic, string similarity, semantic, contextual
  - Flexible candidate generation: exact lookup, fulltext blocking, ANN search (Faiss/hnswlib)

- **Named Entity Recognition**:
  - `recognize_entities()` function using spaCy
  - Support for multiple entity types (PERSON, ORG, GPE, etc.)

- **Alias Retrieval**:
  - `get_aliases()` function for retrieving aliases from Wikidata and WordNet
  - Support for named entities, relationships, property names, and property values
  - Wikidata API integration with rate limiting and caching
  - WordNet integration via spacy-wordnet and NLTK

- **Canonicalization**:
  - `canonicalize_entity()`: Normalize entities using Mode A/B resolution
  - `canonicalize_relationship()`: Canonicalize verbs with tense handling
  - `canonicalize_property_name()`: Canonicalize adjective-based property names
  - `canonicalize_property_value()`: Canonicalize noun-based property values

- **Configuration System**:
  - Comprehensive `Config` class with Pydantic validation
  - Configurable thresholds, weights, and model parameters
  - Support for custom normalization rules

- **Storage & Indexing**:
  - In-memory storage implementation
  - FAISS and hnswlib ANN index support
  - Efficient candidate retrieval

- **Testing**:
  - Comprehensive test suite
  - Example scripts demonstrating all features

### Dependencies
- spaCy >= 3.7.0
- sentence-transformers >= 2.2.0
- transformers >= 4.30.0
- spacy-wordnet >= 0.1.0
- nltk >= 3.8.0
- requests >= 2.31.0
- faiss-cpu >= 1.7.4
- hnswlib >= 0.7.0
- rapidfuzz >= 3.0.0
- And more (see requirements.txt)

## [Unreleased]

### Planned
- Vector database integration (Pinecone, Weaviate)
- Advanced ANN indexing strategies
- Multi-language support
- REST API wrapper
- Web UI for entity management

---

[0.2.1]: https://github.com/dadhichgaurav1/advanced-text-processing/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/dadhichgaurav1/advanced-text-processing/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/dadhichgaurav1/advanced-text-processing/releases/tag/v0.1.0
