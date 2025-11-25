"""Mode A: Sequential pipeline with early stopping."""

from typing import List, Optional, Tuple
from ner_lib.models.entity import Mention, Entity
from ner_lib.models.candidate import MatchResult, Candidate, SameCandidate, NextSteps, Citation
from ner_lib.config import Config
from ner_lib.storage import StorageBackend
from ner_lib.signals import (
    ExactMatcher, quick_fuzzy_score, quick_acronym_check,
    EmbeddingModel, semantic_similarity_score
)
from ner_lib.candidate_generation import HashMapLookup, CombinedBlocker, FaissIndex, HNSWIndex, FAISS_AVAILABLE, HNSWLIB_AVAILABLE


class ModeAResolver:
    """Sequential resolver with early stopping."""
    
    def __init__(
        self,
        config: Config,
        storage: StorageBackend,
        embedding_model: Optional[EmbeddingModel] = None
    ):
        """
        Initialize Mode A resolver.
        
        Args:
            config: Configuration
            storage: Storage backend
            embedding_model: Optional pre-initialized embedding model
        """
        self.config = config
        self.storage = storage
        
        # Initialize components
        self.exact_matcher = ExactMatcher()
        self.embedding_model = embedding_model
        self.ann_index = None
        
        # Build indices from storage
        self._build_indices()
    
    def _build_indices(self):
        """Build search indices from storage."""
        entities = self.storage.get_all_entities()
        
        # Build exact matcher
        for entity in entities:
            self.exact_matcher.add_entity(
                entity.id,
                entity.canonical_name,
                entity.aliases
            )
    
    def build_ann_index(self, embedding_model: EmbeddingModel):
        """
        Build ANN index for semantic search.
        
        Args:
            embedding_model: Embedding model to use
        """
        self.embedding_model = embedding_model
        entities = self.storage.get_all_entities()
        
        if not entities:
            return
        
        # Generate embeddings
        canonical_names = [e.canonical_name for e in entities]
        entity_ids = [e.id for e in entities]
        
        embeddings = embedding_model.encode(canonical_names, show_progress=True)
        
        # Create ANN index
        if self.config.ann.index_type == "faiss" and FAISS_AVAILABLE:
            self.ann_index = FaissIndex(
                embedding_dim=embedding_model.embedding_dim,
                metric=self.config.ann.metric
            )
        elif self.config.ann.index_type == "hnswlib" and HNSWLIB_AVAILABLE:
            self.ann_index = HNSWIndex(
                embedding_dim=embedding_model.embedding_dim,
                metric=self.config.ann.metric,
                ef_construction=self.config.ann.hnsw_ef_construction,
                M=self.config.ann.hnsw_m
            )
        else:
            raise ValueError(f"ANN index type '{self.config.ann.index_type}' not available")
        
        self.ann_index.build_index(entity_ids, embeddings)
    
    def resolve(self, mention: Mention) -> MatchResult:
        """
        Resolve mention using Mode A sequential pipeline.
        
        Steps:
        1. Normalize (done in Mention.__post_init__)
        2. Exact alias lookup → STOP if found
        3. Acronym check → STOP if high confidence
        4. Fuzzy matching → STOP if high confidence
        5. ANN + semantic → aggregate signals
        6. Apply decision thresholds
        
        Args:
            mention: Mention to resolve
        
        Returns:
            Match result
        """
        citations: List[Citation] = []
        
        # Step 2: Exact alias lookup
        exact_result = self.exact_matcher.match(mention.text)
        if exact_result:
            entity_id, citation = exact_result
            entity = self.storage.get_entity(entity_id)
            
            if entity:
                citations.append(citation)
                return MatchResult(
                    mention=mention,
                    matched_entity=entity,
                    confidence=1.0,
                    citations=citations,
                    next_steps=NextSteps.NONE
                )
        
        # Get all entities for further checks
        entities = self.storage.get_all_entities()
        
        if not entities:
            # No entities to match against
            return MatchResult(
                mention=mention,
                matched_entity=None,
                confidence=0.0,
                citations=citations,
                next_steps=NextSteps.NEW_ENTITY
            )
        
        # Step 3: Acronym check
        for entity in entities:
            if quick_acronym_check(
                mention.text,
                entity.canonical_name,
                threshold=self.config.thresholds.high_acronym
            ):
                citation = Citation(
                    source="Custom",
                    method="acronym_match",
                    component="acronym",
                    confidence_contribution=1.0
                )
                citations.append(citation)
                
                return MatchResult(
                    mention=mention,
                    matched_entity=entity,
                    confidence=self.config.thresholds.high_acronym,
                    citations=citations,
                    next_steps=NextSteps.NONE
                )
        
        # Step 4: Fuzzy matching
        best_fuzzy_entity = None
        best_fuzzy_score = 0.0
        
        for entity in entities:
            score = quick_fuzzy_score(mention.normalized_text, entity.normalized_name)
            if score > best_fuzzy_score:
                best_fuzzy_score = score
                best_fuzzy_entity = entity
        
        if best_fuzzy_score >= self.config.thresholds.high_fuzzy:
            citation = Citation(
                source="RapidFuzz",
                method="token_set_ratio",
                component="fuzzy_matching",
                confidence_contribution=best_fuzzy_score
            )
            citations.append(citation)
            
            return MatchResult(
                mention=mention,
                matched_entity=best_fuzzy_entity,
                confidence=best_fuzzy_score,
                citations=citations,
                next_steps=NextSteps.NONE
            )
        
        # Step 5: ANN + semantic
        if self.ann_index and self.embedding_model:
            # Generate embedding for mention
            mention_embedding = self.embedding_model.encode(mention.text)
            
            # Search ANN
            candidate_ids, ann_scores = self.ann_index.search(
                mention_embedding,
                top_k=min(10, len(entities))
            )
            
            # Get best candidate
            if candidate_ids:
                best_entity_id = candidate_ids[0]
                best_entity = self.storage.get_entity(best_entity_id)
                
                # Compute semantic similarity
                if best_entity:
                    sem_score, sem_citation = semantic_similarity_score(
                        mention.text,
                        best_entity.canonical_name,
                        self.embedding_model
                    )
                    citations.append(sem_citation)
                    
                    # Step 6: Apply thresholds
                    if sem_score >= self.config.thresholds.auto_merge:
                        # Auto-merge
                        return MatchResult(
                            mention=mention,
                            matched_entity=best_entity,
                            confidence=sem_score,
                            citations=citations,
                            next_steps=NextSteps.NONE
                        )
                    elif sem_score >= self.config.thresholds.review_low:
                        # Send to review queue
                        return MatchResult(
                            mention=mention,
                            matched_entity=best_entity,
                            confidence=sem_score,
                            citations=citations,
                            next_steps=NextSteps.HUMAN_REVIEW
                        )
        
        # No match found
        return MatchResult(
            mention=mention,
            matched_entity=None,
            confidence=0.0,
            citations=citations,
            next_steps=NextSteps.NEW_ENTITY
        )
