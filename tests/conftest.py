"""Shared test fixtures.

Every test in this suite is fully offline: nothing here makes a live API call.
The LLM and embedding clients are monkeypatched in the individual tests, so
these fixtures only provide cheap, deterministic settings.
"""

from __future__ import annotations

import pytest

from rag.config import Settings


@pytest.fixture
def settings() -> Settings:
    """Default settings with no real credentials (no live calls are made)."""
    return Settings(
        provider="openai",
        openai_api_key="test-key-not-real",
        chunk_size=1000,
        chunk_overlap=150,
        top_k=4,
        relevance_threshold=0.25,
    )
