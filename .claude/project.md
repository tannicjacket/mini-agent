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

### Retrieval Quality

### Index Lifecycle

### Tool Interface

### Future Architecture Notes
