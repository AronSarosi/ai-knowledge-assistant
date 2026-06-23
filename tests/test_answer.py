"""Tests for rag.answer.generate_answer (LLM mocked, no API calls).

We monkeypatch the chat model so it returns a canned reply, then assert on the
grounded-detection and citation-extraction logic that is the heart of the
anti-hallucination behaviour.
"""

from __future__ import annotations

import rag.answer as answer_mod
from rag.answer import NOT_FOUND, generate_answer
from rag.schemas import Chunk


class _FakeReply:
    def __init__(self, content: str):
        self.content = content


class _FakeLLM:
    """Stand-in for a LangChain chat model: returns a fixed reply, no network."""

    def __init__(self, reply: str):
        self._reply = reply
        self.calls: list = []

    def invoke(self, messages):
        self.calls.append(messages)
        return _FakeReply(self._reply)


def _patch_llm(monkeypatch, reply: str) -> _FakeLLM:
    fake = _FakeLLM(reply)
    monkeypatch.setattr(answer_mod, "_build_llm", lambda settings: fake)
    return fake


def _chunks() -> list[Chunk]:
    return [
        Chunk(text="Full-time staff get 28 days of paid leave.", source="handbook.pdf", page=2),
        Chunk(text="Staff may work from home up to three days a week.", source="policy.docx"),
    ]


def test_no_chunks_returns_not_found_without_calling_llm(settings, monkeypatch):
    # Guard clause: with nothing retrieved we must not even build the LLM.
    def _boom(_settings):
        raise AssertionError("LLM should not be built when there are no chunks")

    monkeypatch.setattr(answer_mod, "_build_llm", _boom)
    ans = generate_answer("anything?", [], settings)
    assert ans.text == NOT_FOUND
    assert ans.grounded is False
    assert ans.citations == []


def test_grounded_answer_extracts_only_referenced_citations(settings, monkeypatch):
    _patch_llm(monkeypatch, "Full-time staff get 28 days of paid leave [1].")
    ans = generate_answer("How much leave?", _chunks(), settings)
    assert ans.grounded is True
    # Only passage [1] was referenced, so only it is surfaced.
    assert [c.index for c in ans.citations] == [1]
    assert ans.citations[0].location == "handbook.pdf, p.2"


def test_grounded_answer_with_multiple_citations(settings, monkeypatch):
    _patch_llm(monkeypatch, "Leave is 28 days [1]. Remote work is allowed [2].")
    ans = generate_answer("Tell me everything", _chunks(), settings)
    assert ans.grounded is True
    assert [c.index for c in ans.citations] == [1, 2]


def test_not_found_reply_sets_grounded_false_and_no_citations(settings, monkeypatch):
    _patch_llm(monkeypatch, NOT_FOUND)
    ans = generate_answer("What is the CEO's home address?", _chunks(), settings)
    assert ans.grounded is False
    assert ans.citations == []
    assert ans.text == NOT_FOUND


def test_not_found_detection_is_case_insensitive(settings, monkeypatch):
    _patch_llm(monkeypatch, NOT_FOUND.upper())
    ans = generate_answer("unknown?", _chunks(), settings)
    assert ans.grounded is False


def test_citation_snippet_is_truncated_at_300_chars(settings, monkeypatch):
    long_chunk = [Chunk(text="x" * 500, source="big.txt")]
    _patch_llm(monkeypatch, "Here is the answer [1].")
    ans = generate_answer("q?", long_chunk, settings)
    snippet = ans.citations[0].snippet
    assert snippet.endswith("...")
    assert len(snippet) == 303  # 300 chars + "..."
