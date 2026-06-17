"""构建 demo RAG 索引。"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from modelscope import snapshot_download
from sentence_transformers import SentenceTransformer

from mini_agent.rag.chunking import split_text


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EMBEDDINGS_PATH = DATA_DIR / "chunk_embeddings.npy"
CHUNKS_PATH = DATA_DIR / "chunks.json"
MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"

# 切分参数：中文约 2~3 句一块。demo 语料偏短，主要为把 chunking 机制跑通，
# 真正调参留到有 evaluation set 之后。
CHUNK_MAX_CHARS = 200
CHUNK_OVERLAP = 40


# 模拟某 SaaS 产品的文档片段。每条带稳定的 `id`（doc_id），不依赖列表顺序。
DOCUMENTS = [
    {
        "id": "pro-subscription",
        "title": "Pro 订阅",
        "url": "https://docs.example.com/billing/pro",
        "text": "Pro 订阅分为月度和年度两种。月度 38 元，年度 388 元，年度比月度便宜约 15%。订阅可随时取消，取消后保留至当期结束。",
    },
    {
        "id": "free-limits",
        "title": "免费版限制",
        "url": "https://docs.example.com/billing/free-limits",
        "text": "免费版用户每月最多创建 3 个项目，单个项目大小不超过 100MB。需要更多额度需升级到 Pro 订阅。",
    },
    {
        "id": "data-export",
        "title": "数据导出",
        "url": "https://docs.example.com/data/export",
        "text": "在「设置 → 数据」页面可以一键导出全部账户数据，导出格式为 JSON 压缩包。导出请求会在 24 小时内通过邮件发送下载链接。",
    },
    {
        "id": "account-deletion",
        "title": "账户注销",
        "url": "https://docs.example.com/account/deletion",
        "text": "进入「设置 → 账户」点击「永久删除账户」即可注销。注销后账户数据保留 30 天，期间登录可恢复，30 天后彻底清除无法找回。",
    },
    {
        "id": "account-email",
        "title": "修改邮箱地址",
        "url": "https://docs.example.com/account/email",
        "text": "在「设置 → 账户 → 登录邮箱」处可更换邮箱，需要原邮箱和新邮箱各点击一次确认链接才能生效。",
    },
    {
        "id": "reset-password",
        "title": "重置密码",
        "url": "https://docs.example.com/account/reset-password",
        "text": "登录页点击「忘记密码」，输入注册邮箱即可收到重置链接。重置链接 30 分钟内有效，过期后需重新申请。",
    },
    {
        "id": "api-rate-limit",
        "title": "API 速率限制",
        "url": "https://docs.example.com/api/rate-limit",
        "text": "免费版每分钟最多 60 次 API 请求，Pro 用户每分钟 600 次。超过限制会返回 429 状态码，建议客户端做指数退避重试。",
    },
    {
        "id": "team-collaboration",
        "title": "团队协作",
        "url": "https://docs.example.com/team/collaboration",
        "text": "Pro 用户可以创建团队空间，邀请成员协同编辑。团队空间下的项目对所有成员可见，权限分为只读、可写、管理员三档。",
    },
    {
        # 故意写长，覆盖多个话题，让 chunking 真正切成多块（验证 Phase C 用）。
        "id": "account-management-guide",
        "title": "账户管理完整指南",
        "url": "https://docs.example.com/account/guide",
        "text": (
            "本指南覆盖账户的常见管理操作。首先是登录与安全：建议开启两步验证，"
            "在「设置 → 安全」绑定身份验证器 App，每次登录除密码外还需输入动态验证码。"
            "其次是会话管理：同一账户最多保持 5 个活跃登录会话，超出后最早的会话会被自动登出，"
            "你也可以在「设置 → 安全 → 登录设备」里手动注销任意设备。"
            "关于通知：系统通知分为产品更新、账单提醒和安全告警三类，"
            "其中安全告警无法关闭，产品更新和账单提醒可在「设置 → 通知」中按需开关。"
            "最后是账户协助：如果你忘记了绑定的两步验证设备，需要通过注册邮箱发起账户找回，"
            "客服会在 1~2 个工作日内人工核验身份后帮助你重置两步验证。"
        ),
    },
]


def build_chunk_records() -> list[dict]:
    """把每篇文档切成 chunk，展开成扁平的 chunk 记录列表。

    每条记录带稳定的 `chunk_id`（`{doc_id}::c{i}`）和 `doc_id`，便于后续
    incremental update / evaluation 对齐；`text` 是这个 chunk 的文本。
    """

    records: list[dict] = []
    for doc in DOCUMENTS:
        pieces = split_text(doc["text"], CHUNK_MAX_CHARS, CHUNK_OVERLAP)
        for i, piece in enumerate(pieces):
            records.append(
                {
                    "chunk_id": f"{doc['id']}::c{i}",
                    "doc_id": doc["id"],
                    "title": doc["title"],
                    "url": doc["url"],
                    "text": piece,
                }
            )
    return records


def build_index() -> None:
    """下载 embedding 模型并生成 demo chunk 索引。"""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 第一次会从 modelscope 下载约 1.1GB 模型权重，缓存到 ~/.cache/modelscope/
    # 之后 snapshot_download 会直接返回缓存路径，不再下载
    model_dir = snapshot_download(MODEL_NAME)
    model = SentenceTransformer(model_dir)

    # 检索单元是 chunk：先把文档切块，再对每个 chunk 的 text 编码
    chunks = build_chunk_records()
    texts = [chunk["text"] for chunk in chunks]
    chunk_embeddings = model.encode(texts)
    print(
        f"文档数：{len(DOCUMENTS)}, chunk 数：{len(chunks)}, "
        f"向量形状：{chunk_embeddings.shape}"
    )

    # 向量和 chunk 记录必须按相同下标一一对应
    np.save(EMBEDDINGS_PATH, chunk_embeddings)
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"索引已保存到 {EMBEDDINGS_PATH.name} 和 {CHUNKS_PATH.name}")


def main() -> None:
    """命令行入口。"""

    build_index()


if __name__ == "__main__":
    main()
