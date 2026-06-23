"""The whole RAG system as one small, readable object.

If you only read one file to understand this tool, read this one. A
KnowledgeBase ties the three stages together:

    kb = KnowledgeBase(settings)
    kb.ingest(name, file_bytes)     # parse -> chunk -> embed -> store
    answer = kb.ask("How much leave do I get?")   # retrieve -> generate

That's RAG. Everything else is detail.
"""

from __future__ import annotations

from pathlib import Path

from .config import Settings, load_settings
from .ingest import load_directory, load_file
from .schemas import Answer
from .store import VectorStore


class KnowledgeBase:
    """An in-memory knowledge base you can add documents to and ask questions of."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or load_settings()
        self.store = VectorStore(self.settings)
        # Track what's been indexed so the UI can show the active sources.
        self.sources: list[str] = []
        self.chunk_count = 0

    def ingest(self, name: str, data: bytes) -> int:
        """Add one document. Returns the number of chunks indexed from it."""
        chunks = load_file(name, data, self.settings)
        added = self.store.add(chunks)
        if added and name not in self.sources:
            self.sources.append(name)
        self.chunk_count += added
        return added

    def ingest_directory(self, directory: Path) -> int:
        """Add every supported file in a folder (used for the demo sample set)."""
        chunks = load_directory(directory, self.settings)
        added = self.store.add(chunks)
        for c in chunks:
            if c.source not in self.sources:
                self.sources.append(c.source)
        self.chunk_count += added
        return added

    def ask(self, question: str) -> Answer:
        """Retrieve the relevant passages and return a grounded, cited answer."""
        from .answer import generate_answer

        chunks = self.store.search(question)
        return generate_answer(question, chunks, self.settings)
