"""聊天模型客户端初始化。"""

from __future__ import annotations

from openai import OpenAI

from mini_agent.config import get_api_key


def build_openai_client() -> OpenAI:
    """创建一个可复用的 OpenAI client。"""

    return OpenAI(api_key=get_api_key())
