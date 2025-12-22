# RAG-Based Assistant

A simple RAG pipeline that ingests corporate documents, chunks them, and indexes into ChromaDB for retrieval.

## Setup

1. Create and activate a Python environment (3.10+ recommended).
2. Install deps:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and adjust as needed.

## Environment Variables

- `ROOT_DATA_DIR`: Root folder for input/output data. Defaults to `./data`.
- `LOG_LEVEL`: Logging level (e.g., `INFO`, `DEBUG`).
- `CHROMA_EMBED_MODEL`: SentenceTransformer model name (default `all-MiniLM-L6-v2`).
- `CHROMA_COLLECTION`: ChromaDB collection name (default `corporate_documents`).

## Data Layout

```
data/
  finance/marketing/hr/engineering/general/
    chunked_reports/*.json   # produced by extraction step
  chroma_db/                 # Chroma persistence
```

## Ingest

Runs chunk processing and saves to ChromaDB:

```bash
python -m src.main
```

or directly:

```bash
python -c "from src.ingest import run_chunking; run_chunking()"
```

## Notes

- Re-runs use semantic IDs and `upsert`, so indexing is idempotent.
- Ensure `data/chunked_reports` JSONs exist before running `ingest`.
- Configure `ROOT_DATA_DIR` if your data folder is elsewhere.
