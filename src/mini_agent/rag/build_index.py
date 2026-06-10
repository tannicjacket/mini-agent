# build_index.py
import json
import numpy as np
from modelscope import snapshot_download
from sentence_transformers import SentenceTransformer

# 第一次会从 modelscope 下载约 1.1GB 模型权重，缓存到 ~/.cache/modelscope/
# 之后 snapshot_download 会直接返回缓存路径，不再下载
model_dir = snapshot_download("Qwen/Qwen3-Embedding-0.6B")
model = SentenceTransformer(model_dir)


# 模拟某 SaaS 产品的文档片段
documents = [
    {
        "title": "Pro 订阅",
        "url": "https://docs.example.com/billing/pro",
        "text": "Pro 订阅分为月度和年度两种。月度 38 元，年度 388 元，年度比月度便宜约 15%。订阅可随时取消，取消后保留至当期结束。",
    },
    {
        "title": "免费版限制",
        "url": "https://docs.example.com/billing/free-limits",
        "text": "免费版用户每月最多创建 3 个项目，单个项目大小不超过 100MB。需要更多额度需升级到 Pro 订阅。",
    },
    {
        "title": "数据导出",
        "url": "https://docs.example.com/data/export",
        "text": "在「设置 → 数据」页面可以一键导出全部账户数据，导出格式为 JSON 压缩包。导出请求会在 24 小时内通过邮件发送下载链接。",
    },
    {
        "title": "账户注销",
        "url": "https://docs.example.com/account/deletion",
        "text": "进入「设置 → 账户」点击「永久删除账户」即可注销。注销后账户数据保留 30 天，期间登录可恢复，30 天后彻底清除无法找回。",
    },
    {
        "title": "修改邮箱地址",
        "url": "https://docs.example.com/account/email",
        "text": "在「设置 → 账户 → 登录邮箱」处可更换邮箱，需要原邮箱和新邮箱各点击一次确认链接才能生效。",
    },
    {
        "title": "重置密码",
        "url": "https://docs.example.com/account/reset-password",
        "text": "登录页点击「忘记密码」，输入注册邮箱即可收到重置链接。重置链接 30 分钟内有效，过期后需重新申请。",
    },
    {
        "title": "API 速率限制",
        "url": "https://docs.example.com/api/rate-limit",
        "text": "免费版每分钟最多 60 次 API 请求，Pro 用户每分钟 600 次。超过限制会返回 429 状态码，建议客户端做指数退避重试。",
    },
    {
        "title": "团队协作",
        "url": "https://docs.example.com/team/collaboration",
        "text": "Pro 用户可以创建团队空间，邀请成员协同编辑。团队空间下的项目对所有成员可见，权限分为只读、可写、管理员三档。",
    },
]


# 只对每条文档的 text 字段编码，metadata 不参与向量计算
texts = [doc["text"] for doc in documents]
# encode 默认返回 numpy 数组，可以直接传给 np.save
doc_embeddings = model.encode(texts)
print(f"文档数：{len(documents)}, 向量形状：{doc_embeddings.shape}")

# 把向量和带 metadata 的原始文档一起保存
# 注意：doc_embeddings 第 i 行向量必须对应 documents 第 i 个 dict，下标要严格一一对应
np.save("doc_embeddings.npy", doc_embeddings)
with open("documents.json", "w", encoding="utf-8") as f:
    json.dump(documents, f, ensure_ascii=False, indent=2)
print("索引已保存到 doc_embeddings.npy 和 documents.json")