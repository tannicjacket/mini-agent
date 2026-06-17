# mini-agent

一个用于循序渐进学习 Python、tool calling、RAG 和 agent 开发的练习项目。  
A learning project for gradually exploring Python, tool calling, RAG, and agent development.

## Contents

- [Overview](#overview)
- [Current Status](#current-status)
- [Runtime](#runtime)
- [Project Layout](#project-layout)
- [RAG Roadmap](#rag-roadmap)

## Overview

当前主代码已经收拢到 `src/mini_agent/`。默认运行路径是本地 `tool calling + RAG` 聊天流程；`examples/` 只保留兼容入口，不再承载主实现。  
The main code now lives under `src/mini_agent/`. The default runtime is a local `tool calling + RAG` chat flow; `examples/` is kept only as a compatibility layer.

## Current Status

### Completed / 已完成

- 已完成 `chat / tools / rag / mcp / agent` 的基础目录重构。  
  The base `chat / tools / rag / mcp / agent` structure has been refactored into place.

- 默认运行链路已经统一为 `main.py -> agent/runner.py -> chat/loop.py`。  
  The default runtime path is now unified as `main.py -> agent/runner.py -> chat/loop.py`.

- 已接入三个本地工具：`weather`、`web`、`search_docs`。  
  Three local tools are wired in: `weather`, `web`, and `search_docs`.

- 已完成最小可运行 RAG demo，embedding 模型是 `Qwen/Qwen3-Embedding-0.6B`。  
  A minimal runnable RAG demo is in place, using `Qwen/Qwen3-Embedding-0.6B`.

- 已完成 `RAG Phase A: Retrieval Contract Cleanup`：`search_docs` 不再返回裸 top-k JSON，而是返回带 `evidence_id`、`abstain`、`abstain_reason` 和 `model_instructions` 的 typed envelope。  
  `RAG Phase A: Retrieval Contract Cleanup` is complete: `search_docs` no longer returns raw top-k JSON and now returns a typed envelope with `evidence_id`, `abstain`, `abstain_reason`, and `model_instructions`.

- 已完成 `RAG Phase B: Model Lifecycle`：embedding model 和索引数据已经改成 process-level cache，同一 Python 进程里不会每次检索都重新加载。  
  `RAG Phase B: Model Lifecycle` is complete: the embedding model and index data now use a process-level cache and are not reloaded on every retrieval inside the same Python process.

- 已完成 `RAG Phase C: Chunking`：检索单元已经从整篇文档切换到 chunk，索引产物改成 `chunks.json + chunk_embeddings.npy`，并引入稳定的 `doc_id / chunk_id`。  
  `RAG Phase C: Chunking` is complete: the retrieval unit has moved from whole documents to chunks, the index artifacts are now `chunks.json + chunk_embeddings.npy`, and stable `doc_id / chunk_id` identifiers are in place.

- MCP server 已单独整理到 `src/mini_agent/mcp/server.py`。  
  The MCP server has been separated into `src/mini_agent/mcp/server.py`.

### In Progress / 当前进行中

当前正在准备“最小可行 RAG”的下一步：在 chunk-level retrieval 已跑通后，继续考虑最小持久化存储、evaluation 和更细的质量优化。  
The current focus is the next step for the minimal RAG path: now that chunk-level retrieval is in place, move on to minimal persistent storage, evaluation, and finer-grained quality work.

当前阶段：`RAG Phase D: Minimal Persistent Storage`（规划中）  
Current phase: `RAG Phase D: Minimal Persistent Storage` (planning)

当前进度：

- 已完成 retrieval contract 改造。  
  The retrieval contract refactor is complete.

- 已完成进程内 model / index lifecycle 优化。  
  The in-process model / index lifecycle optimization is complete.

- 已完成 chunk-level retrieval、稳定 `doc_id / chunk_id`、以及最小 chunk overlap 切分。  
  Chunk-level retrieval, stable `doc_id / chunk_id`, and minimal chunk-overlap splitting are complete.

- 当前还没有真正的持久化 store、evaluation workflow、hybrid retrieval 或 reranker。  
  There is still no real persistent store, evaluation workflow, hybrid retrieval, or reranker.

### Next / 下一步

- 继续把当前两文件 artifact（`chunks.json + chunk_embeddings.npy`）往更稳定的持久化形态推进。  
  Move the current two-file artifact pair (`chunks.json + chunk_embeddings.npy`) toward a more stable persistence shape.

- 在 chunking 稳定之后补最小可运行的 evaluation workflow。  
  Add a minimal runnable evaluation workflow after chunking has stabilized.

- 再根据 bad case 决定是否需要 hybrid retrieval 和 reranking。  
  Then decide whether hybrid retrieval and reranking are needed based on real bad cases.

## Runtime

推荐从项目根目录启动，并使用项目自己的 `.venv`。  
Run from the project root and prefer the project-local `.venv`.

```bash
source .venv/bin/activate
python src/mini_agent/main.py
python src/mini_agent/rag/build_index.py
python src/mini_agent/rag/search.py "Pro 订阅多少钱"
python src/mini_agent/mcp/server.py
```

说明：

- `src/mini_agent/main.py`：当前默认主入口。  
  `src/mini_agent/main.py`: current default app entrypoint.

- `src/mini_agent/mcp/server.py`：独立 MCP server 入口，不是默认运行链路。  
  `src/mini_agent/mcp/server.py`: standalone MCP server entrypoint, not the default runtime path.

- `examples/mini_chatbot/`：旧路径兼容入口。  
  `examples/mini_chatbot/`: legacy compatibility entrypoints.

- `search_docs` 现在返回的是 retrieval envelope；chat prompt 已具备 citation / abstain 规则。  
  `search_docs` now returns a retrieval envelope, and the chat prompt already includes citation / abstain rules.

- `build_index.py` 现在会生成 `chunks.json` 和 `chunk_embeddings.npy`，不再是 document-level 的 `documents.json + doc_embeddings.npy`。  
  `build_index.py` now generates `chunks.json` and `chunk_embeddings.npy` instead of the old document-level `documents.json + doc_embeddings.npy`.

- 在同一个 Python 进程里，embedding model 和索引会复用 cache；因此默认 chat 入口更能体现 Phase B 的收益。  
  Within the same Python process, the embedding model and index are reused from cache, so the default chat entrypoint shows the Phase B benefit more clearly.

## Project Layout

### Core App / 核心应用

- [src/mini_agent/main.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/main.py)  
  项目总入口。  
  Project entrypoint.

- [src/mini_agent/agent/runner.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/agent/runner.py)  
  当前默认跑的 agent runner。  
  The current default agent runner.

- [src/mini_agent/chat/loop.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/chat/loop.py)  
  基础 chat 与 tool chat 的主循环。  
  Main loop for both the basic chat and the tool chat.

- [src/mini_agent/chat/client.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/chat/client.py)  
  OpenAI client 初始化。  
  OpenAI client initialization.

- [src/mini_agent/chat/prompts.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/chat/prompts.py)  
  当前 chat prompt。  
  Current chat prompts.

### Tools / 工具层

- [src/mini_agent/tools/weather.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/tools/weather.py)  
  天气 mock tool。  
  Weather mock tool.

- [src/mini_agent/tools/web.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/tools/web.py)  
  网页抓取与正文提取。  
  Web fetching and page-content extraction.

- [src/mini_agent/tools/docs_search.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/tools/docs_search.py)  
  RAG 工具边界。  
  Tool boundary for RAG retrieval.

### RAG / 检索层

- [src/mini_agent/rag/contract.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/rag/contract.py)  
  定义 `RetrievalResult`、`Evidence` 和给模型的固定 retrieval 规则。  
  Defines `RetrievalResult`, `Evidence`, and the fixed retrieval rules given to the model.

- [src/mini_agent/rag/chunking.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/rag/chunking.py)  
  负责最小 chunk 切分逻辑（断句、收口、overlap）。  
  Holds the minimal chunking logic (sentence splitting, greedy packing, overlap).

- [src/mini_agent/rag/build_index.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/rag/build_index.py)  
  构建 chunk-level demo 索引。  
  Builds the chunk-level demo index.

- [src/mini_agent/rag/search.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/rag/search.py)  
  执行 chunk-level dense retrieval。  
  Executes chunk-level dense retrieval.

- [src/mini_agent/rag/data/chunks.json](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/rag/data/chunks.json)  
  chunk 记录数据，带 `chunk_id / doc_id / title / url / text`。  
  Chunk record data with `chunk_id / doc_id / title / url / text`.

- [src/mini_agent/rag/data/chunk_embeddings.npy](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/rag/data/chunk_embeddings.npy)  
  与 `chunks.json` 按下标一一对应的 chunk 向量索引。  
  The chunk embedding index aligned by array position with `chunks.json`.

### MCP / 协议层

- [src/mini_agent/mcp/server.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/mcp/server.py)  
  正式 MCP server 入口。  
  Formal MCP server entrypoint.

- [src/mini_agent/mcp_server.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/mcp_server.py)  
  旧路径兼容壳。  
  Legacy compatibility shim.

### Compatibility / 兼容入口

- [examples/mini_chatbot/chatbot.py](/Users/jiaenxu/Documents/mini-agent/examples/mini_chatbot/chatbot.py)  
- [examples/mini_chatbot/chatbot_v2.py](/Users/jiaenxu/Documents/mini-agent/examples/mini_chatbot/chatbot_v2.py)  
- [examples/mini_chatbot/main.py](/Users/jiaenxu/Documents/mini-agent/examples/mini_chatbot/main.py)

## RAG Roadmap

### Phase A — Retrieval Contract Cleanup

已完成。`search_docs` 已经从原始 top-k JSON 改成 typed retrieval envelope；chat prompt 也已经加入 citation 与 abstain 规则。  
Done. `search_docs` now returns a typed retrieval envelope, and the chat prompt includes citation and abstain rules.

当前结果：

- `RetrievalResult` envelope 已落地。  
  The `RetrievalResult` envelope is now in place.

- 证据现在带稳定的 `evidence_id`（`E1`、`E2`...）。  
  Evidence now carries stable `evidence_id` values (`E1`, `E2`, ...).

- 低相关查询会触发 `abstain`。  
  Low-relevance queries can now trigger `abstain`.

### Phase B — Model Lifecycle

已完成。embedding model 和索引文件已改成 process-level cache：首次冷启动较慢，后续同一进程内复用。  
Done. The embedding model and index files now use a process-level cache: the first call is still a cold start, while later calls reuse the same in-process objects.

当前限制：

- cache 只在单个 Python 进程内生效。  
  The cache only works within a single Python process.

- CLI 每次启动新进程时，仍然会重新初始化运行时资源。  
  CLI still reinitializes runtime resources when each invocation starts a fresh process.

### Phase C — Chunking

已完成。检索单元已经从 document-level 切到 chunk-level，并引入了稳定的 `doc_id / chunk_id`。  
Done. The retrieval unit has moved from document-level to chunk-level, with stable `doc_id / chunk_id` identifiers.

当前结果：

- `build_index.py` 会先断句、再按 `max_chars + overlap` 规则切块。  
  `build_index.py` now splits text into chunks using sentence boundaries plus `max_chars + overlap`.

- 向量索引产物已切换到 `chunks.json + chunk_embeddings.npy`。  
  The index artifacts have been switched to `chunks.json + chunk_embeddings.npy`.

- `search.py` 返回的 raw top-k 结果已带 `chunk_id` 和 `doc_id`。  
  The raw top-k results returned by `search.py` now include `chunk_id` and `doc_id`.

### Phase D — Minimal Persistent Storage

当前准备进入这个阶段。下一步是把现在的两文件 artifact 继续推进成更稳定、可演化的最小持久化方案。  
This is the next planned phase. The next step is to evolve the current two-file artifact setup into a more stable minimal persistence design.

### Evaluation

尚未开始。后续会在 chunking 稳定后补一套最小可运行的 evaluation workflow。  
Not started yet. A minimal runnable evaluation workflow will be added after chunking stabilizes.

### Hybrid Retrieval

尚未开始。当前仍然是单一路径的 dense retrieval。  
Not started yet. The current retrieval path is still dense-only.

### Reranking

尚未开始。当前 top-k 结果还没有单独的 reranker 阶段。  
Not started yet. The current top-k results do not yet have a dedicated reranking stage.
