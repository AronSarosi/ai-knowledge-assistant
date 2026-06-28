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

# The form "Ask" button needs white text on the terracotta background (Streamlit's
# form-submit button doesn't inherit the theme's primary-button colour by default).
st.markdown(
    """
    <style>
    [data-testid="stFormSubmitButton"] button {
      background: #B5532E !important;
      border: none !important;
      box-shadow: 0 10px 26px -10px rgba(181,83,46,0.75) !important;
    }
    [data-testid="stFormSubmitButton"] button,
    [data-testid="stFormSubmitButton"] button p { color: #FFFFFF !important; }
    [data-testid="stFormSubmitButton"] button:hover { background: #99431F !important; }
    /* Disabled upload control in the demo: a plain cursor, not a "not allowed" sign. */
    [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploaderDropzone"] * { cursor: default !important; }
    /* Opened sample document: render it like a paper page, in a smaller font.
       The container key changes per document (docpage_0, docpage_1, ...), so
       switching documents creates a fresh element that starts scrolled at the
       top - hence the prefix match here rather than an exact class. */
    [class*="st-key-docpage"] { background:#EDE8E0; border:1px solid #E0D8CB; border-radius:12px; padding:16px; }
    [class*="st-key-docpage"] [data-testid="stMarkdownContainer"] {
      background:#fff; border:1px solid #E6DFD3; border-radius:6px;
      box-shadow:0 1px 5px rgba(34,30,25,0.10);
      max-width:680px; margin:0 auto; padding:30px 40px;
      font-size:0.8rem; line-height:1.65; color:#3d3a34;
    }
    [class*="st-key-docpage"] h1 { font-size:1.1rem !important; margin:0 0 0.3rem; }
    [class*="st-key-docpage"] h2 { font-size:0.92rem !important; margin-top:1.1rem; }
    [class*="st-key-docpage"] p, [class*="st-key-docpage"] li { font-size:0.8rem !important; color:#3d3a34; }
    [class*="st-key-docpage"] blockquote, [class*="st-key-docpage"] em { color:#8A8175; }
    </style>
    """,
    unsafe_allow_html=True,
)

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


def _doc_title(path) -> str:
    """'lumen-co-it-security-policy.md' -> 'IT Security Policy' (tab label)."""
    stem = path.stem
    for prefix in ("lumen-co-", "lumen-"):
        if stem.startswith(prefix):
            stem = stem[len(prefix):]
    return stem.replace("-", " ").title().replace("It ", "IT ")


def _toggle_preview(name: str) -> None:
    """Show the clicked document, or hide it if it was already open."""
    current = st.session_state.get("preview_doc")
    st.session_state.preview_doc = None if current == name else name


# --- Step 1: the knowledge base --------------------------------------------
if settings.demo_mode:
    render_step(
        "1. The sample knowledge base",
        "This live demo runs on a small, pre-loaded sample. Uploads are switched "
        "off here - just ask your questions against the sample below.",
    )
else:
    render_step("1. Your knowledge base", "Upload your documents, or try the built-in sample.")

uploaded = st.file_uploader(
    "Upload PDF, Word, text or markdown files",
    type=["pdf", "docx", "txt", "md"],
    accept_multiple_files=True,
    label_visibility="collapsed",
    disabled=settings.demo_mode,
)
if settings.demo_mode:
    uploaded = None
    st.caption(
        "Uploads are off in this demo - the sample documents below are already "
        "loaded for you, so you can try it straight away."
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
        files = sorted(p for p in SAMPLE_DOCS_DIR.glob("*") if p.is_file())
        st.caption(
            f"For this demo, a sample set of **{len(files)} documents** is pre-loaded "
            f"({kb.chunk_count} passages indexed). Click a document to read it - this "
            "is the data your questions run against."
        )
        cols = st.columns(len(files))
        for i, (col, path) in enumerate(zip(cols, files)):
            col.button(
                f"📄 {_doc_title(path)}",
                key=f"doc_{i}",
                on_click=_toggle_preview,
                args=(path.name,),
                use_container_width=True,
            )
        sel = st.session_state.get("preview_doc")
        if sel and (SAMPLE_DOCS_DIR / sel).is_file():
            sel_idx = next((i for i, p in enumerate(files) if p.name == sel), None)
            if sel_idx is not None:
                # Mark the open document's card with a neutral grey "active" look.
                st.markdown(
                    f"<style>.st-key-doc_{sel_idx} button {{ background:#ECE7DE !important; "
                    f"border-color:#D8CFC0 !important; }} "
                    f".st-key-doc_{sel_idx} button p {{ color:#5B544B !important; }}</style>",
                    unsafe_allow_html=True,
                )
            with st.container(height=420, key=f"docpage_{sel_idx}"):
                st.markdown((SAMPLE_DOCS_DIR / sel).read_text(encoding="utf-8"))

st.divider()

# --- Step 2: ask -----------------------------------------------------------
render_step("2. Ask a question", "Plain English. Every answer shows its sources.")

st.session_state.setdefault("messages", [])
st.session_state.setdefault("question_count", 0)

capped = settings.demo_mode and st.session_state.question_count >= settings.demo_question_limit
kb_ready = bool(kb and kb.chunk_count > 0)

# The question box sits inline, right under the heading, at the page width (not
# pinned to the bottom of the window). A form so Enter submits and it clears.
with st.form("ask", clear_on_submit=True):
    typed = st.text_input(
        "Your question",
        placeholder="Ask anything about your data...",
        label_visibility="collapsed",
        disabled=capped or not kb_ready,
    )
    submitted = st.form_submit_button(
        "Ask", type="primary", disabled=capped or not kb_ready
    )

# Example questions, directly below the box.
if not uploaded and kb:
    st.caption(
        "Try: *What's the remote working policy?* · *How do I report a security incident?*"
    )

if capped:
    st.info(
        f"You've reached the demo limit of {settings.demo_question_limit} questions. "
        "This cap exists so a public demo can't run up the bill - a private "
        "deployment for your team has no limit."
    )

# Handle a new question, then render the whole thread below.
prompt = typed.strip()[:500] if (submitted and typed and typed.strip()) else None
if prompt and kb_ready:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("Searching your documents..."):
        try:
            answer = kb.ask(prompt)
        except Exception as exc:
            answer = None
            st.error(f"Something went wrong: {exc}")
    if answer is not None:
        # `grounded` is False when the model found nothing relevant and said so;
        # we render that in muted grey so a "not found" reads as an honest miss.
        citations = [c.model_dump() for c in answer.citations] if answer.grounded else []
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer.text,
                "citations": citations,
                "grounded": answer.grounded,
            }
        )
        st.session_state.question_count += 1

# The conversation so far (newest at the bottom). Neutral avatars - a person for
# the question, a page for the sourced answer - instead of the default coloured faces.
for msg in st.session_state.messages:
    with st.chat_message(
        msg["role"], avatar="👤" if msg["role"] == "user" else "📄"
    ):
        if msg["role"] == "assistant" and msg.get("grounded") is False:
            st.markdown(f":grey[{msg['content']}]")
        else:
            st.markdown(msg["content"])
        for cite in msg.get("citations", []):
            with st.expander(f"[{cite['index']}] {cite['location']}"):
                st.markdown(cite["snippet"])

render_footer()
