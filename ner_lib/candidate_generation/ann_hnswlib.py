"""HNSW-based ANN search using hnswlib."""

from typing import List, Tuple
import numpy as np

try:
    import hnswlib
    HNSWLIB_AVAILABLE = True
except ImportError:
    HNSWLIB_AVAILABLE = False


class HNSWIndex:
    """HNSW-based ANN index for entity embeddings."""
    
    def __init__(
        self,
        embedding_dim: int,
        metric: str = "cosine",
        ef_construction: int = 200,
        M: int = 16
    ):
        """
        Initialize HNSW index.
        
        Args:
            embedding_dim: Dimension of embeddings
            metric: Distance metric ('cosine' or 'l2')
            ef_construction: Construction parameter (higher = better quality, slower build)
            M: Number of connections per layer (higher = better recall, more memory)
        """
        if not HNSWLIB_AVAILABLE:
            raise ImportError("hnswlib not installed. Install with: pip install hnswlib")
        
        self.embedding_dim = embedding_dim
        self.metric = metric
        self.ef_construction = ef_construction
        self.M = M
        
        # Create index
        space = "cosine" if metric == "cosine" else "l2"
        self.index = hnswlib.Index(space=space, dim=embedding_dim)
        
        self.entity_ids: List[str] = []
        self.initialized = False
    
    def build_index(self, entity_ids: List[str], embeddings: np.ndarray, ef_search: int = 50):
        """
        Build index from entity embeddings.
        
        Args:
            entity_ids: List of entity IDs
            embeddings: Array of shape (n_entities, embedding_dim)
            ef_search: Search parameter (higher = better recall, slower search)
        """
        if embeddings.shape[0] != len(entity_ids):
            raise ValueError("Number of embeddings must match number of entity IDs")
        
        if embeddings.shape[1] != self.embedding_dim:
            raise ValueError(f"Embedding dimension mismatch: {embeddings.shape[1]} != {self.embedding_dim}")
        
        n_entities = len(entity_ids)
        
        # Initialize index
        self.index.init_index(
            max_elements=n_entities,
            ef_construction=self.ef_construction,
            M=self.M
        )
        
        # Set ef for search
        self.index.set_ef(ef_search)
        
        # Add items
        # hnswlib expects labels as integers, so we use indices
        labels = np.arange(n_entities)
        self.index.add_items(embeddings.astype(np.float32), labels)
        
        self.entity_ids = entity_ids
        self.initialized = True
    
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
        if not self.initialized or len(self.entity_ids) == 0:
            return [], []
        
        # Search
        top_k = min(top_k, len(self.entity_ids))
        labels, distances = self.index.knn_query(
            query_embedding.reshape(1, -1).astype(np.float32),
            k=top_k
        )
        
        # Convert labels to entity IDs
        entity_ids = [self.entity_ids[idx] for idx in labels[0]]
        
        # Convert distances to similarity scores
        if self.metric == "cosine":
            # Cosine distance: convert to similarity (1 - distance)
            scores = [1.0 - d for d in distances[0]]
        else:
            # L2 distance: convert to similarity
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
        if not self.initialized or len(self.entity_ids) == 0:
            return [[] for _ in range(len(query_embeddings))], [[] for _ in range(len(query_embeddings))]
        
        # Search
        top_k = min(top_k, len(self.entity_ids))
        labels, distances = self.index.knn_query(
            query_embeddings.astype(np.float32),
            k=top_k
        )
        
        # Convert results
        all_entity_ids = []
        all_scores = []
        
        for i in range(len(query_embeddings)):
            entity_ids = [self.entity_ids[idx] for idx in labels[i]]
            
            if self.metric == "cosine":
                scores = [1.0 - d for d in distances[i]]
            else:
                scores = [1.0 / (1.0 + d) for d in distances[i]]
            
            all_entity_ids.append(entity_ids)
            all_scores.append(scores)
        
        return all_entity_ids, all_scores
    
    def set_ef(self, ef: int):
        """Set ef parameter for search quality."""
        if self.initialized:
            self.index.set_ef(ef)
