"""Candidate generation package."""

from ner_lib.candidate_generation.exact_lookup import HashMapLookup
from ner_lib.candidate_generation.blocking import (
    PrefixBlocker,
    TokenBlocker,
    CombinedBlocker,
)

# ANN imports with error handling
try:
    from ner_lib.candidate_generation.ann_faiss import FaissIndex
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    FaissIndex = None

try:
    from ner_lib.candidate_generation.ann_hnswlib import HNSWIndex
    HNSWLIB_AVAILABLE = True
except ImportError:
    HNSWLIB_AVAILABLE = False
    HNSWIndex = None

__all__ = [
    "HashMapLookup",
    "PrefixBlocker",
    "TokenBlocker",
    "CombinedBlocker",
    "FaissIndex",
    "HNSWIndex",
    "FAISS_AVAILABLE",
    "HNSWLIB_AVAILABLE",
]
