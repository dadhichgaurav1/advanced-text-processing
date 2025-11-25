"""Storage package."""

from ner_lib.storage.interface import StorageBackend
from ner_lib.storage.memory import MemoryStorage

__all__ = ["StorageBackend", "MemoryStorage"]
