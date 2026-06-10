import os
from openai import OpenAI
from dotenv import load_dotenv
from openai.types.chat import ChatCompletionMessageParam

load_dotenv()

# 从环境变量读取，避免把 API Key 硬编码到代码里
API_KEY = os.environ.get("API_KEY")

if not API_KEY :
    raise RuntimeError("请先设置环境变量 API_KEY")

client = OpenAI(api_key=API_KEY)

# 试试修改这段文字，观察 AI 回答风格的变化
# SYSTEM_PROMPT = "你是一个海盗船长，所有回答都要用海盗的口吻，多用'嗷呜'、'宝藏'之类的词"

# 苏格拉底式教学
SYSTEM_PROMPT = "你是一个苏格拉底式的老师，喜欢通过提问引导学生思考，而不是直接给出答案。"

# 对话历史，所有消息都会追加到这个列表里
messages: list[ChatCompletionMessageParam] = [
    {"role": "system", "content": SYSTEM_PROMPT}
]
# messages = [{"role": "system", "content": SYSTEM_PROMPT}]

print(f"[人设] {SYSTEM_PROMPT}")
print("输入消息开始聊天，输入 q 退出\n")

while True:
    user_input = input("你: ")
    if user_input.strip() == "q":
        break

    # 把用户消息追加到对话历史
    messages.append({"role": "user", "content": user_input})

    # 把完整的对话历史发给模型
    # 上一篇 curl 里直接传的 thinking:disabled 是 DeepSeek 自家字段，
    # OpenAI SDK 没原生支持，统一通过 extra_body 透传到请求体顶层
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )

    # 取出模型的回答，也追加到对话历史
    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})

    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        print(f"{role}: {content}")

    print(f"AI: {reply}\n")