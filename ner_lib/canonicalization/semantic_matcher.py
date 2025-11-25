"""Semantic matching using sentence embeddings for canonicalization."""

from typing import List, Optional, Tuple
import logging
import numpy as np

logger = logging.getLogger(__name__)


class SemanticMatcher:
    """
    Semantic matcher using sentence embeddings for finding canonical forms.
    
    Uses cosine similarity to match input text against a predefined schema
    of canonical terms.
    """
    
    def __init__(
        self,
        canonical_terms: List[str],
        model_name: str = "all-MiniLM-L6-v2",
        similarity_threshold: float = 0.7,
        cache_embeddings: bool = True
    ):
        """
        Initialize semantic matcher.
        
        Args:
            canonical_terms: List of canonical terms to match against
            model_name: Name of sentence transformer model
            similarity_threshold: Minimum cosine similarity for a match
            cache_embeddings: Whether to cache embeddings
        """
        self.canonical_terms = canonical_terms
        self.model_name = model_name
        self.similarity_threshold = similarity_threshold
        self.cache_embeddings = cache_embeddings
        
        # Lazy load model and embeddings
        self._model = None
        self._canonical_embeddings = None
        
        if not canonical_terms:
            logger.warning("SemanticMatcher initialized with empty canonical_terms")
    
    @property
    def model(self):
        """Lazy load sentence transformer model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading sentence transformer model: {self.model_name}")
                self._model = SentenceTransformer(self.model_name)
            except ImportError:
                logger.error("sentence-transformers not installed. Install with: pip install sentence-transformers")
                raise
        return self._model
    
    @property
    def canonical_embeddings(self):
        """Lazy compute canonical embeddings."""
        if self._canonical_embeddings is None and self.canonical_terms:
            logger.info(f"Computing embeddings for {len(self.canonical_terms)} canonical terms...")
            self._canonical_embeddings = self.model.encode(
                self.canonical_terms,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            logger.info(f"Embeddings computed: shape {self._canonical_embeddings.shape}")
        return self._canonical_embeddings
    
    def find_best_match(
        self,
        input_text: str,
        top_k: int = 1,
        return_score: bool = False
    ) -> Optional[str] | Tuple[Optional[str], float]:
        """
        Find the best matching canonical term for input text.
        
        Args:
            input_text: Text to match
            top_k: Number of top matches to consider (default: 1)
            return_score: Whether to return similarity score
            
        Returns:
            Best matching canonical term, or None if no match above threshold.
            If return_score=True, returns (term, score) tuple.
        """
        if not self.canonical_terms:
            return (None, 0.0) if return_score else None
        
        try:
            # Encode input
            input_embedding = self.model.encode(
                [input_text],
                convert_to_numpy=True,
                show_progress_bar=False
            )
            
            # Compute cosine similarity
            similarities = self._cosine_similarity(input_embedding, self.canonical_embeddings)
            
            # Get best match
            best_idx = similarities[0].argmax()
            best_score = similarities[0, best_idx]
            
            if best_score >= self.similarity_threshold:
                best_term = self.canonical_terms[best_idx]
                logger.debug(f"Matched '{input_text}' -> '{best_term}' (score: {best_score:.3f})")
                return (best_term, float(best_score)) if return_score else best_term
            else:
                logger.debug(f"No match for '{input_text}' (best score: {best_score:.3f} < {self.similarity_threshold})")
                return (None, float(best_score)) if return_score else None
                
        except Exception as e:
            logger.error(f"Error in semantic matching for '{input_text}': {e}")
            return (None, 0.0) if return_score else None
    
    def find_top_k_matches(
        self,
        input_text: str,
        k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find top-k matching canonical terms.
        
        Args:
            input_text: Text to match
            k: Number of top matches to return
            
        Returns:
            List of (term, score) tuples, sorted by score descending
        """
        if not self.canonical_terms:
            return []
        
        try:
            # Encode input
            input_embedding = self.model.encode(
                [input_text],
                convert_to_numpy=True,
                show_progress_bar=False
            )
            
            # Compute cosine similarity
            similarities = self._cosine_similarity(input_embedding, self.canonical_embeddings)
            
            # Get top-k indices
            top_k_indices = similarities[0].argsort()[-k:][::-1]
            
            # Filter by threshold and return
            results = []
            for idx in top_k_indices:
                score = similarities[0, idx]
                if score >= self.similarity_threshold:
                    results.append((self.canonical_terms[idx], float(score)))
            
            return results
            
        except Exception as e:
            logger.error(f"Error in top-k matching for '{input_text}': {e}")
            return []
    
    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Compute cosine similarity between two embedding matrices.
        
        Args:
            a: Matrix of shape (n, d)
            b: Matrix of shape (m, d)
            
        Returns:
            Similarity matrix of shape (n, m)
        """
        # Normalize
        a_norm = a / np.linalg.norm(a, axis=1, keepdims=True)
        b_norm = b / np.linalg.norm(b, axis=1, keepdims=True)
        
        # Dot product
        return np.dot(a_norm, b_norm.T)
    
    def clear_cache(self):
        """Clear cached embeddings."""
        self._canonical_embeddings = None
        logger.info("Cleared cached embeddings")
    
    def update_canonical_terms(self, new_terms: List[str]):
        """
        Update canonical terms and recompute embeddings.
        
        Args:
            new_terms: New list of canonical terms
        """
        self.canonical_terms = new_terms
        self.clear_cache()
        # Trigger recomputation
        _ = self.canonical_embeddings
