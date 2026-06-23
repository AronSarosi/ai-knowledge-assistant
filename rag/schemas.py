"""The handful of data shapes that move through the RAG pipeline.

Kept deliberately small and readable - these three objects are the whole
vocabulary of the system:

  Chunk    - a small passage of a source document, plus where it came from.
  Citation - a source the answer was actually built from (shown to the user).
  Answer   - the model's grounded reply, plus its citations.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    """A small passage of text plus the provenance we show in citations."""

    text: str
    source: str  # file name the passage came from
    page: int | None = None  # page number for PDFs (None for docx/txt/md)

    def location(self) -> str:
        """Human-readable provenance, e.g. 'handbook.pdf, p.4'."""
        if self.page is not None:
            return f"{self.source}, p.{self.page}"
        return self.source


class Citation(BaseModel):
    """A source passage the answer was grounded in, surfaced for verification."""

    index: int  # the [n] marker used in the answer text
    location: str  # e.g. 'handbook.pdf, p.4'
    snippet: str  # the passage itself, so the reader can check the claim


class Answer(BaseModel):
    """A grounded answer to one question."""

    question: str
    text: str
    citations: list[Citation] = Field(default_factory=list)
    # True when the model found nothing relevant in the documents and said so,
    # rather than guessing. This is the anti-hallucination signal.
    grounded: bool = True
