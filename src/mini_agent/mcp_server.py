"""兼容旧路径的 MCP server 入口。"""

from __future__ import annotations

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mini_agent.mcp.server import main


if __name__ == "__main__":
    main()
