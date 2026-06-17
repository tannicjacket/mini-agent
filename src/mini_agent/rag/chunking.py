"""把一篇文档的长文本切成若干 chunk（检索的最小单元）。

切分只在建索引时发生（query 不切），所以这里只放纯函数，方便单测。
策略：先按句末标点断句，再贪心地把句子塞进不超过 max_chars 的块；
相邻块之间抄一点尾巴做 overlap，避免跨边界的句子两边都答不全。
"""

from __future__ import annotations

import re


# 句末标点：中文。！？ 加换行。lookbehind `(?<=...)` 表示"在标点之后切"，
# 这样标点会留在前一句末尾，而不是被切掉。
_SENTENCE_END = re.compile(r"(?<=[。！？\n])")


def _split_sentences(text: str) -> list[str]:
    """按句末标点把整段文本断成句子，丢掉纯空白的碎片。"""

    return [part for part in _SENTENCE_END.split(text) if part.strip()]


def split_text(text: str, max_chars: int = 200, overlap: int = 40) -> list[str]:
    """把 text 切成若干 chunk。

    `max_chars` - 单个 chunk 的目标字数上限（按句子边界收口，可能略超）。
    `overlap`   - 收口时把上一个 chunk 末尾多少个字抄进下一个 chunk 开头。

    返回 chunk 字符串列表；空文本返回空列表。单句若本身超过 max_chars，
    会原样成块（不在句子中间硬切），demo 语料不会触发。
    """

    text = text.strip()
    if not text:
        return []

    chunks: list[str] = []
    cur = ""

    for sentence in _split_sentences(text):
        # 当前块已经装了东西、再加这句就超限 → 先把当前块收口，
        # 再用它的末尾 overlap 个字做新块的开头。
        if cur and len(cur) + len(sentence) > max_chars:
            chunks.append(cur)
            cur = cur[-overlap:] if overlap else ""
        cur += sentence

    if cur:
        chunks.append(cur)

    return chunks
