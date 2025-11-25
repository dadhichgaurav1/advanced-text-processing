# Contributing to Advanced Text Processing

Thank you for your interest in contributing to Advanced Text Processing! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone git@github.com:YOUR_USERNAME/advanced-text-processing.git
   cd advanced-text-processing
   ```
3. **Add the upstream repository**:
   ```bash
   git remote add upstream git@github.com:dadhichgaurav1/advanced-text-processing.git
   ```

## Development Setup

### Prerequisites

- Python 3.9 or higher
- pip or conda for package management
- Git for version control

### Installation

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install the package in development mode with all dependencies**:
   ```bash
   pip install -e ".[dev,docs]"
   ```

3. **Download required models and data**:
   ```bash
   # Download spaCy model
   python -m spacy download en_core_web_lg
   
   # Download NLTK data
   python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"
   ```

4. **Verify installation**:
   ```bash
   pytest tests/ -v
   ```

## How to Contribute

### Types of Contributions

We welcome many types of contributions:

- **Bug fixes**: Fix issues in the codebase
- **New features**: Add new functionality
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve test coverage
- **Examples**: Add usage examples
- **Performance improvements**: Optimize existing code

### Contribution Workflow

1. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes** following our coding standards

3. **Write or update tests** for your changes

4. **Run the test suite** to ensure everything passes:
   ```bash
   pytest tests/ -v --cov=ner_lib
   ```

5. **Format your code**:
   ```bash
   black ner_lib tests examples
   isort ner_lib tests examples
   ```

6. **Commit your changes** with a clear commit message:
   ```bash
   git commit -m "Add feature: brief description"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request** on GitHub

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use [Black](https://black.readthedocs.io/) for code formatting (line length: 100)
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Use type hints where appropriate
- Write docstrings for all public functions, classes, and modules

### Code Formatting

We use Black for consistent code formatting:

```bash
# Format all code
black ner_lib tests examples

# Check formatting without making changes
black --check ner_lib tests examples
```

### Import Sorting

We use isort to keep imports organized:

```bash
# Sort imports
isort ner_lib tests examples

# Check import sorting
isort --check-only ner_lib tests examples
```

### Docstring Format

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """Brief description of the function.
    
    Longer description if needed, explaining the function's purpose,
    behavior, and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param2 is negative
        
    Example:
        >>> example_function("test", 5)
        True
    """
    pass
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=ner_lib --cov-report=html

# Run specific test file
pytest tests/test_resolver.py -v

# Run specific test
pytest tests/test_resolver.py::test_entity_resolution -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names that explain what is being tested
- Include both positive and negative test cases
- Mock external API calls (Wikidata, etc.)

Example test:

```python
def test_canonicalize_relationship():
    """Test relationship canonicalization with various inputs."""
    result = canonicalize_relationship("is running")
    assert result['canonical_name'] == "running"
    assert result['lemma'] == "run"
    assert isinstance(result['aliases'], list)
```

## Pull Request Process

1. **Update documentation** if you're changing functionality
2. **Add tests** for new features or bug fixes
3. **Update CHANGELOG.md** with your changes
4. **Ensure all tests pass** and code is formatted
5. **Write a clear PR description** explaining:
   - What changes you made
   - Why you made them
   - How to test them
6. **Link related issues** using keywords like "Fixes #123"
7. **Be responsive** to review feedback

### PR Checklist

Before submitting your PR, ensure:

- [ ] Code follows the style guide
- [ ] Code is formatted with Black and isort
- [ ] All tests pass
- [ ] New tests are added for new functionality
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Commit messages are clear and descriptive

## Reporting Bugs

### Before Submitting a Bug Report

- Check the [issue tracker](https://github.com/dadhichgaurav1/advanced-text-processing/issues) for existing reports
- Try to reproduce the issue with the latest version
- Collect relevant information (Python version, OS, error messages, etc.)

### Submitting a Bug Report

Use the bug report template and include:

- **Clear title** describing the issue
- **Steps to reproduce** the bug
- **Expected behavior**
- **Actual behavior**
- **Environment details** (Python version, OS, package version)
- **Code sample** demonstrating the issue
- **Error messages** or stack traces

## Suggesting Enhancements

We welcome feature suggestions! When suggesting an enhancement:

1. **Check existing issues** to avoid duplicates
2. **Use the feature request template**
3. **Explain the use case** and why it would be valuable
4. **Provide examples** of how it would work
5. **Consider implementation** if you're willing to contribute code

## Development Tips

### Useful Commands

```bash
# Install in editable mode
pip install -e .

# Run linting
flake8 ner_lib tests

# Type checking
mypy ner_lib

# Build documentation (if using Sphinx)
cd docs && make html

# Build distribution packages
python -m build
```

### Debugging

- Use `pytest -s` to see print statements during tests
- Use `pytest --pdb` to drop into debugger on failures
- Use logging instead of print statements in library code

## Questions?

If you have questions about contributing:

- Open a [discussion](https://github.com/dadhichgaurav1/advanced-text-processing/discussions)
- Ask in an issue
- Check existing documentation

## License

By contributing to Advanced Text Processing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Advanced Text Processing! 🎉
