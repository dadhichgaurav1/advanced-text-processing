"""Alias retrieval module for NER library."""

from ner_lib.aliases.alias_retrieval import get_aliases, clear_caches
from ner_lib.aliases.wikidata_client import WikidataClient
from ner_lib.aliases.synonym_provider import SynonymProvider

__all__ = [
    "get_aliases",
    "clear_caches",
    "WikidataClient",
    "SynonymProvider"
]
