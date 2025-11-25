# Acknowledgements

This project builds upon the excellent work of many open-source libraries and their maintainers. We are grateful for their contributions to the community.

## Core NLP and Machine Learning

### spaCy
- **Purpose**: Industrial-strength Natural Language Processing
- **License**: MIT License
- **Website**: https://spacy.io
- **Repository**: https://github.com/explosion/spaCy
- **Maintainer**: Explosion AI
- **Usage**: Named entity recognition, part-of-speech tagging, lemmatization, and linguistic analysis

### Sentence Transformers
- **Purpose**: State-of-the-art sentence, text and image embeddings
- **License**: Apache License 2.0
- **Website**: https://www.sbert.net
- **Repository**: https://github.com/UKPLab/sentence-transformers
- **Maintainer**: UKP Lab, TU Darmstadt
- **Usage**: Semantic similarity computation and embedding generation

### Transformers (Hugging Face)
- **Purpose**: State-of-the-art Machine Learning for PyTorch, TensorFlow, and JAX
- **License**: Apache License 2.0
- **Website**: https://huggingface.co/transformers
- **Repository**: https://github.com/huggingface/transformers
- **Maintainer**: Hugging Face
- **Usage**: Pre-trained transformer models and tokenizers

## Knowledge Bases and Linguistic Resources

### Wikidata
- **Purpose**: Free and open knowledge base
- **License**: CC0 (Public Domain)
- **Website**: https://www.wikidata.org
- **API**: https://www.wikidata.org/w/api.php
- **Maintainer**: Wikimedia Foundation
- **Usage**: Entity alias retrieval and entity information lookup

### WordNet (via NLTK)
- **Purpose**: Large lexical database of English
- **License**: WordNet License (permissive)
- **Website**: https://wordnet.princeton.edu
- **Maintainer**: Princeton University
- **Usage**: Synonym retrieval for relationships, properties, and values

### spacy-wordnet
- **Purpose**: WordNet integration for spaCy
- **License**: MIT License
- **Repository**: https://github.com/recognai/spacy-wordnet
- **Maintainer**: Recognai
- **Usage**: Seamless WordNet access within spaCy pipeline

### NLTK (Natural Language Toolkit)
- **Purpose**: Leading platform for building Python programs to work with human language data
- **License**: Apache License 2.0
- **Website**: https://www.nltk.org
- **Repository**: https://github.com/nltk/nltk
- **Maintainer**: NLTK Project
- **Usage**: WordNet access and linguistic utilities

## Vector Search and Indexing

### FAISS (Facebook AI Similarity Search)
- **Purpose**: Efficient similarity search and clustering of dense vectors
- **License**: MIT License
- **Repository**: https://github.com/facebookresearch/faiss
- **Maintainer**: Meta AI Research
- **Usage**: Approximate nearest neighbor search for entity candidates

### hnswlib
- **Purpose**: Header-only C++/python library for fast approximate nearest neighbors
- **License**: Apache License 2.0
- **Repository**: https://github.com/nmslib/hnswlib
- **Maintainer**: nmslib
- **Usage**: Alternative ANN search implementation

### autofaiss
- **Purpose**: Automatically create FAISS indices with optimal configuration
- **License**: Apache License 2.0
- **Repository**: https://github.com/criteo/autofaiss
- **Maintainer**: Criteo
- **Usage**: Simplified FAISS index creation and optimization

## String Matching and Similarity

### RapidFuzz
- **Purpose**: Rapid fuzzy string matching
- **License**: MIT License
- **Repository**: https://github.com/maxbachmann/RapidFuzz
- **Maintainer**: Max Bachmann
- **Usage**: Fast fuzzy string matching and similarity scoring

### Jellyfish
- **Purpose**: Python library for approximate and phonetic matching of strings
- **License**: BSD License
- **Repository**: https://github.com/jamesturk/jellyfish
- **Maintainer**: James Turk
- **Usage**: Phonetic encoding and string distance metrics

