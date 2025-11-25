# Installation Guide

This guide covers the installation process for the **Advanced Text Processing** library, including system requirements, installation methods, and post-installation setup.

## System Requirements

- **Operating System**: macOS, Linux, or Windows
- **Python Version**: 3.9, 3.10, 3.11, or 3.12
- **RAM**: Minimum 4GB recommended (8GB+ for optimal performance with large models)
- **Disk Space**: ~2GB for library and models (spaCy models, WordNet data, Sentence Transformers)

## Installation Methods

### Option 1: Install from PyPI (Recommended)

Once published, you can install the library directly from PyPI:

```bash
pip install advanced-text-processing
```

### Option 2: Install from Source

If you want the latest development version or want to contribute:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/dadhichgaurav1/advanced-text-processing.git
   cd advanced-text-processing
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in editable mode**:
   ```bash
   pip install -e .
   ```

## Post-Installation Setup

After installing the library, you need to download the required language models and data resources.

### 1. Download spaCy Model

We use the large English model (`en_core_web_lg`) for best accuracy:

```bash
python -m spacy download en_core_web_lg
```

### 2. Download NLTK Data

Required for WordNet synonym retrieval:

```bash
python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"
```

### 3. Verify Installation

You can verify that everything is set up correctly by running a simple script:

```python
from ner_lib import recognize_entities

text = "Apple Inc. was founded by Steve Jobs in Cupertino."
result = recognize_entities(text)

print(f"Found {result['total_entities']} entities:")
for entity in result['entities']:
    print(f"- {entity['text']} ({entity['type']})")
```

## Optional Dependencies

### Development Tools

If you plan to develop or run tests:

```bash
pip install advanced-text-processing[dev]
```

This installs `pytest`, `black`, `flake8`, `mypy`, and other development tools.

### Documentation Tools

If you want to build the documentation locally:

```bash
pip install advanced-text-processing[docs]
```

## Troubleshooting

### `ModuleNotFoundError: No module named '_lzma'`

This is a common issue with Python installations (especially pyenv on macOS) that affects the `sentence-transformers` library.

**Fix for macOS:**
```bash
brew install xz
pyenv uninstall <your-python-version>
pyenv install <your-python-version>
```

### `OSError: [E050] Can't find model 'en_core_web_lg'`

This means the spaCy model wasn't downloaded or isn't linked correctly.

**Fix:**
Run `python -m spacy download en_core_web_lg` again. If using a virtual environment, ensure it's activated.

### `LookupError: Resource wordnet not found`

This means the NLTK data wasn't downloaded.

**Fix:**
Run `python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"`
