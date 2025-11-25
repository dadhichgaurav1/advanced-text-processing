"""Mode B: Parallel signal aggregation."""

from typing import List, Optional, Dict
import numpy as np

from ner_lib.models.entity import Mention, Entity
from ner_lib.models.candidate import MatchResult, Candidate, SameCandidate, NextSteps, Citation
from ner_lib.config import Config
from ner_lib.storage import StorageBackend
from ner_lib.signals import (
    ExactMatcher, combined_fuzzy_score, acronym_score,
    EmbeddingModel, semantic_similarity_score,
    domain_consistency_boost, recency_boost
)
from ner_lib.candidate_generation import (
    HashMapLookup, CombinedBlocker,
    FaissIndex, HNSWIndex,
    FAISS_AVAILABLE, HNSWLIB_AVAILABLE
)
from ner_lib.scoring import WeightedAggregator


class ModeBResolver:
    """Parallel signal aggregation resolver."""
    
    def __init__(
        self,
        config: Config,
        storage: StorageBackend,
        embedding_model: Optional[EmbeddingModel] = None
    ):
        """
        Initialize Mode B resolver.
        
        Args:
            config: Configuration
            storage: Storage backend
            embedding_model: Optional pre-initialized embedding model
        """
        self.config = config
        self.storage = storage
        self.embedding_model = embedding_model
        
        # Initialize components
        self.exact_matcher = ExactMatcher()
        self.blocker = CombinedBlocker()
        self.ann_index = None
        self.aggregator = WeightedAggregator(config.mode_b_weights)
        
        # Build indices
        self._build_indices()
    
    def _build_indices(self):
        """Build search indices from storage."""
        entities = self.storage.get_all_entities()
        
        for entity in entities:
            # Exact matcher
            self.exact_matcher.add_entity(
                entity.id,
                entity.canonical_name,
                entity.aliases
            )
            
            # Blocker
            self.blocker.add_entity(
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
        Resolve mention using Mode B parallel signal aggregation.
        
        Steps:
        1. Normalize (done in Mention.__post_init__)
        2. Generate candidates (union of exact, blocking, ANN)
        3. Compute all signals for each candidate in parallel
        4. Aggregate scores
        5. Apply decision thresholds
        
        Args:
            mention: Mention to resolve
        
        Returns:
            Match result
        """
        all_citations: List[Citation] = []
        
        # Step 2: Generate candidates
        candidate_ids = self._generate_candidates(mention)
        
        if not candidate_ids:
            return MatchResult(
                mention=mention,
                matched_entity=None,
                confidence=0.0,
                citations=all_citations,
                next_steps=NextSteps.NEW_ENTITY
            )
        
        # Step 3: Compute signals for all candidates
        candidates = self._compute_signals(mention, candidate_ids)
        
        if not candidates:
            return MatchResult(
                mention=mention,
                matched_entity=None,
                confidence=0.0,
                citations=all_citations,
                next_steps=NextSteps.NEW_ENTITY
            )
        
        # Step 4: Aggregate scores
        for candidate in candidates:
            candidate.final_score = self.aggregator.aggregate(candidate)
        
        # Sort by score
        candidates.sort(key=lambda c: c.final_score, reverse=True)
        best_candidate = candidates[0]
        
        # Get entity
        best_entity = self.storage.get_entity(best_candidate.entity_id)
        
        # Collect all citations
        all_citations.extend(best_candidate.citations)
        
        # Step 5: Apply thresholds
        if best_candidate.final_score >= self.config.thresholds.mode_b_auto_merge:
            # Very high confidence: auto-merge
            next_steps = NextSteps.NONE
        elif best_candidate.final_score >= self.config.thresholds.mode_b_auto_link:
            # High confidence: auto-link but audit
            next_steps = NextSteps.NONE
        elif best_candidate.final_score >= self.config.thresholds.mode_b_review:
            # Medium confidence: human review
            next_steps = NextSteps.HUMAN_REVIEW
        else:
            # Low confidence: new entity
            return MatchResult(
                mention=mention,
                matched_entity=None,
                confidence=best_candidate.final_score,
                citations=all_citations,
                next_steps=NextSteps.NEW_ENTITY,
                candidates=candidates
            )
        
        return MatchResult(
            mention=mention,
            matched_entity=best_entity,
            confidence=best_candidate.final_score,
            citations=all_citations,
            next_steps=next_steps,
            candidates=candidates
        )
    
    def _generate_candidates(self, mention: Mention) -> List[str]:
        """
        Generate candidate entity IDs from multiple sources.
        
        Args:
            mention: Mention to match
        
        Returns:
            Deduplicated list of candidate entity IDs
        """
        candidate_ids = set()
        
        # Exact lookup
        exact_result = self.exact_matcher.match(mention.text)
        if exact_result:
            entity_id, _ = exact_result
            candidate_ids.add(entity_id)
        
        # Blocking
        blocked_ids = self.blocker.get_candidates(mention.text)
        candidate_ids.update(blocked_ids)
        
        # ANN search
        if self.ann_index and self.embedding_model:
            mention_embedding = self.embedding_model.encode(mention.text)
            ann_ids, _ = self.ann_index.search(
                mention_embedding,
                top_k=self.config.ann.top_k
            )
            candidate_ids.update(ann_ids)
        
        return list(candidate_ids)
    
    def _compute_signals(self, mention: Mention, candidate_ids: List[str]) -> List[Candidate]:
        """
        Compute all signals for candidates.
        
        Args:
            mention: Mention to match
            candidate_ids: List of candidate entity IDs
        
        Returns:
            List of candidates with computed signals
        """
        candidates = []
        
        for entity_id in candidate_ids:
            entity = self.storage.get_entity(entity_id)
            if not entity:
                continue
            
            candidate = Candidate(entity_id=entity_id, entity=entity)
            
            # Compute all signals
            self._compute_exact_signal(mention, entity, candidate)
            self._compute_fuzzy_signals(mention, entity, candidate)
            self._compute_acronym_signal(mention, entity, candidate)
            
            if self.embedding_model:
                self._compute_semantic_signal(mention, entity, candidate)
            
            self._compute_contextual_signals(mention, entity, candidate)
            
            candidates.append(candidate)
        
        return candidates
    
    def _compute_exact_signal(self, mention: Mention, entity: Entity, candidate: Candidate):
        """Compute exact match signal."""
        exact_result = self.exact_matcher.match(mention.text)
        if exact_result and exact_result[0] == entity.id:
            citation = exact_result[1]
            candidate.add_signal('exact_match', 1.0, citation)
        else:
            candidate.add_signal('exact_match', 0.0)
    
    def _compute_fuzzy_signals(self, mention: Mention, entity: Entity, candidate: Candidate):
        """Compute fuzzy string similarity signals."""
        score, citations = combined_fuzzy_score(
            mention.normalized_text,
            entity.normalized_name
        )
        
        # Use token_set_ratio as the main fuzzy signal
        for citation in citations:
            if citation.method == "token_set_ratio":
                candidate.add_signal('token_set_ratio', citation.confidence_contribution / self.config.mode_b_weights.token_set_ratio, citation)
                break
        
        if 'token_set_ratio' not in candidate.signals:
            candidate.add_signal('token_set_ratio', score)
    
    def _compute_acronym_signal(self, mention: Mention, entity: Entity, candidate: Candidate):
        """Compute acronym signal."""
        score, citation = acronym_score(mention.text, entity.canonical_name)
        candidate.add_signal('acronym', score, citation)
    
    def _compute_semantic_signal(self, mention: Mention, entity: Entity, candidate: Candidate):
        """Compute semantic similarity signal."""
        if self.embedding_model:
            score, citation = semantic_similarity_score(
                mention.text,
                entity.canonical_name,
                self.embedding_model
            )
            candidate.add_signal('embedding_cosine', score, citation)
    
    def _compute_contextual_signals(self, mention: Mention, entity: Entity, candidate: Candidate):
        """Compute contextual signals."""
        total_contextual = 0.0
        citations = []
        
        # Domain consistency
        boost, citation = domain_consistency_boost(
            mention.metadata,
            entity.metadata
        )
        if boost > 0:
            total_contextual += boost
            if citation:
                citations.append(citation)
        
        # Recency
        recency = recency_boost(entity)
        total_contextual += recency
        
        if total_contextual > 0:
            candidate.add_signal('contextual', total_contextual, citations[0] if citations else None)
        else:
            candidate.add_signal('contextual', 0.0)
