"""Configuration: load .env, expose typed settings.

Same shape as the Lead Research Agent's config so the two tools feel identical
under the hood. Everything that varies between environments (keys, model,
provider, demo caps) comes from environment variables, so the same container
image runs locally, on Cloud Run, or in a client's cloud with nothing changed
but the .env / secrets.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Project root = the folder that contains this package.
ROOT = Path(__file__).resolve().parent.parent
SAMPLE_DOCS_DIR = ROOT / "data" / "sample_docs"

# Load .env once, on import. Safe to call repeatedly.
load_dotenv(ROOT / ".env")


def _as_bool(value: str, default: bool = False) -> bool:
    if value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class Settings:
    """Runtime settings derived from the environment."""

    # --- Provider -----------------------------------------------------------
    provider: str = "openai"  # 'openai' or 'azure'

    openai_api_key: str = ""
    # Cheap, fast chat model for answering. gpt-4o-mini is plenty for grounded
    # Q&A where the facts come from the retrieved text, not the model.
    openai_model: str = "gpt-4o-mini"
    # The embedding model turns text into vectors. 3-small is cheap and strong.
    openai_embedding_model: str = "text-embedding-3-small"

    azure_api_key: str = ""
    azure_endpoint: str = ""
    azure_deployment: str = ""
    azure_embedding_deployment: str = ""
    azure_api_version: str = "2024-08-01-preview"

    # --- Retrieval tuning ---------------------------------------------------
    # How big each chunk is (characters) and how much neighbouring chunks
    # overlap so a sentence split across a boundary is never lost.
    chunk_size: int = 1000
    chunk_overlap: int = 150
    # How many chunks we retrieve and feed to the model per question.
    top_k: int = 4
    # Minimum relevance score (0-1, cosine-based) a retrieved chunk must clear
    # to be used. Anything below is treated as not really about the question, so
    # an off-topic query returns no chunks and the assistant says it can't find
    # the answer rather than stretching. 0.25 is a safe default: low enough to
    # keep genuine paraphrase matches, high enough to reject unrelated text.
    relevance_threshold: float = 0.25

    # Grounded answering runs cold for consistency - we want it to report the
    # documents faithfully, not get creative.
    temperature: float = 0.1

    # --- Demo guardrails ----------------------------------------------------
    # Caps so a PUBLIC demo URL can't run up the API bill. Turn DEMO_MODE off
    # for a private/client deployment to lift them.
    demo_mode: bool = True
    demo_question_limit: int = 15
    max_upload_mb: int = 10
    max_files: int = 5

    @property
    def embedding_model(self) -> str:
        """The embedding model/deployment name for the active provider."""
        if self.provider == "azure":
            return self.azure_embedding_deployment
        return self.openai_embedding_model

    def validate(self) -> list[str]:
        """Return human-readable problems, empty if good to go."""
        problems: list[str] = []
        if self.provider == "openai" and not self.openai_api_key:
            problems.append("OPENAI_API_KEY is not set (.env).")
        if self.provider == "azure" and not (
            self.azure_api_key and self.azure_endpoint and self.azure_deployment
        ):
            problems.append(
                "Azure provider selected but AZURE_OPENAI_* vars are incomplete (.env)."
            )
        return problems


def load_settings() -> Settings:
    """Build Settings from environment variables."""
    return Settings(
        provider=os.getenv("LLM_PROVIDER", "openai").strip().lower(),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        openai_embedding_model=os.getenv(
            "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
        ),
        azure_api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", ""),
        azure_embedding_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", ""),
        azure_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
        chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "150")),
        top_k=int(os.getenv("TOP_K", "4")),
        relevance_threshold=float(os.getenv("RELEVANCE_THRESHOLD", "0.25")),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
        demo_mode=_as_bool(os.getenv("DEMO_MODE", "true"), default=True),
        demo_question_limit=int(os.getenv("DEMO_QUESTION_LIMIT", "15")),
        max_upload_mb=int(os.getenv("MAX_UPLOAD_MB", "10")),
        max_files=int(os.getenv("MAX_FILES", "5")),
    )
