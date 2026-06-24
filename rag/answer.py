"""Stage 3 of RAG: write a grounded, cited answer from the retrieved chunks.

This is where trust is won or lost. The model is given ONLY the passages we
retrieved, numbered [1], [2], ... and told three things:

  1. Answer using only those passages.
  2. Mark each claim with the [n] it came from.
  3. If the passages don't contain the answer, say so - never guess.

That last rule is the whole anti-hallucination story: the model is allowed to
say "I couldn't find this in your documents", which is exactly what a trustworthy
internal assistant should do.
"""

from __future__ import annotations

from typing import Any, List

from langchain_core.messages import HumanMessage, SystemMessage

from .config import Settings
from .schemas import Answer, Citation, Chunk

# Phrase the model uses verbatim when nothing relevant was retrieved. We detect
# it to set the `grounded=False` flag for the UI.
NOT_FOUND = "I couldn't find an answer to that in your documents."

SYSTEM_PROMPT = f"""You are a careful internal knowledge assistant. You answer \
staff questions using ONLY the numbered source passages provided.

Rules:
- Use only the information in the passages. Do not use outside knowledge.
- After each fact, cite the passage it came from with its number in square \
brackets, e.g. [1] or [2][3].
- Be concise and direct. British English.
- If the passages do not contain the answer, reply with exactly: \
"{NOT_FOUND}" and nothing else.
- Never invent figures, names, dates, or policies."""


def _build_llm(settings: Settings):
    if settings.provider == "azure":
        from langchain_openai import AzureChatOpenAI

        return AzureChatOpenAI(
            azure_endpoint=settings.azure_endpoint,
            azure_deployment=settings.azure_deployment,
            api_version=settings.azure_api_version,
            api_key=settings.azure_api_key,
            temperature=settings.temperature,
        )

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=settings.temperature,
    )


def get_callbacks(settings: Settings) -> List[Any]:
    """Return LangChain callbacks. Includes Langfuse only if its keys are set.

    Tracing is best-effort: if Langfuse isn't installed or fails to start, we
    return no callbacks rather than break the answer. With no keys (the default)
    this is a plain no-op.
    """
    if not settings.langfuse_enabled:
        return []
    try:
        from langfuse import Langfuse
        from langfuse.langchain import CallbackHandler

        # In langfuse v3 the CallbackHandler takes no keys; it uses the Langfuse
        # client, which reads LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY /
        # LANGFUSE_HOST from the environment. Initialise the client explicitly
        # with our settings first, then hand back a keyless handler.
        Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )
        return [CallbackHandler()]
    except Exception:
        # Tracing is best-effort. Never let it break a run.
        return []


def _format_passages(chunks: list[Chunk]) -> str:
    """Render retrieved chunks as a numbered list for the prompt."""
    blocks = []
    for i, c in enumerate(chunks, start=1):
        blocks.append(f"[{i}] (Source: {c.location()})\n{c.text}")
    return "\n\n".join(blocks)


def generate_answer(
    question: str, chunks: list[Chunk], settings: Settings
) -> Answer:
    """Produce a grounded, cited answer from the retrieved chunks."""
    if not chunks:
        return Answer(question=question, text=NOT_FOUND, grounded=False)

    llm = _build_llm(settings)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Source passages:\n\n{_format_passages(chunks)}\n\n"
                f"Question: {question}"
            )
        ),
    ]
    # Attach tracing callbacks only when there are any, so the default (no-key)
    # path keeps the plain invoke(messages) signature untouched.
    callbacks = get_callbacks(settings)
    if callbacks:
        result = llm.invoke(messages, config={"callbacks": callbacks})
    else:
        result = llm.invoke(messages)
    reply = result.content.strip()

    grounded = NOT_FOUND.lower() not in reply.lower()
    citations: list[Citation] = []
    if grounded:
        # Only surface the passages the answer actually referenced, so the
        # citation list matches the [n] markers the reader sees.
        for i, c in enumerate(chunks, start=1):
            if f"[{i}]" in reply:
                citations.append(
                    Citation(
                        index=i,
                        location=c.location(),
                        snippet=c.text[:300] + ("..." if len(c.text) > 300 else ""),
                    )
                )

    return Answer(
        question=question, text=reply, citations=citations, grounded=grounded
    )
