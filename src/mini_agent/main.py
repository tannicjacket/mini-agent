"""项目默认运行入口。"""

from __future__ import annotations

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mini_agent.agent.runner import main as run_agent


def main() -> None:
    """运行当前默认的 mini agent。"""

    run_agent()


if __name__ == "__main__":
    main()
