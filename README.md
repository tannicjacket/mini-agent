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

- MCP server 已单独整理到 `src/mini_agent/mcp/server.py`。  
  The MCP server has been separated into `src/mini_agent/mcp/server.py`.

### In Progress / 当前进行中

当前正在处理“最小可行 RAG”的下一步问题：在 `Phase A/B` 已落地后，把 retrieval unit 从整篇文档推进到更合理的 chunk，并为后续质量校准和评测打基础。  
The current focus is the next step for the minimal RAG path: after Phase A/B have landed, move the retrieval unit from whole documents to more reasonable chunks and lay the groundwork for later quality calibration and evaluation.

当前阶段：`RAG Phase C: Chunking`（规划中）  
Current phase: `RAG Phase C: Chunking` (planning)

当前进度：

- `Phase A` 已完成：`search_docs` 不再返回裸 top-k JSON，而是返回带 `evidence_id`、`abstain` 和 `model_instructions` 的 typed envelope。  
  `Phase A` is complete: `search_docs` no longer returns raw top-k JSON and now returns a typed envelope with `evidence_id`, `abstain`, and `model_instructions`.

- `Phase B` 已完成：embedding model 和索引数据已经改成 process-level cache，不再每次检索都重新加载。  
  `Phase B` is complete: the embedding model and index data now use a process-level cache instead of being reloaded on every retrieval call.

- 当前仍然是 document-level dense retrieval，chunking、evaluation 和更细的质量优化还没开始。  
  The system is still document-level dense retrieval; chunking, evaluation, and finer-grained quality work have not started yet.

### Next / 下一步

- 把检索单元从整篇文档推进到更细粒度的 chunk。  
  Move the retrieval unit from whole documents to finer-grained chunks.

- 给后续的 `doc_id / chunk_id / chunk metadata` 设计打基础。  
  Lay the groundwork for future `doc_id / chunk_id / chunk metadata` design.

- 在 chunking 稳定后，再继续做 evaluation、hybrid retrieval 和 reranking。  
  After chunking is stable, continue with evaluation, hybrid retrieval, and reranking.

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

- [src/mini_agent/rag/build_index.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/rag/build_index.py)  
  构建 demo 索引。  
  Builds the demo index.

- [src/mini_agent/rag/search.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/rag/search.py)  
  执行 dense retrieval。  
  Executes dense retrieval.

- [src/mini_agent/rag/data/documents.json](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/rag/data/documents.json)  
  demo 文档数据。  
  Demo document data.

- [src/mini_agent/rag/data/doc_embeddings.npy](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/rag/data/doc_embeddings.npy)  
  demo 向量索引。  
  Demo embedding index.

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

已完成。`search_docs` 已从原始 top-k JSON 升级为更明确的 retrieval contract，chat 层也已理解 citation 与 abstain。  
Done. `search_docs` has been upgraded from raw top-k JSON into a clearer retrieval contract, and the chat layer now understands citation and abstain behavior.

当前限制：

- 只有 document-level 向量，没有 chunking。  
  Retrieval is still document-level only, with no chunking.

- 低相关问题仍会被强制返回 top-k。  
  Low-relevance queries still force a top-k result.

### Phase B — Model Lifecycle

已完成。embedding model 和索引文件已改成 process-level cache：首次冷启动较慢，后续同一进程内复用。  
Done. The embedding model and index files now use a process-level cache: the first call is still a cold start, while later calls reuse the same in-process objects.

### Phase C — Chunking

当前准备进入这个阶段。下一步会把 retrieval unit 从整篇文档推进到更细粒度的 chunk，并逐步补齐稳定 identifier 与 chunk metadata。  
This is the next planned phase. The retrieval unit will move from whole documents to finer-grained chunks, together with stable identifiers and chunk metadata.

当前目标：

- 把长文档拆成 chunk，避免一个 embedding 混合多个主题。  
  Split long documents into chunks so one embedding no longer blends multiple topics.

- 让检索命中的 `text` 从“整篇文档”变成“更聚焦的一段 chunk”。  
  Make retrieved `text` a focused chunk instead of an entire document.

- 为后续 evaluation、hybrid retrieval 和 reranking 铺路。  
  Prepare the ground for later evaluation, hybrid retrieval, and reranking.

### Phase D — Minimal Persistent Storage

### Evaluation

尚未开始。后续会在 chunking 稳定后补一套最小可运行的 evaluation workflow。  
Not started yet. A minimal runnable evaluation workflow will be added after chunking stabilizes.

### Hybrid Retrieval

### Reranking
