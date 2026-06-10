import json
import os
import sys
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCallParam,
    ChatCompletionToolParam,
)

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mini_agent.tools.web import get_page_content


load_dotenv()

API_KEY = os.environ.get("API_KEY")
if not API_KEY :
    raise RuntimeError("请先设置环境变量 API_KEY")

client = OpenAI(api_key=API_KEY)

# 用 JSON 格式描述模型可以使用的工具
tools: list[ChatCompletionToolParam] = [
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
                        "description": "用户的问题或检索语句"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# 工具的真正实现（实际项目中这里会调用天气 API）
def get_weather(city):
    weather_data = {
        "北京": {"temperature": 8, "condition": "多云"},
        "上海": {"temperature": 15, "condition": "晴"},
        "广州": {"temperature": 22, "condition": "阵雨"},
    }
    data = weather_data.get(city, {"temperature": "未知", "condition": "未知"})
    # json.dumps 把字典转成 JSON 字符串，ensure_ascii=False 让中文正常显示
    return json.dumps(data, ensure_ascii=False)

def search_docs(query: str) -> str:

    from mini_agent.rag.search import search_documents

    results = search_documents(query, top_k=3)
    return json.dumps(results, ensure_ascii=False)

# 工具名到函数的映射
tool_functions = {
    "get_weather": get_weather,
    "get_page_content": get_page_content,
    "search_docs": search_docs,
}

SYSTEM_PROMPT = "你是一个友好的助手，可以查询天气、抓取网页内容，也可以检索产品知识库。当用户问到订阅、价格、限制、导出、账号、API 规则等文档问题时，优先使用 search_docs 工具。"

messages: list[ChatCompletionMessageParam] = [
    {"role": "system", "content": SYSTEM_PROMPT}]

print(f"[人设] {SYSTEM_PROMPT}")
print("输入消息开始聊天，输入 q 退出\n")

while True:
    user_input = input("你: ")
    if user_input.strip() == "q":
        break

    messages.append({"role": "user", "content": user_input})

    # 把工具列表传给 API，模型会自己判断是否需要调用
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,

    )
    assistant_message = response.choices[0].message

    # 如果模型决定调用工具
    if assistant_message.tool_calls:
        tool_calls_for_history: list[ChatCompletionMessageToolCallParam] = []
        for tool_call in assistant_message.tool_calls:
            
            # 不给这行 pylance 会报错
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

        messages.append(assistant_msg_for_history)
        for tool_call in assistant_message.tool_calls:

            if tool_call.type != "function":
                continue

            # arguments 是 JSON 字符串，需要解析成字典
            args = json.loads(tool_call.function.arguments)
            # **args 把字典解包成关键字参数，等价于 func(city="北京")
            func = tool_functions[tool_call.function.name]
            result = func(**args)
            print(f"  [调用工具] {tool_call.function.name}({args}) => {result}")
            # role 为 "tool" 表示这是工具返回的结果
            # tool_call_id 用来关联这条结果对应哪个工具调用
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })
        # 拿到工具结果后再调一次模型，让它生成自然语言回答
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
        )
        assistant_message = response.choices[0].message

    final_reply = assistant_message.content or ""
    messages.append({"role": "assistant", "content": final_reply})
    print(f"AI: {final_reply}\n")
