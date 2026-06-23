"""Tests for rag.ingest.load_file chunking (no API calls).

These exercise the parse + chunk logic on plain text/markdown, the
unsupported-extension guard, and the empty-input case. PDF/DOCX parsing is left
to their libraries; we cover the chunking and provenance logic that is ours.
"""

from __future__ import annotations

import pytest

from rag.ingest import load_file
from rag.schemas import Chunk


def test_load_file_chunks_text(settings):
    chunks = load_file("notes.txt", b"Hello world. This is a test document.", settings)
    assert len(chunks) >= 1
    assert all(isinstance(c, Chunk) for c in chunks)
    assert all(c.source == "notes.txt" for c in chunks)
    # Non-PDF inputs carry no page number.
    assert all(c.page is None for c in chunks)


def test_load_file_markdown_supported(settings):
    chunks = load_file("readme.md", b"# Title\n\nSome body text here.", settings)
    assert len(chunks) >= 1
    assert chunks[0].source == "readme.md"


def test_load_file_splits_long_text_into_multiple_chunks(settings):
    settings.chunk_size = 100
    settings.chunk_overlap = 10
    long_text = ("This is sentence number {}. ".format(i) for i in range(200))
    data = "".join(long_text).encode("utf-8")
    chunks = load_file("big.txt", data, settings)
    assert len(chunks) > 1


def test_load_file_unsupported_extension_raises(settings):
    with pytest.raises(ValueError, match="Unsupported file type"):
        load_file("image.png", b"\x89PNG\r\n", settings)


def test_load_file_empty_text_yields_no_chunks(settings):
    chunks = load_file("empty.txt", b"", settings)
    assert chunks == []


def test_load_file_whitespace_only_yields_no_chunks(settings):
    # The splitter drops content that has no real text, so zero chunks come out.
    chunks = load_file("blank.txt", b"   \n\n   \t  ", settings)
    assert chunks == []
