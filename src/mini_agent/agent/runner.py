"""当前 mini agent 的运行入口。"""

from __future__ import annotations

from mini_agent.chat.loop import run_tool_chat


def main() -> None:
    """运行当前默认的 mini agent 聊天入口。"""

    run_tool_chat()
