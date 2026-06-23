"""RAG knowledge-assistant package.

Public surface is deliberately tiny: build a KnowledgeBase, add documents, ask
questions. See pipeline.py for the guided tour.
"""

from .config import Settings, load_settings
from .pipeline import KnowledgeBase
from .schemas import Answer, Citation, Chunk

__all__ = [
    "KnowledgeBase",
    "Settings",
    "load_settings",
    "Answer",
    "Citation",
    "Chunk",
]
