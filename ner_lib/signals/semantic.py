"""Semantic similarity using SentenceTransformers."""

from typing import List, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer

from ner_lib.models.candidate import Citation


class EmbeddingModel:
    """Wrapper for SentenceTransformer embedding model."""
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str = "cpu"
    ):
        """
        Initialize embedding model.
        
        Args:
            model_name: SentenceTransformer model name
            device: 'cpu' or 'cuda'
        """
        self.model_name = model_name
        self.device = device
        self._model: Optional[SentenceTransformer] = None
        self._embedding_dim: Optional[int] = None
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the model."""
        if self._model is None:
            self._model = SentenceTransformer(self.model_name, device=self.device)
            # Get embedding dimension
            self._embedding_dim = self._model.get_sentence_embedding_dimension()
        return self._model
    
    @property
    def embedding_dim(self) -> int:
        """Get embedding dimension."""
        if self._embedding_dim is None:
            _ = self.model  # Trigger lazy load
        return self._embedding_dim
    
    def encode(
        self,
        texts: List[str] | str,
        batch_size: int = 32,
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Generate embeddings for texts.
        
        Args:
            texts: Single text or list of texts
            batch_size: Batch size for encoding
            show_progress: Whether to show progress bar
        
        Returns:
            Embeddings array of shape (n, embedding_dim) or (embedding_dim,)
        """
        if isinstance(texts, str):
            texts = [texts]
            return_single = True
        else:
            return_single = False
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        
        if return_single:
            return embeddings[0]
        return embeddings


def cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """
    Compute cosine similarity between two embeddings.
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
    
    Returns:
        Cosine similarity score 0-1
    
    Citation: SentenceTransformers
    """
    # Normalize vectors
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    # Compute cosine similarity
    similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
    
    # Convert from [-1, 1] to [0, 1]
    similarity = (similarity + 1.0) / 2.0
    
    # Clip to [0, 1]
    return float(np.clip(similarity, 0.0, 1.0))


def batch_cosine_similarity(
    query_embedding: np.ndarray,
    candidate_embeddings: np.ndarray
) -> np.ndarray:
    """
    Compute cosine similarity between query and multiple candidates.
    
    Args:
        query_embedding: Query embedding of shape (embedding_dim,)
        candidate_embeddings: Candidate embeddings of shape (n, embedding_dim)
    
    Returns:
        Similarity scores of shape (n,)
    """
    # Normalize query
    query_norm = query_embedding / np.linalg.norm(query_embedding)
    
    # Normalize candidates
    candidate_norms = candidate_embeddings / np.linalg.norm(
        candidate_embeddings, axis=1, keepdims=True
    )
    
    # Compute dot products
    similarities = np.dot(candidate_norms, query_norm)
    
    # Convert from [-1, 1] to [0, 1]
    similarities = (similarities + 1.0) / 2.0
    
    return np.clip(similarities, 0.0, 1.0)


def semantic_similarity_score(
    mention: str,
    canonical_name: str,
    embedding_model: EmbeddingModel
) -> Tuple[float, Citation]:
    """
    Compute semantic similarity using embeddings.
    
    Args:
        mention: Mention text
        canonical_name: Canonical entity name
        embedding_model: Embedding model instance
    
    Returns:
        Tuple of (similarity_score, citation)
    """
    # Generate embeddings
    embeddings = embedding_model.encode([mention, canonical_name])
    
    # Compute similarity
    score = cosine_similarity(embeddings[0], embeddings[1])
    
    # Create citation
    citation = Citation(
        source="SentenceTransformers",
        method=f"embedding_cosine ({embedding_model.model_name})",
        component="semantic",
        confidence_contribution=score
    )
    
    return score, citation
