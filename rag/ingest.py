"""Stage 1 of RAG: turn raw files into clean, chunked passages.

Two jobs:
  1. PARSE  - pull plain text out of PDF / DOCX / TXT / MD, keeping page numbers
              for PDFs so citations can point to an exact page.
  2. CHUNK  - split that text into ~1000-character overlapping passages.

Why chunk at all? Two reasons. First, embeddings capture meaning best over a
focused passage, not a whole 40-page document. Second, we only feed the model
the few passages that matter for a question, so it stays fast, cheap, and
grounded. The small overlap means a fact sitting on a chunk boundary still
lands whole inside at least one chunk.
"""

from __future__ import annotations

import io
from pathlib import Path

import docx2txt
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from .config import Settings
from .schemas import Chunk

SUPPORTED = {".pdf", ".docx", ".txt", ".md"}


# --- Parsing ----------------------------------------------------------------
def _read_pdf(data: bytes) -> list[tuple[str, int]]:
    """Return (text, page_number) for each non-empty page."""
    reader = PdfReader(io.BytesIO(data))
    pages: list[tuple[str, int]] = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append((text, i))
    return pages


def _read_docx(data: bytes) -> str:
    """DOCX has no real page concept, so we treat it as one continuous text."""
    return docx2txt.process(io.BytesIO(data)) or ""


def _read_text(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


# --- Public API -------------------------------------------------------------
def load_file(name: str, data: bytes, settings: Settings) -> list[Chunk]:
    """Parse one file's bytes into chunks tagged with their source + page.

    `name` is the original file name (used in citations). `data` is the raw
    bytes - works for both an uploaded file and one read off disk.
    """
    suffix = Path(name).suffix.lower()
    if suffix not in SUPPORTED:
        raise ValueError(f"Unsupported file type: {suffix}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        # Split on natural boundaries first (paragraphs, then lines, then
        # sentences) so chunks stay readable.
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: list[Chunk] = []
    if suffix == ".pdf":
        for text, page in _read_pdf(data):
            for piece in splitter.split_text(text):
                chunks.append(Chunk(text=piece, source=name, page=page))
    else:
        whole = _read_docx(data) if suffix == ".docx" else _read_text(data)
        for piece in splitter.split_text(whole):
            chunks.append(Chunk(text=piece, source=name))

    return chunks


def load_directory(directory: Path, settings: Settings) -> list[Chunk]:
    """Parse every supported file in a folder (used for the demo sample docs)."""
    chunks: list[Chunk] = []
    for path in sorted(directory.glob("*")):
        if path.suffix.lower() in SUPPORTED:
            chunks.extend(load_file(path.name, path.read_bytes(), settings))
    return chunks
