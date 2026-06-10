# mini-agent

一个用于循序渐进学习 Python、tool calling、RAG 和 agent 开发的练习项目。  
A learning project for gradually exploring Python, tool calling, RAG, and agent development.

## Chatbot Branch Summary / `chatbot` 分支摘要

`chatbot` 分支已经完成并合并到 `main`。这一阶段主要实现了一个最小可运行的 chatbot，以及一个带 tool calling 的 `chatbot_v2`。  
The `chatbot` branch has been completed and merged into `main`. This stage mainly adds a minimal runnable chatbot and a tool-calling `chatbot_v2`.

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

- [examples/mini_chatbot/chatbot.py](/Users/jiaenxu/Documents/mini-agent/examples/mini_chatbot/chatbot.py)  
  最小 chatbot 版本。  
  Minimal chatbot version.

- [examples/mini_chatbot/chatbot_v2.py](/Users/jiaenxu/Documents/mini-agent/examples/mini_chatbot/chatbot_v2.py)  
  带 tool calling 的 chatbot 版本。  
  Chatbot version with tool calling.

#### Reusable Tools / 可复用工具

- [src/mini_agent/tools/web.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/tools/web.py)  
  网页抓取与正文提取工具。  
  Web fetching and page-content extraction tool.

- [src/mini_agent/tools/__init__.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/tools/__init__.py)  
  工具导出入口。  
  Tool export entrypoint.

#### MCP Server / MCP 服务入口

- [src/mini_agent/mcp_server.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/mcp_server.py)  
  MCP server 入口，目前注册了 `get_page_content`。  
  MCP server entrypoint, currently registering `get_page_content`.

### Quick Run / 快速运行

在项目根目录并激活 `.venv` 后，可运行：  
From the project root with `.venv` activated, you can run:

```bash
python examples/mini_chatbot/chatbot.py
python examples/mini_chatbot/chatbot_v2.py
python src/mini_agent/mcp_server.py
```

说明：  
Notes:

- `chatbot.py` 是基础对话版本。  
  `chatbot.py` is the basic chat version.

- `chatbot_v2.py` 会在本地直接调用工具函数，不是通过 MCP 协议调用。  
  `chatbot_v2.py` calls tool functions locally, not through the MCP protocol.

- `mcp_server.py` 是独立的 MCP server 入口。  
  `mcp_server.py` is a standalone MCP server entrypoint.

## RAG Summary / RAG 阶段摘要

当前 RAG 流程已经接入到 `chatbot_v2`，并使用 `Qwen/Qwen3-Embedding-0.6B` 作为 embedding 模型。  
The current RAG flow has been integrated into `chatbot_v2`, using `Qwen/Qwen3-Embedding-0.6B` as the embedding model.

### Implemented Features / 已实现功能

- 已完成索引构建脚本。  
  An index-building script has been implemented.

- 已完成向量检索脚本。  
  A vector search script has been implemented.

- `chatbot_v2` 已支持通过 `search_docs` tool 调用知识库检索。  
  `chatbot_v2` now supports knowledge-base retrieval through the `search_docs` tool.

- 当前 demo 知识库使用 8 条模拟 SaaS 文档。  
  The current demo knowledge base uses 8 mock SaaS documentation chunks.

### Relevant Paths / 相关路径

- [src/mini_agent/rag/build_index.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/rag/build_index.py)  
  构建 embedding 索引。  
  Builds the embedding index.

- [src/mini_agent/rag/search.py](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/rag/search.py)  
  执行向量检索。  
  Performs vector retrieval.

- [src/mini_agent/rag/doc_embeddings.npy](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/rag/doc_embeddings.npy)  
  已生成的 demo 向量索引文件。  
  Generated demo embedding index file.

- [src/mini_agent/rag/documents.json](/Users/jiaenxu/Documents/mini-agent/src/mini_agent/rag/documents.json)  
  与索引对应的原始文档数据。  
  Original document data aligned with the index.

- [examples/mini_chatbot/chatbot_v2.py](/Users/jiaenxu/Documents/mini-agent/examples/mini_chatbot/chatbot_v2.py)  
  当前通过 `search_docs` 调用 RAG 检索。  
  Currently calls RAG retrieval through `search_docs`.

### Current Limitations / 当前限制

- 知识库规模很小，只有 8 条模拟文档，覆盖范围有限。  
  The knowledge base is very small, with only 8 mock documents and limited coverage.

- 每次调用 `search_docs` 都会重新加载 embedding 模型，响应较慢。  
  Each `search_docs` call reloads the embedding model, so response time is slow.

- 当前没有设置相似度阈值，低相关问题也会强行返回 top-k 结果。  
  There is currently no similarity threshold, so low-relevance queries still return forced top-k results.

- `build_index.py` 仍偏实验脚本风格，输出路径和执行方式还可以进一步规范化。  
  `build_index.py` is still closer to an experimental script, and its output path and execution flow can be standardized further.

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
