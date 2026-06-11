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

## Verification

- Prefer checking the default chat entrypoint after changing chat, tools, or agent flow
- Prefer checking direct retrieval after changing `rag/` or `tools/docs_search.py`
- Prefer checking the MCP server entrypoint after changing `mcp/` or MCP-exposed tools

## RAG Planning

### Evaluation

### Data Source

### Embedding Model

### Retrieval Interface
