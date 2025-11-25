"""Score aggregation for Mode B."""

from typing import Dict, List
from ner_lib.models.candidate import Candidate, Citation
from ner_lib.config import ModeBWeights


class WeightedAggregator:
    """Weighted linear combination of signals."""
    
    def __init__(self, weights: ModeBWeights = None):
        """
        Initialize aggregator.
        
        Args:
            weights: Signal weights configuration
        """
        if weights is None:
            from ner_lib.config import DEFAULT_CONFIG
            weights = DEFAULT_CONFIG.mode_b_weights
        
        self.weights = weights
    
    def aggregate(self, candidate: Candidate) -> float:
        """
        Aggregate signals into final score.
        
        Args:
            candidate: Candidate with signals
        
        Returns:
            Final aggregated score
        """
        signals = candidate.signals
        score = 0.0
        
        # Exact match overrides everything
        if signals.get('exact_match', 0.0) == 1.0:
            return 1.0
        
        # Weighted combination
        score += signals.get('exact_match', 0.0) * self.weights.exact_match
        score += signals.get('embedding_cosine', 0.0) * self.weights.embedding_cosine
        score += signals.get('token_set_ratio', 0.0) * self.weights.token_set_ratio
        score += signals.get('acronym', 0.0) * self.weights.acronym
        
        # Add contextual boost (additive)
        contextual = signals.get('contextual', 0.0)
        score += contextual * self.weights.contextual_boost
        
        # Clip to [0, 1]
        score = max(0.0, min(1.0, score))
        
        return score
    
    def aggregate_with_details(self, candidate: Candidate) -> tuple[float, Dict[str, float]]:
        """
        Aggregate signals and return detailed breakdown.
        
        Args:
            candidate: Candidate with signals
        
        Returns:
            Tuple of (final_score, contribution_breakdown)
        """
        signals = candidate.signals
        contributions = {}
        
        # Check exact match override
        if signals.get('exact_match', 0.0) == 1.0:
            return 1.0, {'exact_match': 1.0}
        
        # Calculate contributions
        contributions['exact_match'] = signals.get('exact_match', 0.0) * self.weights.exact_match
        contributions['embedding_cosine'] = signals.get('embedding_cosine', 0.0) * self.weights.embedding_cosine
        contributions['token_set_ratio'] = signals.get('token_set_ratio', 0.0) * self.weights.token_set_ratio
        contributions['acronym'] = signals.get('acronym', 0.0) * self.weights.acronym
        contributions['contextual'] = signals.get('contextual', 0.0) * self.weights.contextual_boost
        
        # Sum total
        score = sum(contributions.values())
        score = max(0.0, min(1.0, score))
        
        return score, contributions