### FlashText
- **Purpose**: Extract keywords from sentence or replace keywords in sentences
- **License**: MIT License
- **Repository**: https://github.com/vi3k6i5/flashtext
- **Maintainer**: Vikash Singh
- **Usage**: Fast keyword extraction and matching

## Entity Resolution and Record Linkage

### Dedupe
- **Purpose**: Python library for accurate and scalable fuzzy matching, record deduplication and entity-resolution
- **License**: MIT License
- **Repository**: https://github.com/dedupeio/dedupe
- **Maintainer**: Dedupe.io
- **Usage**: Advanced entity resolution algorithms

### RecordLinkage
- **Purpose**: Python Record Linkage Toolkit for linking and deduplicating records
- **License**: BSD License
- **Repository**: https://github.com/J535D165/recordlinkage
- **Maintainer**: Jonathan de Bruin
- **Usage**: Record linkage and deduplication utilities

## HTTP and API Integration

### Requests
- **Purpose**: HTTP library for Python
- **License**: Apache License 2.0
- **Repository**: https://github.com/psf/requests
- **Maintainer**: Python Software Foundation
- **Usage**: HTTP requests to external APIs (Wikidata)

### requests-ratelimiter
- **Purpose**: Rate limiting for the requests library
- **License**: MIT License
- **Repository**: https://github.com/JWCook/requests-ratelimiter
- **Maintainer**: Jordan Cook
- **Usage**: Rate limiting for Wikidata API requests

### cachetools
- **Purpose**: Extensible memoizing collections and decorators
- **License**: MIT License
- **Repository**: https://github.com/tkem/cachetools
- **Maintainer**: Thomas Kemmer
- **Usage**: Caching for API responses and embeddings

## Data Processing

### Pandas
- **Purpose**: Powerful data structures for data analysis
- **License**: BSD License
- **Website**: https://pandas.pydata.org
- **Repository**: https://github.com/pandas-dev/pandas
- **Maintainer**: Pandas Development Team
- **Usage**: Data manipulation and analysis

### NumPy
- **Purpose**: Fundamental package for scientific computing with Python
- **License**: BSD License
- **Website**: https://numpy.org
- **Repository**: https://github.com/numpy/numpy
- **Maintainer**: NumPy Developers
- **Usage**: Numerical computations and array operations

## Configuration and Utilities

### Pydantic
- **Purpose**: Data validation using Python type annotations
- **License**: MIT License
- **Repository**: https://github.com/pydantic/pydantic
- **Maintainer**: Samuel Colvin
- **Usage**: Configuration validation and data models

### python-dotenv
- **Purpose**: Read key-value pairs from .env file and set them as environment variables
- **License**: BSD License
- **Repository**: https://github.com/theskumar/python-dotenv
- **Maintainer**: Saurabh Kumar
- **Usage**: Environment variable management

## Development Tools

### pytest
- **Purpose**: Testing framework
- **License**: MIT License
- **Repository**: https://github.com/pytest-dev/pytest
- **Maintainer**: pytest-dev
- **Usage**: Unit testing and test automation

### Black
- **Purpose**: The uncompromising Python code formatter
- **License**: MIT License
- **Repository**: https://github.com/psf/black
- **Maintainer**: Python Software Foundation
- **Usage**: Code formatting

## Special Thanks

We would like to extend special thanks to:

- The **Explosion AI** team for spaCy and their excellent documentation
- The **Hugging Face** community for democratizing access to state-of-the-art NLP models
- The **Wikimedia Foundation** for maintaining Wikidata as a free knowledge resource
- All the open-source contributors who maintain these incredible libraries

## Citation

If you use this library in your research or projects, please consider citing the underlying libraries as well. Many of them have specific citation requirements listed in their respective documentation.

---

**Note**: This list represents the direct dependencies of this project. Each of these libraries may have their own dependencies. We are grateful to the entire open-source ecosystem that makes this work possible.

**License Compliance**: All libraries used in this project are compatible with the MIT License. Users are responsible for ensuring compliance with individual library licenses when using this software.
