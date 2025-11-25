"""Configuration management for NER library."""

from typing import Dict, Optional
from pydantic import BaseModel, Field


class ThresholdsConfig(BaseModel):
    """Confidence thresholds for decision making."""
    
    # Mode A thresholds
    high_acronym: float = Field(default=0.9, ge=0.0, le=1.0, description="High confidence acronym match")
    high_fuzzy: float = Field(default=0.9, ge=0.0, le=1.0, description="High confidence fuzzy match")
    auto_merge: float = Field(default=0.85, ge=0.0, le=1.0, description="Auto-merge threshold")
    review_low: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum threshold for review queue")
    
    # Mode B thresholds
    mode_b_auto_merge: float = Field(default=0.9, ge=0.0, le=1.0, description="Mode B auto-merge threshold")
    mode_b_auto_link: float = Field(default=0.7, ge=0.0, le=1.0, description="Mode B auto-link threshold")
    mode_b_review: float = Field(default=0.45, ge=0.0, le=1.0, description="Mode B review threshold")


class ModeBWeights(BaseModel):
    """Weights for Mode B signal aggregation."""
    
    exact_match: float = Field(default=0.40, description="Exact/alias match weight")
    embedding_cosine: float = Field(default=0.30, description="Semantic embedding similarity weight")
    token_set_ratio: float = Field(default=0.10, description="Fuzzy token set ratio weight")
    acronym: float = Field(default=0.10, description="Acronym match weight")
    contextual_boost: float = Field(default=0.20, description="Contextual signals boost (additive)")


class ANNConfig(BaseModel):
    """Configuration for ANN search."""
    
    top_k: int = Field(default=10, ge=1, description="Number of candidates to retrieve")
    index_type: str = Field(default="faiss", description="ANN library to use: 'faiss' or 'hnswlib'")
    metric: str = Field(default="cosine", description="Distance metric: 'cosine' or 'l2'")
    
    # HNSW-specific
    hnsw_ef_construction: int = Field(default=200, ge=1, description="HNSW construction parameter")
    hnsw_m: int = Field(default=16, ge=1, description="HNSW M parameter")
    hnsw_ef_search: int = Field(default=50, ge=1, description="HNSW search parameter")


class ModelConfig(BaseModel):
    """Configuration for ML models."""
    
    sentence_transformer_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="SentenceTransformer model name"
    )
    embedding_dim: Optional[int] = Field(default=None, description="Embedding dimension (auto-detected if None)")
    device: str = Field(default="cpu", description="Device for model inference: 'cpu' or 'cuda'")


class NormalizationConfig(BaseModel):
    """Configuration for text normalization."""
    
    legal_suffixes: list[str] = Field(
        default_factory=lambda: [
            "inc", "ltd", "llc", "corp", "corporation", "company", "co",
            "limited", "gmbh", "ag", "sa", "plc", "pvt", "pty"
        ],
        description="Legal suffixes to strip from entity names"
    )
    lowercase: bool = Field(default=True, description="Convert to lowercase")
    strip_punctuation: bool = Field(default=True, description="Remove punctuation")
    collapse_whitespace: bool = Field(default=True, description="Collapse multiple spaces")


class WikidataConfig(BaseModel):
    """Configuration for Wikidata API integration."""
    
    api_endpoint: str = Field(
        default="https://www.wikidata.org/w/api.php",
        description="Wikidata API endpoint"
    )
    search_limit: int = Field(default=10, ge=1, le=50, description="Number of entities per search")
    requests_per_minute: int = Field(default=10000, ge=1, description="Rate limit for API requests")
    cache_ttl_seconds: int = Field(default=3600, ge=0, description="Cache TTL in seconds (0 = no expiration)")
    cache_maxsize: int = Field(default=1000, ge=0, description="Maximum cache size (0 = unlimited)")
    timeout_seconds: int = Field(default=10, ge=1, description="Request timeout in seconds")


class SynonymConfig(BaseModel):
    """Configuration for synonym retrieval."""
    
    max_synonyms: int = Field(default=5, ge=1, description="Maximum number of synonyms to return")
    use_spacy_wordnet: bool = Field(default=True, description="Use spacy-wordnet for synonyms")
    use_nltk_fallback: bool = Field(default=True, description="Use NLTK WordNet as fallback")
    filter_by_pos: bool = Field(default=True, description="Filter synonyms by part-of-speech")


class SemanticMatchingConfig(BaseModel):
    """Configuration for semantic matching using embeddings."""
    
    enabled: bool = Field(default=False, description="Enable semantic matching for canonicalization")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum cosine similarity for match")
    model_name: str = Field(default="all-MiniLM-L6-v2", description="Sentence transformer model for embeddings")
    cache_embeddings: bool = Field(default=True, description="Cache embeddings for canonical terms")
    # Canonical schemas (optional - can be set at runtime)
    canonical_relationships: list[str] = Field(default_factory=list, description="List of canonical relationship names")
    canonical_properties: list[str] = Field(default_factory=list, description="List of canonical property names")


class Config(BaseModel):
    """Main configuration for NER library."""
    
    thresholds: ThresholdsConfig = Field(default_factory=ThresholdsConfig)
    mode_b_weights: ModeBWeights = Field(default_factory=ModeBWeights)
    ann: ANNConfig = Field(default_factory=ANNConfig)
    models: ModelConfig = Field(default_factory=ModelConfig)
    normalization: NormalizationConfig = Field(default_factory=NormalizationConfig)
    wikidata: WikidataConfig = Field(default_factory=WikidataConfig)
    synonyms: SynonymConfig = Field(default_factory=SynonymConfig)
    semantic_matching: SemanticMatchingConfig = Field(default_factory=SemanticMatchingConfig)
    
    # General settings
    mode: str = Field(default="A", description="Operational mode: 'A' or 'B'")
    enable_citations: bool = Field(default=True, description="Track and return citations")
    
    class Config:
        """Pydantic config."""
        validate_assignment = True


# Default configuration instance
DEFAULT_CONFIG = Config()
