# Project Memory

## Purpose

This file stores stable project context that is useful across sessions.

## Scope

- In scope: `src/mini_agent/`, `examples/`, `README.md`, and `pyproject.toml`
- Out of scope by default: `mini_demo/`
- Ignore by default: `python-playground` branch

## Current Structure

- `src/mini_agent/main.py`: default project entrypoint
- `src/mini_agent/agent/runner.py`: current mini agent runner used by the main entrypoint
- `src/mini_agent/chat/`: chat client, prompts, and local tool-calling loop
- `src/mini_agent/tools/`: reusable tools such as weather, web, and docs search
- `src/mini_agent/rag/`: RAG indexing and retrieval code plus demo data
- `src/mini_agent/mcp/server.py`: standalone MCP server entrypoint
- `examples/mini_chatbot/`: related compatibility and learning entrypoints, still relevant to the project

## Current Behavior

- The default main flow currently runs the local tool-calling chat loop.
- `search_docs` is wired into the chat loop and calls the RAG retrieval module.
- MCP support exists as a separate server entrypoint and is not the default tool execution path.

## Important Files

- `src/mini_agent/main.py`
- `src/mini_agent/agent/runner.py`
- `src/mini_agent/chat/loop.py`
- `src/mini_agent/tools/docs_search.py`
- `src/mini_agent/rag/build_index.py`
- `src/mini_agent/rag/search.py`
- `src/mini_agent/mcp/server.py`

## RAG Planning

### Current RAG Shape

- Documents are hardcoded as a Python list (`DOCUMENTS`) in `src/mini_agent/rag/build_index.py`.
- The built index lives in two files: `src/mini_agent/rag/data/documents.json` and `doc_embeddings.npy`.
- One vector per document (no sub-document chunking); the embedding array has shape `(N_docs, embedding_dim)`.
- `search_documents(query, top_k)` in `src/mini_agent/rag/search.py` loads the index, encodes the query, computes similarity, and returns top-k results as a list of dicts.
- The `search_docs` tool wraps that call and returns the result as a raw JSON string.
- The chat loop appends that JSON string to the message history as `role=tool` content with no further structure.

### Retrieval Quality

Stable limitations true today, independent of any planned phase:

- No chunking: long documents dilute their own embeddings; the retrieval unit is the entire document.
- No abstain signal: top-k is always returned, even when nothing is relevant; the model has no way to know retrieval failed.
- Dense-only top-k: no lexical or sparse signal for keyword-heavy queries such as entity names, error codes, or version numbers.
- Single embedding model with no calibration: similarity scores are raw dot products and are not directly interpretable as probabilities.
- No reranking step: precision is bounded by the dense recall stage.

### Index Lifecycle

- Building the index is a full overwrite: `build_index.py` re-encodes all documents and rewrites both files.
- No incremental update path, no stable document or chunk identity beyond array position, no version tracking, no content hashing.
- During a rebuild the on-disk index is briefly inconsistent — the two files are not updated atomically.

### Tool Interface

Current contract:

- `search_docs(query: str) -> str` returns `json.dumps([{index, score, title, url, text}, ...])`.
- The model receives raw JSON; nothing tells it which items are "evidence", that it must cite them, or what to do when results are weak.

Stable long-term direction:

- Replace the raw JSON return with a typed envelope (`RetrievalResult`) that carries:
  - an `evidence` list with stable `evidence_id`s (e.g. `E1`, `E2`) so model output can be checked for valid citations,
  - an `abstain` flag plus `abstain_reason` meaning "do not rely on this retrieval",
  - `model_instructions` embedded inline (citation grammar, refuse-when-empty rule).
- The chat loop validates that any citation in the model's reply references a real `evidence_id`.
- Raw similarity scores are not surfaced to the model; a coarse `confidence_band` may be exposed instead.

### Future Architecture Notes

High-level direction only. No backend choice, no phase schedule, no detailed schema is recorded here.

- RAG is shaped as a real subsystem (a `RagService`-style object), not a script — composed of an embedding component, a retrieval component, and a retrieval-policy component.
- Documents and chunks acquire stable identifiers and live in a persistent store with metadata, replacing the current two-file artifact.
- The retrieval-to-LLM contract stays evidence-oriented (typed envelope, citations, abstain) rather than raw text.
- Retrieval-quality decisions (thresholds, reranking, hybrid retrieval) are driven by an offline evaluation set rather than intuition.
- Multi-tenancy, ACL, and service extraction are acknowledged as possible future directions only — no schema commitment, no runtime interface commitment.
