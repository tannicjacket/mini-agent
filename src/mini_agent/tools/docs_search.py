"""文档检索工具。"""

from __future__ import annotations

import json


def search_docs(query: str) -> str:
    """调用 RAG 检索模块，并把结果转成 JSON 字符串返回。"""

    from mini_agent.rag.search import search_documents

    results = search_documents(query, top_k=3)
    return json.dumps(results, ensure_ascii=False)
