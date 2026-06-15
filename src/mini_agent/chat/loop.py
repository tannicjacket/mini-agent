"""聊天循环与 tool-calling 主流程。"""

from __future__ import annotations

import json

from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCallParam,
    ChatCompletionToolParam,
)

from mini_agent.chat.client import build_openai_client
from mini_agent.chat.prompts import BASIC_SYSTEM_PROMPT, TOOL_CHAT_SYSTEM_PROMPT
from mini_agent.tools.docs_search import search_docs
from mini_agent.tools.weather import get_weather
from mini_agent.tools.web import get_page_content


MODEL_NAME = "gpt-4o-mini"

TOOLS: list[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的当前天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称",
                    }
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_page_content",
            "description": "抓取网页正文，返回清洗后的主要文本内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "要抓取的网页 URL",
                    }
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "检索产品知识库，返回与用户问题最相关的文档片段",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "用户的问题或检索语句",
                    }
                },
                "required": ["query"],
            },
        },
    },
]

TOOL_FUNCTIONS = {
    "get_weather": get_weather,
    "get_page_content": get_page_content,
    "search_docs": search_docs,
}


def run_basic_chat() -> None:
    """运行最小多轮聊天 demo。"""

    client = build_openai_client()
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": BASIC_SYSTEM_PROMPT}
    ]

    print(_format_persona_block(BASIC_SYSTEM_PROMPT))

    while True:
        user_input = input("你: ")
        if user_input.strip() == "q":
            break

        messages.append({"role": "user", "content": user_input})
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
        )

        reply = response.choices[0].message.content or ""
        messages.append({"role": "assistant", "content": reply})
        print(f"\nAI: {reply}\n")


def run_tool_chat() -> None:
    """运行带本地 tool-calling 与 RAG 的聊天 demo。"""

    client = build_openai_client()
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": TOOL_CHAT_SYSTEM_PROMPT}
    ]

    print(_format_persona_block(TOOL_CHAT_SYSTEM_PROMPT))

    while True:
        user_input = input("你: ")
        if user_input.strip() == "q":
            break

        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOLS,
        )
        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:
            messages.append(_build_assistant_history_message(assistant_message))

            for tool_call in assistant_message.tool_calls:
                if tool_call.type != "function":
                    continue

                args = json.loads(tool_call.function.arguments)
                func = TOOL_FUNCTIONS[tool_call.function.name]
                result = func(**args)
                print(_format_tool_call_block(tool_call.function.name, args, result))
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )

            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=TOOLS,
            )
            assistant_message = response.choices[0].message

        final_reply = assistant_message.content or ""
        messages.append({"role": "assistant", "content": final_reply})
        print(f"\nAI: {final_reply}\n")


# CLI 排版用的分隔线宽度
_BAR_WIDTH = 60


def _format_persona_block(prompt: str) -> str:
    """把人设 system prompt 包成带分隔线的独立块，避免和提示语糊在一起。"""

    bar = "─" * _BAR_WIDTH
    return (
        f"{bar}\n"
        f"[人设]\n"
        f"{prompt}\n"
        f"{bar}\n"
        "输入消息开始聊天，输入 q 退出"
    )


def _format_tool_call_block(name: str, args: dict, result: str) -> str:
    """把一次工具调用整理成多行、易读的 CLI 输出块。

    对 search_docs 的 envelope 做结构化展开（逐条证据分行，丢掉对人类无用的
    model_instructions）；其它工具的纯文本结果则原样打印、超长截断。
    """

    lines = ["", f"  [调用工具] {name}  参数 {args}"]

    envelope = _try_parse_envelope(result)
    if envelope is not None:
        if envelope.get("abstain"):
            reason = envelope.get("abstain_reason") or "无足够相关证据"
            lines.append(f"  检索未命中 (abstain=true)：{reason}")
        else:
            evidence = envelope.get("evidence", [])
            lines.append(f"  检索命中 {len(evidence)} 条证据 (abstain=false)：")
            for ev in evidence:
                lines.append(f"    [{ev['evidence_id']}] {ev['title']} — {ev['url']}")
                lines.append(f"         {ev['text']}")
    else:
        lines.append(f"  结果：{_truncate(str(result), 300)}")

    return "\n".join(lines)


def _try_parse_envelope(result: str) -> dict | None:
    """尝试把工具结果解析成 search_docs 的 envelope；不是就返回 None。"""

    try:
        data = json.loads(result)
    except (json.JSONDecodeError, TypeError):
        return None

    if isinstance(data, dict) and "evidence" in data and "abstain" in data:
        return data
    return None


def _truncate(text: str, limit: int) -> str:
    """超过 limit 个字符就截断并加省略提示，避免一条结果刷屏。"""

    if len(text) <= limit:
        return text
    return text[:limit] + " …（已截断）"


def _build_assistant_history_message(
    assistant_message,
) -> ChatCompletionAssistantMessageParam:
    """把 SDK 返回的 assistant tool_calls 转成可回传给下一轮 API 的消息。"""

    tool_calls_for_history: list[ChatCompletionMessageToolCallParam] = []
    for tool_call in assistant_message.tool_calls or []:
        if tool_call.type != "function":
            continue

        tool_calls_for_history.append(
            {
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                },
            }
        )

    assistant_msg_for_history: ChatCompletionAssistantMessageParam = {
        "role": "assistant",
        "tool_calls": tool_calls_for_history,
    }
    if assistant_message.content is not None:
        assistant_msg_for_history["content"] = assistant_message.content

    return assistant_msg_for_history
