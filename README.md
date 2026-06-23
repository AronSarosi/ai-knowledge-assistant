# AI Knowledge Assistant

Ask your company's documents a question in plain English and get a **grounded,
cited answer** - with the exact source quoted so it's checkable in seconds. If
the answer isn't in your documents, it says so rather than guessing.

A portfolio piece for [aronsarosi.com](https://aronsarosi.com), and a real,
client-ready RAG (Retrieval-Augmented Generation) system.

---

## How it works (RAG in four steps)

```
                 ┌──────────┐   ┌──────────┐   ┌────────────────┐
  Your docs ───▶ │  INGEST  │──▶│  EMBED   │──▶│  VECTOR STORE  │
  (PDF/Word/...) │ parse +  │   │ meaning  │   │ search by      │
                 │ chunk    │   │ → vectors│   │ meaning        │
                 └──────────┘   └──────────┘   └────────┬───────┘
                                                         │ top matches
  Question ──────────────────────────────────────▶ RETRIEVE
                                                         │
                                                         ▼
                                                   ┌──────────┐
                                                   │  ANSWER  │  grounded +
                                                   │  (LLM)   │  cited, or
                                                   └──────────┘  "not found"
```

1. **Ingest** (`rag/ingest.py`) - pull text out of PDF / Word / text / markdown
   and split it into ~1000-character overlapping **chunks**, keeping page numbers
   for citations.
2. **Embed + store** (`rag/store.py`) - turn each chunk into an **embedding** (a
   vector capturing its meaning) and keep it in a **vector store** that finds text
   by meaning, not keywords.
3. **Retrieve** - embed the question, fetch the few most relevant chunks.
4. **Answer** (`rag/answer.py`) - hand *only* those chunks to the model, which
   answers using just them, **cites** each claim, and refuses when the answer
   isn't there.

The whole thing is one small object - see `rag/pipeline.py`:

```python
kb = KnowledgeBase(settings)
kb.ingest("handbook.pdf", file_bytes)
answer = kb.ask("How much annual leave do I get?")
```

## Run it locally

```bash
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy .env.example .env          # then add your OPENAI_API_KEY
streamlit run app.py
```

Open http://localhost:8501. It loads with a sample employee handbook so you can
try it immediately; upload your own documents to replace it.

## Run it as a container

```bash
docker build -t knowledge-assistant .
docker run -p 8080:8080 -e PORT=8080 -e OPENAI_API_KEY=sk-... knowledge-assistant
```

Open http://localhost:8080. The same image deploys to Google Cloud Run, AWS, or
a client's cloud unchanged - that portability is the point of containerising it.

## Configuration

Everything is set via environment variables (see `.env.example`):

| Variable | Purpose | Default |
|---|---|---|
| `OPENAI_API_KEY` | OpenAI key (required) | - |
| `OPENAI_MODEL` | Chat model for answering | `gpt-4o-mini` |
| `OPENAI_EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `LLM_PROVIDER` | `openai` or `azure` | `openai` |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | Chunking | `1000` / `150` |
| `TOP_K` | Chunks retrieved per question | `4` |
| `DEMO_MODE` | Caps for a public demo | `true` |
| `DEMO_QUESTION_LIMIT` / `MAX_UPLOAD_MB` / `MAX_FILES` | The caps | `15` / `10` / `5` |

## From demo to production (what changes for a client)

This build keeps the index **in memory** so it needs zero infrastructure - ideal
for a demo and for handing over a self-contained container. For a larger client
deployment you swap a single piece - the `VectorStore` class in `rag/store.py` -
for a **persistent** vector database (pgvector, Qdrant, or Pinecone) so the index
survives restarts and scales to millions of passages. Nothing else in the app
changes. That swap-one-piece design is deliberate.

Turn `DEMO_MODE=false` to lift the public-demo caps for an internal deployment.

---

*Built by Aron Sarosi. Answers are generated from the documents you provide and
shown with their sources - always check the cited passage before relying on an
answer for anything important.*
