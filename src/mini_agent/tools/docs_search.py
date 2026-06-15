"""文档检索工具。

Phase A 之后这个 tool 不再返回裸的 list[dict]，而是 RAG 层定义的
RetrievalResult envelope（含 evidence_id、abstain、model_instructions）
经 JSON 序列化后的字符串。函数签名保持不变，chat/loop.py 那张
TOOL_FUNCTIONS 表无需改动。
"""

from __future__ import annotations


def search_docs(query: str) -> str:
    """检索文档并返回 envelope 的 JSON 字符串。"""

    # 延迟 import：避免在主入口启动时就触发 numpy / sentence-transformers
    # 这条链路的加载成本。
    from mini_agent.rag.search import retrieve

    return retrieve(query, top_k=3).to_tool_payload()
