# mini-agent

一个用于循序渐进学习 Python、tool calling、RAG 和 agent 开发的练习项目。  
A learning project for gradually exploring Python, tool calling, RAG, and agent development.

## Chatbot Branch Summary / `chatbot` 分支摘要

`chatbot` 分支已经完成并合并到 `main`。这一阶段主要实现了一个最小可运行的 chatbot，以及一个带 tool calling 的 `chatbot_v2`。目前主实现已经收拢到 `src/mini_agent/`，`examples/` 只保留兼容入口。  
The `chatbot` branch has been completed and merged into `main`. This stage mainly adds a minimal runnable chatbot and a tool-calling `chatbot_v2`. The main implementation now lives under `src/mini_agent/`, while `examples/` is kept only as a compatibility entry layer.

### Scope / 范围说明

本节只描述 `chatbot` 这一条开发线的内容。后续如果增加 `mini_rag_bot`、`mini_agent` 或其他练习，可以继续按相同方式追加新的独立小节。  
This section only describes the `chatbot` development track. Future practice tracks such as `mini_rag_bot`, `mini_agent`, or others can be added as separate sections in the same style.

### Implemented Features / 已实现功能

- 基础单轮/多轮聊天 demo，使用 OpenAI API。  
  Basic single-turn and multi-turn chatbot demo using the OpenAI API.

- `chatbot_v2` 支持 tool calling。  
  `chatbot_v2` supports tool calling.

- 内置天气查询 mock tool。  
  Includes a mock weather lookup tool.

- 新增网页正文抓取工具 `get_page_content`，可提取页面主要文本内容。  
  Adds a web content tool `get_page_content` that extracts the main text from a page.

- 新增 `mcp_server.py`，把网页抓取能力注册为 MCP tool 的入口。  
  Adds `mcp_server.py` as an entrypoint for exposing the web content tool as an MCP tool.

### Relevant Paths / 相关路径

#### Chatbot Demos / Chatbot 示例

- [src/mini_agent/chat/client.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/chat/client.py)  
  OpenAI client 初始化。  
  OpenAI client initialization.

- [src/mini_agent/chat/prompts.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/chat/prompts.py)  
  基础聊天和 tool-calling 聊天使用的 system prompt。  
  System prompts for both the basic chat and the tool-calling chat.

- [src/mini_agent/chat/loop.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/chat/loop.py)  
  当前 chatbot 主流程，包含基础对话和 tool calling 循环。  
  Current chatbot main flow, including the basic chat loop and the tool-calling loop.

- [src/mini_agent/agent/runner.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/agent/runner.py)  
  当前默认 mini agent 入口，现阶段会运行 tool-calling chatbot。  
  Current default mini-agent entrypoint, which currently runs the tool-calling chatbot.

- [src/mini_agent/main.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/main.py)  
  项目默认运行入口。  
  Project default entrypoint.

- [examples/mini_chatbot/chatbot.py](/Users/jiaenxu/Documents/mini-agent/examples/mini_chatbot/chatbot.py)  
  旧的最小 chatbot 路径，现为兼容壳。  
  Old basic chatbot path, now kept as a compatibility shim.

- [examples/mini_chatbot/chatbot_v2.py](/Users/jiaenxu/Documents/mini-agent/examples/mini_chatbot/chatbot_v2.py)  
  旧的 tool-calling chatbot 路径，现为兼容壳。  
  Old tool-calling chatbot path, now kept as a compatibility shim.

#### Reusable Tools / 可复用工具

- [src/mini_agent/tools/web.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/tools/web.py)  
  网页抓取与正文提取工具。  
  Web fetching and page-content extraction tool.

- [src/mini_agent/tools/weather.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/tools/weather.py)  
  天气 mock tool。  
  Weather mock tool.

- [src/mini_agent/tools/docs_search.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/tools/docs_search.py)  
  文档检索 tool，内部调用 RAG 检索模块。  
  Documentation search tool that internally calls the RAG retrieval module.

- [src/mini_agent/tools/__init__.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/tools/__init__.py)  
  工具导出入口。  
  Tool export entrypoint.

#### MCP Server / MCP 服务入口

- [src/mini_agent/mcp/server.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/mcp/server.py)  
  正式 MCP server 入口，目前注册了 `get_page_content`。  
  Formal MCP server entrypoint, currently registering `get_page_content`.

- [src/mini_agent/mcp_server.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/mcp_server.py)  
  旧路径兼容入口，内部转发到 `src/mini_agent/mcp/server.py`。  
  Legacy compatibility entrypoint that forwards to `src/mini_agent/mcp/server.py`.

### Quick Run / 快速运行

