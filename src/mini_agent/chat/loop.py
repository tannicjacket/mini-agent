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

    print(f"[人设] {BASIC_SYSTEM_PROMPT}")
    print("输入消息开始聊天，输入 q 退出\n")

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
        print(f"AI: {reply}\n")


def run_tool_chat() -> None:
    """运行带本地 tool-calling 与 RAG 的聊天 demo。"""

    client = build_openai_client()
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": TOOL_CHAT_SYSTEM_PROMPT}
    ]

    print(f"[人设] {TOOL_CHAT_SYSTEM_PROMPT}")
    print("输入消息开始聊天，输入 q 退出\n")

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
                print(f"  [调用工具] {tool_call.function.name}({args}) => {result}")
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
        print(f"AI: {final_reply}\n")


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
