# mini-agent

一个用于循序渐进学习 Python、tool calling、RAG 和 agent 开发的练习项目。  
A learning project for gradually exploring Python, tool calling, RAG, and agent development.

## Contents

- [Overview](#overview)
- [Current Status](#current-status)
- [Runtime](#runtime)
- [Project Layout](#project-layout)
- [RAG Roadmap](#rag-roadmap)
- [Claude Harness](#claude-harness)

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

当前正在处理“最小可行 RAG”的下一步问题：先清理 retrieval contract，再考虑质量、存储和评测。  
The current focus is the next step for the minimal RAG path: clean up the retrieval contract first, then move on to quality, storage, and evaluation.

当前阶段：`RAG Phase A: Retrieval Contract Cleanup`  
Current phase: `RAG Phase A: Retrieval Contract Cleanup`

当前进度：

- 已完成问题定义和 pre-execution note。  
  The problem framing and pre-execution note are done.

- 已明确本期目标是改 `RAG -> chat loop` 的接口契约，不是提升检索质量。  
  The current scope is explicitly the `RAG -> chat loop` contract, not retrieval quality.

- 代码实现还没开始。  
  The code implementation has not started yet.

### Next / 下一步

- 把 `search_docs` 从“裸 JSON top-k”改成带 `evidence_id`、`abstain` 和 `model_instructions` 的 typed envelope。  
  Change `search_docs` from raw top-k JSON into a typed envelope with `evidence_id`, `abstain`, and `model_instructions`.

- 更新 prompt，让模型学会在 RAG 路径里引用和拒答。  
  Update the prompt so the model can cite and abstain properly in the RAG path.

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

### Notes / 学习记录

- [docs/rag-note.md](/Users/jiaenxu/Documents/mini-agent/docs/rag-note.md)  
  当前 RAG 学习线的 pre-execution note / worklog。  
  The current RAG pre-execution note and worklog.

## RAG Roadmap

### Phase A — Retrieval Contract Cleanup

当前是这个阶段。目标是把 `search_docs` 从原始 top-k JSON 改成更明确的 retrieval contract，并让 chat 层理解 citation 与 abstain。  
This is the current phase. The goal is to replace raw top-k JSON with a clearer retrieval contract and make the chat layer understand citation and abstain behavior.

当前限制：

- 只有 document-level 向量，没有 chunking。  
  Retrieval is still document-level only, with no chunking.

- 每次检索都会重新加载 embedding 模型。  
  The embedding model is reloaded on every retrieval call.

- 低相关问题仍会被强制返回 top-k。  
  Low-relevance queries still force a top-k result.

### Phase B — Model Lifecycle

### Phase C — Chunking

### Phase D — Minimal Persistent Storage

### Evaluation

### Hybrid Retrieval

### Reranking

## Claude Harness

这一部分记录的是项目里的 Claude harness 结构，不是业务代码。它的作用是让后续会话能快速恢复项目上下文、运行方式和当前工作阶段。  
This section describes the Claude harness structure in the repo, not the product code. Its job is to help later sessions recover project context, runtime paths, and the current work phase quickly.

### Memory Files / 记忆文件

- [CLAUDE.md](/Users/jiaenxu/Documents/mini-agent/CLAUDE.md)  
  项目级协作约束：回复语言、作用域限制、以及 `.claude` 文档的职责边界。  
  Project-level collaboration rules: response language, scope limits, and the responsibility split inside `.claude`.

- [.claude/project.md](/Users/jiaenxu/Documents/mini-agent/.claude/project.md)  
  稳定 project memory，记录长期有效的架构、RAG 现状和未来方向。  
  Stable project memory for architecture, current RAG shape, and long-term direction.

- [.claude/runbook.md](/Users/jiaenxu/Documents/mini-agent/.claude/runbook.md)  
  运行手册，记录当前可执行入口、RAG 命令和验证方式。  
  Runbook for current entrypoints, RAG commands, and verification paths.

- [.claude/progress/current.md](/Users/jiaenxu/Documents/mini-agent/.claude/progress/current.md)  
  短期 working context，记录当前 focus、下一个阶段和暂时风险。  
  Short-lived working context for the current focus, next phase, and immediate risks.

- [.claude/commands/resume.md](/Users/jiaenxu/Documents/mini-agent/.claude/commands/resume.md)  
  恢复上下文命令，告诉 Claude 下一次进入仓库时应该先读哪些文件，并输出什么摘要。  
  Resume command that tells Claude which files to read first and what summary to produce on re-entry.

### Skill / 学习技能

- [.claude/skills/learning-note/SKILL.md](/Users/jiaenxu/Documents/mini-agent/.claude/skills/learning-note/SKILL.md)  
  在开始一个新 module / phase 之前，先写 pre-execution note，帮助把“为什么要这样改”讲清楚。  
  Writes a pre-execution note before a new module or phase so the change is understandable before coding starts.

- [.claude/skills/learning-note/references/example-phase-a-overview.md](/Users/jiaenxu/Documents/mini-agent/.claude/skills/learning-note/references/example-phase-a-overview.md)  
  `learning-note` 的校准样例，定义 note 的深度、7-section 结构和语气。  
  Calibration example for `learning-note`, defining the note depth, 7-section shape, and tone.

### Local Settings / 本地设置

- `.claude/settings.local.json`  
  可选的本地 Claude 权限配置，通常不会提交到仓库。  
  Optional local Claude permission configuration, usually not committed to the repository.
