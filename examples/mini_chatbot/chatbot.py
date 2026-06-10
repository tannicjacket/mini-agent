"""兼容旧路径的基础 chatbot 入口。"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mini_agent.chat.loop import run_basic_chat


if __name__ == "__main__":
    run_basic_chat()
