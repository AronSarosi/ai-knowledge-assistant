"""Tests for the small data shapes in rag.schemas (pure logic, no API)."""

from __future__ import annotations

from rag.schemas import Answer, Chunk


def test_location_with_page():
    chunk = Chunk(text="hello", source="handbook.pdf", page=4)
    assert chunk.location() == "handbook.pdf, p.4"


def test_location_without_page():
    chunk = Chunk(text="hello", source="policy.docx")
    assert chunk.location() == "policy.docx"


def test_location_page_zero_is_shown():
    # page is `int | None`; 0 is a real value, not "missing", so it must show.
    chunk = Chunk(text="hello", source="weird.pdf", page=0)
    assert chunk.location() == "weird.pdf, p.0"


def test_answer_defaults_grounded_true_with_no_citations():
    answer = Answer(question="q?", text="some answer")
    assert answer.grounded is True
    assert answer.citations == []