在项目根目录并激活 `.venv` 后，推荐运行正式入口：  
From the project root with `.venv` activated, the recommended formal entrypoints are:

```bash
python src/mini_agent/main.py
python src/mini_agent/rag/build_index.py
python src/mini_agent/rag/search.py "Pro 订阅多少钱"
python src/mini_agent/mcp/server.py
```

说明：  
Notes:

- `src/mini_agent/main.py` 是当前默认主入口。  
  `src/mini_agent/main.py` is the current default main entrypoint.

- 当前默认入口会运行本地 tool calling + RAG 版本，不是通过 MCP 协议调用工具。  
  The current default entrypoint runs the local tool-calling + RAG version, not MCP-based tool calling.

- `src/mini_agent/mcp/server.py` 是独立的 MCP server 入口。  
  `src/mini_agent/mcp/server.py` is the standalone MCP server entrypoint.

如果你还想沿用旧命令，兼容入口仍可运行：  
If you still want to use the old commands, the compatibility entrypoints still work:

```bash
python examples/mini_chatbot/chatbot.py
python examples/mini_chatbot/chatbot_v2.py
python examples/mini_chatbot/main.py
python src/mini_agent/mcp_server.py
```

## RAG Summary / RAG 阶段摘要

当前 RAG 流程已经接入到 `src/mini_agent/main.py` 对应的主聊天流程中，并使用 `Qwen/Qwen3-Embedding-0.6B` 作为 embedding 模型。  
The current RAG flow has been integrated into the main chat flow behind `src/mini_agent/main.py`, using `Qwen/Qwen3-Embedding-0.6B` as the embedding model.

### Implemented Features / 已实现功能

- 已完成索引构建脚本。  
  An index-building script has been implemented.

- 已完成向量检索脚本。  
  A vector search script has been implemented.

- 当前主聊天流程已支持通过 `search_docs` tool 调用知识库检索。  
  The current main chat flow now supports knowledge-base retrieval through the `search_docs` tool.

- 当前 demo 知识库使用 8 条模拟 SaaS 文档。  
  The current demo knowledge base uses 8 mock SaaS documentation chunks.

### Relevant Paths / 相关路径

- [src/mini_agent/rag/build_index.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/rag/build_index.py)  
  构建 embedding 索引。  
  Builds the embedding index.

- [src/mini_agent/rag/search.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/rag/search.py)  
  执行向量检索。  
  Performs vector retrieval.

- [src/mini_agent/rag/data/doc_embeddings.npy](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/rag/data/doc_embeddings.npy)  
  已生成的 demo 向量索引文件。  
  Generated demo embedding index file.

- [src/mini_agent/rag/data/documents.json](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/rag/data/documents.json)  
  与索引对应的原始文档数据。  
  Original document data aligned with the index.

- [src/mini_agent/tools/docs_search.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/tools/docs_search.py)  
  当前 `search_docs` tool 的实现。  
  Current implementation of the `search_docs` tool.

- [src/mini_agent/chat/loop.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/chat/loop.py)  
  当前主聊天流程通过这里触发 `search_docs`。  
  The current main chat flow triggers `search_docs` from here.

### Current Limitations / 当前限制

- 知识库规模很小，只有 8 条模拟文档，覆盖范围有限。  
  The knowledge base is very small, with only 8 mock documents and limited coverage.

- 每次调用 `search_docs` 都会重新加载 embedding 模型，响应较慢。  
  Each `search_docs` call reloads the embedding model, so response time is slow.

- 当前没有设置相似度阈值，低相关问题也会强行返回 top-k 结果。  
  There is currently no similarity threshold, so low-relevance queries still return forced top-k results.

- `build_index.py` 虽然已经规范到 `rag/data/` 输出，但文档内容仍是硬编码的 demo 数据。  
  Although `build_index.py` now writes cleanly into `rag/data/`, its document content is still hard-coded demo data.

- 首次运行依赖下载较大模型文件，对网络稳定性要求较高。  
  First-time setup depends on downloading a large model file and requires a stable network.

### Planned Improvements / 预计修改方向

- 给检索结果增加相似度阈值，低分时明确返回“未找到足够相关内容”。  
  Add a similarity threshold so low-confidence retrieval can explicitly return “not enough relevant information found”.

- 把 embedding 模型改成常驻或缓存加载，避免每次检索都重新初始化。  
  Keep the embedding model warm or cached to avoid reinitializing it on every search.

- 把 `build_index.py` 和 `search.py` 进一步整理成更标准的模块化结构。  
  Refactor `build_index.py` and `search.py` into a cleaner, more modular structure.

- 后续用真实文档替换当前 mock 文档，提升覆盖范围和实际意义。  
  Replace the current mock documents with real documents later to improve coverage and usefulness.
