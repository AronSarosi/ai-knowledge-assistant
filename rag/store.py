"""Stage 2 of RAG: embed the chunks and retrieve the relevant ones.

An EMBEDDING is a list of ~1500 numbers that captures the *meaning* of a piece
of text. Two passages about "annual leave" land near each other in that number
space even if one says "holiday" and the other says "PTO". That's why this
beats keyword search: it matches on meaning, not exact words.

A VECTOR STORE is just a database built to answer one question fast: "which
stored vectors are nearest to this one?" We use Chroma in-memory here, which
keeps the whole thing to a single portable Python process - perfect for a demo
and for handing a client a container that runs anywhere.

(For a large client deployment you'd swap this one class for a persistent vector
DB - pgvector, Qdrant, Pinecone - and nothing else in the app would change.
That swap-one-piece design is the point.)
"""

from __future__ import annotations

from langchain_chroma import Chroma

from .config import Settings
from .schemas import Chunk


def _embeddings(settings: Settings):
    """Build the embedding client for the active provider."""
    if settings.provider == "azure":
        from langchain_openai import AzureOpenAIEmbeddings

        return AzureOpenAIEmbeddings(
            azure_endpoint=settings.azure_endpoint,
            azure_deployment=settings.azure_embedding_deployment,
            api_version=settings.azure_api_version,
            api_key=settings.azure_api_key,
        )

    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        api_key=settings.openai_api_key,
    )


class VectorStore:
    """A thin wrapper around an in-memory Chroma collection.

    Two methods are all the rest of the app needs: add() to index chunks, and
    search() to find the most relevant ones for a question.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        # No persist_directory => Chroma runs purely in memory. The index lives
        # for the life of the process (we cache it per user session in app.py).
        self._db = Chroma(
            collection_name="knowledge_base",
            embedding_function=_embeddings(settings),
        )

    def add(self, chunks: list[Chunk]) -> int:
        """Embed and store chunks. Returns how many were added."""
        if not chunks:
            return 0
        texts = [c.text for c in chunks]
        # Metadata rides alongside each vector so search results know their
        # source file and page for citations.
        metadatas = [{"source": c.source, "page": c.page} for c in chunks]
        self._db.add_texts(texts=texts, metadatas=metadatas)
        return len(chunks)

    def search(self, query: str, k: int | None = None) -> list[Chunk]:
        """Return up to k chunks whose meaning is genuinely close to the query.

        We ask Chroma for relevance scores (0-1, higher = more similar) and drop
        anything below the configured threshold. This is what lets the assistant
        honestly say "I can't find that" instead of stretching a loosely-related
        passage into an answer: if nothing clears the bar we return no chunks at
        all. `top_k` stays the cap on how many we keep.
        """
        k = k or self.settings.top_k
        threshold = self.settings.relevance_threshold
        # similarity_search_with_relevance_scores normalises distance to a 0-1
        # relevance score, so one threshold works regardless of the embedding
        # model's raw distance scale.
        scored = self._db.similarity_search_with_relevance_scores(query, k=k)
        return [
            Chunk(
                text=doc.page_content,
                source=doc.metadata.get("source", "unknown"),
                page=doc.metadata.get("page"),
            )
            for doc, score in scored
            if score >= threshold
        ]
