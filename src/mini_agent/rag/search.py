import functools
import json
import sys
from pathlib import Path

import numpy as np
import numpy.typing as npt
from modelscope import snapshot_download
from sentence_transformers import SentenceTransformer

from mini_agent.rag.contract import (
    MODEL_INSTRUCTIONS,
    Evidence,
    RetrievalResult,
)


# 以当前文件所在目录作为基准，避免从不同目录运行脚本时找不到索引文件
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# build_index.py 产出的两个文件路径（检索单元是 chunk）
EMBEDDINGS_PATH = DATA_DIR / "chunk_embeddings.npy"
CHUNKS_PATH = DATA_DIR / "chunks.json"

# 检索时必须使用和建索引时相同的 embedding 模型，否则向量空间不一致
MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"

# top-1 相似度低于这个阈值时触发 abstain。**占位值**，未经 eval set
# 校准；Phase 后期会用标注数据重新选。当前 0.4 来自一次性手测：
# demo 知识库内合理 query 的 top-1 落在约 0.58 ~ 0.83，跨主题
# (GraphQL/天气) 落在 0.18 ~ 0.38，0.4 能挡住明显跨题的同时不误伤。
ABSTAIN_THRESHOLD = 0.4


def load_index() -> tuple[npt.NDArray[np.float32], list[dict]]:
    """加载已经保存好的 chunk 向量索引和 chunk 记录。"""

    if not EMBEDDINGS_PATH.exists() or not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            "索引文件不存在，请先运行 `python -m mini_agent.rag.build_index` 生成数据。"
        )

    # 读取所有 chunk 的向量矩阵，形状是 (chunk 数, 向量维度)
    # 这里显式转成 float32，方便后面和 similarity 的类型要求对齐
    chunk_embeddings = np.load(EMBEDDINGS_PATH).astype(np.float32)

    # 读取与向量一一对应的 chunk 记录（含 chunk_id / doc_id / title / url / text）
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    return chunk_embeddings, chunks


def load_embedding_model() -> SentenceTransformer:
    """加载 embedding 模型。第一次运行时可能会下载模型。"""

    # 从 ModelScope 获取模型目录；如果本地已有缓存，会直接复用缓存
    model_dir = snapshot_download(MODEL_NAME)

    # 用 SentenceTransformer 包装模型，后续可直接调用 encode 和 similarity
    return SentenceTransformer(model_dir)


# Phase B：进程级单例。@functools.cache 把无参函数的返回值缓存在进程内存，
# 第一次调用真的执行 load_*（模型加载几秒、索引读盘几十 ms），之后直接返回
# 同一个对象，免去 chat loop 里每次 retrieve 重新加载的开销。
# 缓存的都是纯内存资源（torch/numpy 张量、tokenizer），进程退出时 OS 整块回收，
# 不需要 atexit cleanup。本仓库 chat loop 单线程，不涉及 thread safety。
@functools.cache
def get_embedding_model() -> SentenceTransformer:
    """返回进程内共享的 embedding 模型（首次调用时才真正加载）。"""

    return load_embedding_model()


@functools.cache
def get_index() -> tuple[npt.NDArray[np.float32], list[dict]]:
    """返回进程内共享的向量索引和文档（首次调用时才真正读盘）。"""

    return load_index()


def search_documents(query: str, top_k: int = 3) -> list[dict]:
    """对查询语句做向量检索，返回最相关的 top_k 个 chunk。"""

    # 先加载已有索引数据（命中进程级缓存后近乎零成本）
    chunk_embeddings, chunks = get_index()

    # 再加载和建索引时相同的 embedding 模型（同样走进程级缓存）
    model = get_embedding_model()

    # 把用户问题编码成查询向量
    # 这里使用 prompt_name="query"，表示按查询语句的方式编码
    # 同时显式要求返回 numpy，并统一转成 float32，避免 similarity 的类型重载报错
    query_embedding = model.encode(
        [query],
        prompt_name="query",
        convert_to_numpy=True,
    ).astype(np.float32)

    # 计算查询向量与每个 chunk 向量的相似度
    # 返回结果是一个二维结构，这里取第 0 个查询对应的一行
    similarities = model.similarity(query_embedding, chunk_embeddings).numpy()[0]

    # 按相似度从高到低排序，取最相关的 top_k 个 chunk 下标
    top_indices = np.argsort(-similarities)[:top_k]

    results = []
    for idx in top_indices:
        # 把结果整理成结构化数据，方便命令行打印，也方便以后被 chatbot/agent 直接调用
        chunk = chunks[idx]
        results.append(
            {
                "index": int(idx),
                "score": float(similarities[idx]),
                "chunk_id": chunk["chunk_id"],
                "doc_id": chunk["doc_id"],
                "title": chunk["title"],
                "url": chunk["url"],
                "text": chunk["text"],
            }
        )

    return results


def retrieve(query: str, top_k: int = 3) -> RetrievalResult:
    """Phase A 的新检索入口：返回带 abstain 信号的 envelope。

    实现思路：复用现有 search_documents 拿 raw top-k，再按 top-1
    similarity 是否过低决定 abstain。envelope 里**不**带 raw score —
    project.md 长期方向明确不把相似度暴露给模型。
    """

    raw = search_documents(query, top_k=top_k)

    # 没有任何结果（理论上索引非空时不会出现）或 top-1 相似度过低
    # 都走 abstain 分支。一并写明 reason，方便排查。
    if not raw or raw[0]["score"] < ABSTAIN_THRESHOLD:
        return RetrievalResult(
            evidence=[],
            abstain=True,
            abstain_reason="top-1 similarity below threshold",
            model_instructions=MODEL_INSTRUCTIONS,
        )

    # 按命中顺序生成稳定的 evidence_id："E1"、"E2"、"E3"…
    # 模型在回答里就靠这个 id 做 [E1] 这种引用。
    evidence_list = [
        Evidence(
            evidence_id=f"E{rank}",
            title=item["title"],
            url=item["url"],
            text=item["text"],
        )
        for rank, item in enumerate(raw, start=1)
    ]

    return RetrievalResult(
        evidence=evidence_list,
        abstain=False,
        abstain_reason=None,
        model_instructions=MODEL_INSTRUCTIONS,
    )


def main() -> None:
    """命令行入口：读取查询词，执行检索并打印结果。"""

    # 命令行至少需要一个查询参数
    if len(sys.argv) < 2:
        print("用法：python -m mini_agent.rag.search <查询语句>")
        sys.exit(1)

    query = sys.argv[1]
    results = search_documents(query)

    print(f"\n查询：{query}")
    for rank, item in enumerate(results, 1):
        print(f"  Top {rank} 相似度 {item['score']:.3f} chunk {item['chunk_id']}")
        print(f"    标题：{item['title']}")
        print(f"    链接：{item['url']}")
        print(f"    片段：{item['text']}")


if __name__ == "__main__":
    main()
