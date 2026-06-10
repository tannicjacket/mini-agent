"""Mini Agent 的 MCP server 入口。"""

from __future__ import annotations

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mini_agent.tools.web import get_page_content as fetch_page_content

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # pragma: no cover - 本地未安装 mcp 时给出明确报错
    FastMCP = None


if FastMCP is not None:
    mcp = FastMCP("Mini Agent MCP", json_response=True)

    @mcp.tool()
    def get_page_content(url: str) -> str:
        """抓取网页正文，过滤脚本和导航等无关内容。"""
        return fetch_page_content(url)


    if __name__ == "__main__":
        mcp.run(transport="stdio")
else:
    def main() -> None:
        raise RuntimeError("请先安装 mcp 包，例如：pip install 'mcp[cli]'")


    if __name__ == "__main__":
        main()
