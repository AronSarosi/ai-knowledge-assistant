"""Tests for rag.store.VectorStore.search threshold filtering (Chroma mocked).

The embedding client and the Chroma collection are both replaced with fakes, so
no embeddings are computed and no network call is made. We only test the
relevance-threshold filtering logic, which is what lets the assistant return no
chunks (and so honestly say "not found") for an off-topic query.
"""

from __future__ import annotations

import rag.store as store_mod
from rag.schemas import Chunk
from rag.store import VectorStore


class _FakeChromaDoc:
    """Mimics a LangChain Document: page_content + metadata."""

    def __init__(self, text: str, source: str, page=None):
        self.page_content = text
        self.metadata = {"source": source, "page": page}


class _FakeChroma:
    """Stand-in for a Chroma collection returning preset scored results."""

    def __init__(self, scored):
        self._scored = scored
        self.last_k = None

    def similarity_search_with_relevance_scores(self, query, k):
        self.last_k = k
        return self._scored


def _make_store(monkeypatch, scored, settings):
    fake_db = _FakeChroma(scored)
    # Neither of these should ever touch the network.
    monkeypatch.setattr(store_mod, "_embeddings", lambda s: object())
    monkeypatch.setattr(store_mod, "Chroma", lambda **kwargs: fake_db)
    return VectorStore(settings), fake_db


def test_search_keeps_only_chunks_above_threshold(monkeypatch, settings):
    settings.relevance_threshold = 0.25
    scored = [
        (_FakeChromaDoc("relevant A", "a.txt"), 0.90),
        (_FakeChromaDoc("borderline below", "b.txt"), 0.10),
        (_FakeChromaDoc("relevant B", "c.pdf", page=3), 0.30),
    ]
    vs, _ = _make_store(monkeypatch, scored, settings)

    results = vs.search("a question")

    assert all(isinstance(c, Chunk) for c in results)
    texts = [c.text for c in results]
    assert texts == ["relevant A", "relevant B"]  # 0.10 was dropped
    # Provenance carries through from metadata.
    assert results[1].source == "c.pdf"
    assert results[1].page == 3


def test_search_at_exact_threshold_is_kept(monkeypatch, settings):
    settings.relevance_threshold = 0.25
    scored = [(_FakeChromaDoc("exactly on the bar", "x.txt"), 0.25)]
    vs, _ = _make_store(monkeypatch, scored, settings)

    results = vs.search("q")
    assert [c.text for c in results] == ["exactly on the bar"]


def test_search_returns_empty_when_nothing_clears_threshold(monkeypatch, settings):
    settings.relevance_threshold = 0.5
    scored = [
        (_FakeChromaDoc("loosely related", "a.txt"), 0.2),
        (_FakeChromaDoc("also weak", "b.txt"), 0.1),
    ]
    vs, _ = _make_store(monkeypatch, scored, settings)

    assert vs.search("off-topic query") == []


def test_search_uses_top_k_by_default(monkeypatch, settings):
    settings.top_k = 7
    vs, fake_db = _make_store(monkeypatch, [], settings)
    vs.search("q")
    assert fake_db.last_k == 7


def test_search_explicit_k_overrides_top_k(monkeypatch, settings):
    settings.top_k = 7
    vs, fake_db = _make_store(monkeypatch, [], settings)
    vs.search("q", k=2)
    assert fake_db.last_k == 2


def test_search_missing_metadata_falls_back_to_unknown(monkeypatch, settings):
    settings.relevance_threshold = 0.0

    class _BareDoc:
        page_content = "no metadata here"
        metadata: dict = {}

    vs, _ = _make_store(monkeypatch, [(_BareDoc(), 0.9)], settings)
    results = vs.search("q")
    assert results[0].source == "unknown"
    assert results[0].page is None
