from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="advanced-text-processing",
    version="0.2.1",
    author="Gaurav Dadhich",
    description="A powerful Named Entity Recognition and Resolution library with semantic matching",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dadhichgaurav1/advanced-text-processing",
    project_urls={
        "Bug Tracker": "https://github.com/dadhichgaurav1/advanced-text-processing/issues",
        "Documentation": "https://github.com/dadhichgaurav1/advanced-text-processing#readme",
        "Source Code": "https://github.com/dadhichgaurav1/advanced-text-processing",
        "Changelog": "https://github.com/dadhichgaurav1/advanced-text-processing/blob/main/CHANGELOG.md",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "gv"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="ner named-entity-recognition entity-resolution nlp semantic-matching canonicalization",
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.4.0",
            "isort>=5.12.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
            "myst-parser>=2.0.0",
        ],
    },
)
