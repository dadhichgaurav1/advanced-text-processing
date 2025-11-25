"""Main EntityResolver API."""

from typing import List, Optional, Union
from ner_lib.config import Config, DEFAULT_CONFIG
from ner_lib.storage import StorageBackend, MemoryStorage
from ner_lib.models.entity import Entity, Alias, Mention
from ner_lib.models.candidate import MatchResult, SameCandidate
from ner_lib.signals import EmbeddingModel
from ner_lib.modes import ModeAResolver, ModeBResolver


class EntityResolver:
    """Unified entity resolution API supporting Mode A and Mode B."""
    
    def __init__(
        self,
        mode: str = "A",
        config: Optional[Config] = None,
        storage: Optional[StorageBackend] = None,
        auto_build_indices: bool = True
    ):
        """
        Initialize EntityResolver.
        
        Args:
            mode: Operational mode ('A' or 'B')
            config: Configuration (uses default if None)
            storage: Storage backend (uses MemoryStorage if None)
            auto_build_indices: Whether to automatically build indices
        
        Example:
            ```python
            # Mode A: Sequential with early stopping
            resolver_a = EntityResolver(mode='A')
            
            # Mode B: Parallel signal aggregation
            resolver_b = EntityResolver(mode='B')
            ```
        """
        if mode not in ['A', 'B']:
            raise ValueError(f"Invalid mode: {mode}. Must be 'A' or 'B'")
        
        self.mode = mode
        self.config = config or DEFAULT_CONFIG
        self.storage = storage or MemoryStorage()
        
        # Initialize embedding model lazily
        self._embedding_model: Optional[EmbeddingModel] = None
        
        # Initialize resolver
        self._resolver = None
        if auto_build_indices:
            self._initialize_resolver()
    
    def _initialize_resolver(self):
        """Initialize the appropriate resolver."""
        if self.mode == "A":
            self._resolver = ModeAResolver(
                config=self.config,
                storage=self.storage,
                embedding_model=self._embedding_model
            )
        else:  # Mode B
            self._resolver = ModeBResolver(
                config=self.config,
                storage=self.storage,
                embedding_model=self._embedding_model
            )
    
    @property
    def embedding_model(self) -> EmbeddingModel:
        """Get or create embedding model (lazy loading)."""
        from ner_lib.signals import SEMANTIC_AVAILABLE
        
        if not SEMANTIC_AVAILABLE:
            raise ImportError(
                "Semantic matching is not available. "
                "Please install compatible versions of torch, transformers, and sentence-transformers. "
                "You can still use the library for exact matching, fuzzy matching, and acronym detection."
            )
        
        if self._embedding_model is None:
            from ner_lib.signals import EmbeddingModel as EM
            self._embedding_model = EM(
                model_name=self.config.models.sentence_transformer_model,
                device=self.config.models.device
            )
        return self._embedding_model
    
    def add_entity(
        self,
        canonical_name: str,
        aliases: Optional[List[str]] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Add a known entity to the knowledge base.
        
        Args:
            canonical_name: Canonical name of the entity
            aliases: Optional list of aliases
            metadata: Optional metadata dict
        
        Returns:
            Entity ID
        
        Example:
            ```python
            resolver.add_entity(
                "Apple Inc.",
                aliases=["Apple", "AAPL"],
                metadata={"domain": "apple.com"}
            )
            ```
        """
        entity = Entity(
            canonical_name=canonical_name,
            aliases=aliases or [],
            metadata=metadata or {}
        )
        
        entity_id = self.storage.create_entity(entity)
        
        # Rebuild indices
        if self._resolver:
            self._initialize_resolver()
        
        return entity_id
    
    def build_semantic_index(self):
        """
        Build ANN index for semantic search.
        
        This enables semantic similarity matching. Should be called after
        adding entities and before resolving mentions.
        
        Raises:
            ImportError: If semantic dependencies are not available
        
        Example:
            ```python
            resolver.add_entity("Apple Inc.", ["Apple"])
            resolver.add_entity("Microsoft Corporation", ["Microsoft"])
            resolver.build_semantic_index()  # Build embeddings index
            ```
        """
        from ner_lib.signals import SEMANTIC_AVAILABLE
        
        if not SEMANTIC_AVAILABLE:
            raise ImportError(
                "Cannot build semantic index: semantic matching dependencies are not available.\n"
                "Please install compatible versions of:\n"
                "  - torch\n"
                "  - transformers\n"
                "  - sentence-transformers\n\n"
                "The library will still work for exact matching, fuzzy matching, and acronym detection.\n"
                "You can skip calling build_semantic_index() to avoid this error."
            )
        
        if not self._resolver:
            self._initialize_resolver()
        
        # Build ANN index
        if hasattr(self._resolver, 'build_ann_index'):
            self._resolver.build_ann_index(self.embedding_model)
    
    def resolve(self, mention: Union[str, Mention]) -> MatchResult:
        """
        Resolve a single entity mention.
        
        Args:
            mention: Mention text or Mention object
        
        Returns:
            Match result with matched entity, confidence, and citations
        
        Example:
            ```python
            result = resolver.resolve("apple inc")
            
            if result.matched_entity:
                print(f"Matched: {result.matched_entity.canonical_name}")
                print(f"Confidence: {result.confidence}")
                print(f"Citations: {[c.source for c in result.citations]}")
            
            if result.next_steps == NextSteps.HUMAN_REVIEW:
                print("Needs human review")
            ```
        """
        # Convert string to Mention object
        if isinstance(mention, str):
            mention = Mention(text=mention)
        
        # Initialize resolver if needed
        if not self._resolver:
            self._initialize_resolver()
        
        # Resolve
        return self._resolver.resolve(mention)
    
    def resolve_batch(self, mentions: List[Union[str, Mention]]) -> List[MatchResult]:
        """
        Resolve multiple mentions.
        
        Args:
            mentions: List of mention texts or Mention objects
        
        Returns:
            List of match results
        
        Example:
            ```python
            results = resolver.resolve_batch([
                "apple inc",
                "microsoft corp",
                "IBM"
            ])
            
            for result in results:
                if result.matched_entity:
                    print(f"{result.mention.text} -> {result.matched_entity.canonical_name}")
            ```
        """
        return [self.resolve(mention) for mention in mentions]
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID."""
        return self.storage.get_entity(entity_id)
    
    def get_all_entities(self) -> List[Entity]:
        """Get all entities."""
        return self.storage.get_all_entities()
    
    def get_review_queue(self, status: str = "pending") -> List[SameCandidate]:
        """
        Get items in review queue.
        
        Args:
            status: Status filter ('pending', 'approved', 'rejected')
        
        Returns:
            List of review items
        """
        return self.storage.get_review_queue(status)
    
    def rebuild_indices(self):
        """
        Rebuild all indices.
        
        Call this after bulk entity additions or modifications.
        """
        self._initialize_resolver()
        
        # Rebuild semantic index if it was previously built
        if self._embedding_model is not None:
            self.build_semantic_index()
