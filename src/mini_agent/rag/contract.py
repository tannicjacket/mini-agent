"""RAG 层与 chat 层之间的 retrieval contract。

Phase A 的目标：把"裸 JSON 列表 → 模型自由发挥"的隐式 contract
换成显式、可校验、带 abstain 的 envelope。这个文件只放契约相关的
类型与给模型的固定规则文本；检索算法本身仍然在 search.py。
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass


# 给模型读的固定规则。和 chat/prompts.py 里的 system prompt 协同工作：
# system prompt 给出大方向，envelope 自带的这段是和具体检索结果绑定的
# "随数据下发"的硬约束。
MODEL_INSTRUCTIONS: str = (
    "本次结果来自 search_docs 工具，请遵守以下规则：\n"
    "1. 如果 abstain 为 true，说明这次检索没有足够相关的内容；"
    "直接告诉用户「目前知识库里没有足够相关的资料」，不要凭弱证据硬答。\n"
    "2. 否则，回答中引用证据必须使用 [E1]、[E2] 这种方括号格式，"
    "且只能引用 evidence 列表里实际出现过的 evidence_id；"
    "禁止编造没出现过的 id。\n"
    "3. 不要把 evidence_id 替换成 url，也不要把 url 单独贴在回答里。\n"
    "4. 如果证据只能回答用户问题的一部分，明确说明只能回答到哪里，"
    "不要扩展无证据的内容。"
)


@dataclass(frozen=True)
class Evidence:
    """一条检索证据。

    `evidence_id` 是这条证据在本次检索中的稳定短标识（"E1"、"E2"…），
    模型在回答里用 [E1] 这种方括号引用它。
    """

    evidence_id: str
    title: str
    url: str
    text: str


@dataclass(frozen=True)
class RetrievalResult:
    """一次检索返回的完整 envelope。

    `evidence`            - 命中的证据列表；abstain 为 True 时为空 list。
    `abstain`             - True 表示这次检索不可信，请模型拒答。
    `abstain_reason`      - abstain 为 True 时的简短原因；否则为 None。
    `model_instructions`  - 给模型读的固定规则文本（见 MODEL_INSTRUCTIONS）。
    """

    evidence: list[Evidence]
    abstain: bool
    abstain_reason: str | None
    model_instructions: str

    def to_tool_payload(self) -> str:
        """在 tool 边界把 envelope 序列化成 JSON 字符串。

        chat/loop.py 把 tool 调用结果当成 string 塞回 messages，
        所以我们在这里统一做 JSON 序列化，避免每个 caller 自己 dump。
        `ensure_ascii=False` 保留中文原文。
        """

        return json.dumps(asdict(self), ensure_ascii=False)
