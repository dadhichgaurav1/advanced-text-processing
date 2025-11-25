"""Faiss-based ANN search for candidate generation."""

from typing import List, Optional, Tuple
import numpy as np

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


class FaissIndex:
    """Faiss-based ANN index for entity embeddings."""
    
    def __init__(
        self,
        embedding_dim: int,
        index_type: str = "flat",
        metric: str = "cosine"
    ):
        """
        Initialize Faiss index.
        
        Args:
            embedding_dim: Dimension of embeddings
            index_type: Type of index ('flat' or 'ivf')
            metric: Distance metric ('cosine' or 'l2')
        """
        if not FAISS_AVAILABLE:
            raise ImportError("faiss not installed. Install with: pip install faiss-cpu")
        
        self.embedding_dim = embedding_dim
        self.index_type = index_type
        self.metric = metric
        
        # Create index
        if metric == "cosine":
            # For cosine similarity, use inner product on normalized vectors
            if index_type == "flat":
                self.index = faiss.IndexFlatIP(embedding_dim)
            else:
                # IVF index for larger datasets
                quantizer = faiss.IndexFlatIP(embedding_dim)
                self.index = faiss.IndexIVFFlat(quantizer, embedding_dim, 100)
        else:
            # L2 distance
            if index_type == "flat":
                self.index = faiss.IndexFlatL2(embedding_dim)
            else:
                quantizer = faiss.IndexFlatL2(embedding_dim)
                self.index = faiss.IndexIVFFlat(quantizer, embedding_dim, 100)
        
        self.entity_ids: List[str] = []
        self.is_trained = False
    
    def build_index(self, entity_ids: List[str], embeddings: np.ndarray):
        """
        Build index from entity embeddings.
        
        Args:
            entity_ids: List of entity IDs
            embeddings: Array of shape (n_entities, embedding_dim)
        """
        if embeddings.shape[0] != len(entity_ids):
            raise ValueError("Number of embeddings must match number of entity IDs")
        
        if embeddings.shape[1] != self.embedding_dim:
            raise ValueError(f"Embedding dimension mismatch: {embeddings.shape[1]} != {self.embedding_dim}")
        
        # Normalize embeddings if using cosine similarity
        if self.metric == "cosine":
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            embeddings = embeddings / np.maximum(norms, 1e-10)
        
        # Train IVF index if needed
        if self.index_type == "ivf" and not self.is_trained:
            self.index.train(embeddings.astype(np.float32))
            self.is_trained = True
        
        # Add vectors
        self.index.add(embeddings.astype(np.float32))
        self.entity_ids = entity_ids
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10
    ) -> Tuple[List[str], List[float]]:
        """
        Search for top-k nearest neighbors.
        
        Args:
            query_embedding: Query embedding of shape (embedding_dim,)
            top_k: Number of results to return
        
        Returns:
            Tuple of (entity_ids, scores)
        """
        if len(self.entity_ids) == 0:
            return [], []
        
        # Reshape query to (1, embedding_dim)
        query = query_embedding.reshape(1, -1)
        
        # Normalize if using cosine similarity
        if self.metric == "cosine":
            norm = np.linalg.norm(query)
            if norm > 0:
                query = query / norm
        
        # Search
        top_k = min(top_k, len(self.entity_ids))
        distances, indices = self.index.search(query.astype(np.float32), top_k)
        
        # Convert to entity IDs and scores
        entity_ids = [self.entity_ids[idx] for idx in indices[0]]
        
        # Convert distances to similarity scores
        if self.metric == "cosine":
            # Inner product is already similarity (0-1 for normalized vectors)
            scores = distances[0].tolist()
        else:
            # Convert L2 distance to similarity
            # Similarity = 1 / (1 + distance)
            scores = [1.0 / (1.0 + d) for d in distances[0]]
        
        return entity_ids, scores
    
    def batch_search(
        self,
        query_embeddings: np.ndarray,
        top_k: int = 10
    ) -> Tuple[List[List[str]], List[List[float]]]:
        """
        Batch search for multiple queries.
        
        Args:
            query_embeddings: Array of shape (n_queries, embedding_dim)
            top_k: Number of results per query
        
        Returns:
            Tuple of (list of entity_id lists, list of score lists)
        """
        if len(self.entity_ids) == 0:
            return [[] for _ in range(len(query_embeddings))], [[] for _ in range(len(query_embeddings))]
        
        # Normalize if using cosine
        queries = query_embeddings.copy()
        if self.metric == "cosine":
            norms = np.linalg.norm(queries, axis=1, keepdims=True)
            queries = queries / np.maximum(norms, 1e-10)
        
        # Search
        top_k = min(top_k, len(self.entity_ids))
        distances, indices = self.index.search(queries.astype(np.float32), top_k)
        
        # Convert results
        all_entity_ids = []
        all_scores = []
        
        for i in range(len(queries)):
            entity_ids = [self.entity_ids[idx] for idx in indices[i]]
            
            if self.metric == "cosine":
                scores = distances[i].tolist()
            else:
                scores = [1.0 / (1.0 + d) for d in distances[i]]
            
            all_entity_ids.append(entity_ids)
            all_scores.append(scores)
        
        return all_entity_ids, all_scores
