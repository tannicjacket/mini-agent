# Runbook

## Purpose

This file records the main ways to run and inspect the current project.

## Main Entrypoints

- Default app entrypoint: `python src/mini_agent/main.py`
- MCP server: `python src/mini_agent/mcp/server.py`
- Legacy MCP compatibility entrypoint: `python src/mini_agent/mcp_server.py`

## Internal Runtime Files

- `src/mini_agent/agent/runner.py`: current runner called by `src/mini_agent/main.py`

## RAG Workflow

- Build or rebuild the demo index: `python src/mini_agent/rag/build_index.py`
- Run a direct retrieval check: `python src/mini_agent/rag/search.py "your query"`

## Environment Notes

- API access is loaded through `src/mini_agent/config.py`
- The current code expects `API_KEY` to be set
- `src/mini_agent/mcp/server.py` requires the `mcp` package to be installed

## Harness Docs Workflow

- Commit harness Markdown files on the `harness-doc` branch

## Verification

- Prefer checking the default chat entrypoint after changing chat, tools, or agent flow
- Prefer checking direct retrieval after changing `rag/` or `tools/docs_search.py`
- Prefer checking the MCP server entrypoint after changing `mcp/` or MCP-exposed tools

## RAG Planning

### Evaluation

No evaluation harness exists yet. Planned for a later phase; do not add commands here until something runnable lands.

### Data Source

Documents are hardcoded in `src/mini_agent/rag/build_index.py` as a Python list. There is no on-disk source-of-truth directory yet.

### Embedding Model

- Model: `Qwen/Qwen3-Embedding-0.6B`, downloaded via `modelscope.snapshot_download` on first use.
- Currently re-instantiated on every `search_documents` call (no process-level cache yet). Expect a per-call warm-up cost until this is changed.

### Retrieval Interface

- Tool entry: `search_docs(query: str) -> str`, returning `json.dumps([...])`.
- Underlying call: `search_documents(query, top_k=3)` in `src/mini_agent/rag/search.py`.
- Direct CLI check: `python src/mini_agent/rag/search.py "your query"`.
