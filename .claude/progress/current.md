# Current Progress

## Purpose

This file stores short-lived working context for the current project phase.

## Current Focus

- The main project is evolving from chatbot demos into a structured mini agent project under `src/mini_agent/`
- The current default flow is a local tool-calling chat loop with RAG support
- MCP exists, but it is currently a separate path rather than the default runtime path

## What Is Already Present

- Chat loop with local tool calling
- Weather and web tools
- `search_docs` wired to the RAG module
- Demo RAG index and document data
- MCP server wrapper for the web content tool

## Active Discussion

- We are currently discussing how to improve and structure the RAG part of the project

## Next Memory To Fill In Later

### Current Goal

Redesign the RAG subsystem in small, learning-oriented phases. Currently entering Phase A: cleaning up the retrieval contract between the RAG layer and the chat loop.

### Latest Decision

Adopt a step-by-step progression (contract → model lifecycle → chunking → minimal persistent storage → quality → evaluation). Defer the final storage backend, hybrid retrieval, reranking, and any multi-tenant or serviceization work until the foundational phases are stable. Any storage introduced in early phases is treated as transitional, not a long-term commitment.

### Next Step

Phase A — retrieval contract cleanup:

- Define a typed `RetrievalResult` envelope: evidence list with stable `evidence_id`, `abstain` flag and reason, embedded `model_instructions`.
- Update `search_docs` to return that envelope, serialized as JSON at the tool boundary.
- Update the chat-loop system prompt to require `[E#]`-style citations and to refuse when `abstain` is true.
- Add a minimal placeholder threshold for abstain; real calibration is a later phase.

### Risks

- The `.env` file may contain a real API key — needs local verification before any commit or push.
- Changing the `search_docs` return shape touches the chat loop; `loop.py` and the system prompt must move in lockstep.
- Introducing an abstain path may surface previously hidden bad cases — desirable, but the user-facing message for "no answer" should be sane.

## RAG Planning

### Problem Statement

Today's RAG path returns raw similarity-ranked JSON to the model with no notion of evidence, citation, or refusal. The model can hallucinate over weak retrieval, cannot reliably cite sources, and has no signal that retrieval failed. The highest-leverage first improvement is therefore the contract between RAG and the chat loop — not storage, not retrieval quality.

### Retrieval Pipeline

Phase A target only:

1. Embed the query (current per-call lifecycle; process-level caching is Phase B).
2. Dense top-k against the existing flat index.
3. Apply a placeholder threshold on the top-1 score; below it, set `abstain=True` and return empty evidence.
4. Build and return a `RetrievalResult` envelope with stable `evidence_id`s and embedded model instructions.

Pipelines for later phases (chunking, persistent store, hybrid, rerank) are intentionally not specified here yet.

### Data Model

Deferred. The introduction of `doc_id`, `chunk_id`, and `chunk_hash` will be designed when chunking lands; no schema is committed now.

### Evaluation Plan

Deferred. Will start from a small hand-labeled golden set (`query → expected chunk_ids`, `should_abstain`) and basic offline metrics; no harness or commands exist yet.

### Open Questions

- Final storage backend (`pgvector`, `sqlite-vss`, plain SQLite + numpy, or something else) — not decided. The minimal storage layer planned for an early phase is explicitly transitional.
- When to introduce hybrid retrieval (BM25 / FTS) — gated on bad cases surfaced by the future evaluation set.
- When to introduce a cross-encoder reranker — same gate.
- Whether the retrieval path needs async or concurrency at all — not decided.
- Whether `tenant_id` / ACL should ever affect the runtime interface — currently future direction only, no schema or runtime commitment.
- How much backend abstraction (Protocol / ABC) is justified — defer until a second implementation actually exists.
- Appropriate observability depth in early phases (structured stdout vs metrics endpoint) — not decided.
