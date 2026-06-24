"""AI Knowledge Assistant - Streamlit UI.

A grounded, cited Q&A interface over your own documents. Upload handbooks,
policies, or manuals (or use the built-in sample) and ask questions in plain
English. Answers quote their sources; if the answer isn't in the documents, the
assistant says so rather than guessing.

Run locally:  streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from rag import KnowledgeBase, load_settings
from rag.config import SAMPLE_DOCS_DIR
from theme import (
    inject_theme,
    render_demo,
    render_footer,
    render_header,
    render_policy_page,
    render_step,
)

st.set_page_config(page_title="AI Knowledge Assistant", page_icon="📚", layout="wide")
inject_theme()

# Routing: ?page=terms and ?page=privacy render as their own themed pages (opened
# in a new tab from the footer), then stop before the main UI is drawn.
_page = st.query_params.get("page")
if _page in ("terms", "privacy"):
    render_policy_page(_page)
    st.stop()

render_header()
render_demo()

settings = load_settings()
problems = settings.validate()


# --- Knowledge base lifecycle ----------------------------------------------
def _signature(uploaded) -> tuple:
    """Identifies the active document set so we only re-index when it changes."""
    if uploaded:
        return tuple(sorted((f.name, f.size) for f in uploaded))
    return ("__sample__",)


def build_kb(uploaded) -> tuple[KnowledgeBase, list[str]]:
    """Build a fresh knowledge base from uploads, or the sample if none.

    Returns the knowledge base plus a list of human-readable warnings (files we
    skipped because they were corrupt, or that yielded no text). A single bad
    file never aborts the batch: we isolate each ingest so the good files still
    get indexed.
    """
    kb = KnowledgeBase(settings)
    warnings: list[str] = []
    if uploaded:
        for f in uploaded:
            try:
                added = kb.ingest(f.name, f.getvalue())
            except Exception as exc:  # one corrupt file shouldn't sink the rest
                warnings.append(f"**{f.name}** couldn't be read and was skipped ({exc}).")
                continue
            if added == 0:
                # No text came out - almost always a scanned / image-only PDF.
                warnings.append(
                    f"**{f.name}** looks scanned/image-only - no text could be "
                    "extracted; OCR isn't supported."
                )
    else:
        kb.ingest_directory(SAMPLE_DOCS_DIR)
    return kb, warnings


# --- Step 1: the knowledge base --------------------------------------------
render_step("1. Your knowledge base", "Upload your documents, or try the built-in sample.")

uploaded = st.file_uploader(
    "Upload PDF, Word, text or markdown files",
    type=["pdf", "docx", "txt", "md"],
    accept_multiple_files=True,
    label_visibility="collapsed",
)

# Enforce the public-demo caps so a shared URL can't be abused.
if uploaded and settings.demo_mode:
    if len(uploaded) > settings.max_files:
        st.warning(f"Demo limit: please upload at most {settings.max_files} files.")
        uploaded = uploaded[: settings.max_files]
    too_big = [f.name for f in uploaded if f.size > settings.max_upload_mb * 1024 * 1024]
    if too_big:
        st.warning(
            f"Demo limit: these files exceed {settings.max_upload_mb}MB and were skipped: "
            + ", ".join(too_big)
        )
        uploaded = [f for f in uploaded if f.size <= settings.max_upload_mb * 1024 * 1024]

if problems:
    st.info(
        "Add your **OPENAI_API_KEY** to a `.env` file to enable answering. "
        "The interface works without it, but questions need a key."
    )

# (Re)build the index only when the document set actually changes - embedding
# costs money and time, so we cache the knowledge base in the session.
sig = _signature(uploaded)
if not problems and st.session_state.get("kb_sig") != sig:
    with st.spinner("Indexing your documents..."):
        try:
            kb_built, warnings = build_kb(uploaded)
            st.session_state.kb = kb_built
            st.session_state.kb_warnings = warnings
            st.session_state.kb_sig = sig
            st.session_state.messages = []  # fresh docs, fresh conversation
        except Exception as exc:  # surface a friendly error, don't crash
            st.error(f"Could not index the documents: {exc}")

kb: KnowledgeBase | None = st.session_state.get("kb")

# Per-file warnings: scanned/image-only PDFs and files we had to skip.
for warning in st.session_state.get("kb_warnings", []):
    st.warning(warning)

# If the whole knowledge base came out empty there's nothing to search, so say
# so prominently instead of letting every question return "not found".
if kb and kb.chunk_count == 0:
    st.error(
        "No readable text could be extracted from your documents, so there's "
        "nothing to search. If these are scanned PDFs, note that OCR isn't "
        "supported - please upload text-based files instead."
    )

if kb and kb.chunk_count > 0:
    if uploaded:
        st.caption(
            f"Ready - {len(kb.sources)} document(s), {kb.chunk_count} passages indexed: "
            + ", ".join(kb.sources)
        )
    else:
        st.caption("Using the sample **Lumen & Co. employee handbook**. Upload your own to replace it.")

st.divider()

# --- Step 2: ask -----------------------------------------------------------
render_step("2. Ask a question", "Plain English. Every answer shows its sources.")

if not uploaded and kb:
    st.caption(
        "Try: *How many holiday days do I get?* · *What's the remote working policy?* "
        "· *What can I claim for hotels?*"
    )

st.session_state.setdefault("messages", [])
st.session_state.setdefault("question_count", 0)

# Replay the conversation so far.
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        for cite in msg.get("citations", []):
            with st.expander(f"[{cite['index']}] {cite['location']}"):
                st.markdown(cite["snippet"])

# Demo cap on questions.
capped = settings.demo_mode and st.session_state.question_count >= settings.demo_question_limit
if capped:
    st.info(
        f"You've reached the demo limit of {settings.demo_question_limit} questions. "
        "This cap exists so a public demo can't run up the bill - a private "
        "deployment for your team has no limit."
    )

# Only allow questions once there's something searchable in the index.
kb_ready = bool(kb and kb.chunk_count > 0)
prompt = st.chat_input("Ask anything about your data...", disabled=capped or not kb_ready)
if prompt and kb_ready:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching your documents..."):
            try:
                answer = kb.ask(prompt)
            except Exception as exc:
                answer = None
                st.error(f"Something went wrong: {exc}")

        if answer is not None:
            # `grounded` is False when the model found nothing relevant and said
            # so. Render that in a muted style and skip the (empty) citation
            # block, so a "not found" reply reads clearly as an honest miss
            # rather than a failed answer.
            if answer.grounded:
                st.markdown(answer.text)
                citations = [c.model_dump() for c in answer.citations]
                for cite in citations:
                    with st.expander(f"[{cite['index']}] {cite['location']}"):
                        st.markdown(cite["snippet"])
            else:
                st.markdown(f":grey[{answer.text}]")
                citations = []
            st.session_state.messages.append(
                {"role": "assistant", "content": answer.text, "citations": citations}
            )
            st.session_state.question_count += 1

render_footer()
