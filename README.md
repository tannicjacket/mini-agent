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
