# Publishing Guide

This guide outlines the process for releasing and publishing the **Advanced Text Processing** library to PyPI.

## Prerequisites

- Access to the PyPI account (or TestPyPI).
- `build` and `twine` installed:
  ```bash
  pip install build twine
  ```

## Versioning

We follow [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`

1. **Update Version Number**:
   - Edit `ner_lib/__init__.py`: `__version__ = "X.Y.Z"`
   - Edit `pyproject.toml`: `version = "X.Y.Z"`
   - Edit `setup.py`: `version="X.Y.Z"`

2. **Update Changelog**:
   - Add a new entry in `CHANGELOG.md` for the release.
   - Move "Unreleased" changes to the new version section.

## Building the Package

1. **Clean previous builds**:
   ```bash
   rm -rf dist/ build/ *.egg-info
   ```

2. **Build Source and Wheel distributions**:
   ```bash
   python -m build
   ```
   This will create `.tar.gz` and `.whl` files in the `dist/` directory.

3. **Check the distribution**:
   ```bash
   twine check dist/*
   ```
   Ensure there are no errors in the metadata or README rendering.

## Testing the Release

Before publishing to the real PyPI, test with TestPyPI:

1. **Upload to TestPyPI**:
   ```bash
   twine upload --repository testpypi dist/*
   ```

2. **Verify Installation**:
   Create a fresh virtual environment and try installing:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --no-deps advanced-text-processing
   ```

## Publishing to PyPI

1. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```
   You will be prompted for your PyPI username and password (or API token).

2. **Verify on PyPI**:
   Check the project page: https://pypi.org/project/advanced-text-processing/

## Post-Release

1. **Tag the Release in Git**:
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```

2. **Create GitHub Release**:
   - Go to "Releases" on GitHub.
   - Draft a new release using the tag.
   - Copy the changelog entry into the release description.
