"""项目级配置与共享初始化逻辑。"""

from __future__ import annotations

import os

from dotenv import load_dotenv


load_dotenv()


def get_api_key() -> str:
    """读取 OpenAI API Key，并在缺失时给出明确报错。"""

    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise RuntimeError("请先设置环境变量 API_KEY")
    return api_key
