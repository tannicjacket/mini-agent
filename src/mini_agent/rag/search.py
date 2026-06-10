import json
import sys
from pathlib import Path

import numpy as np
import numpy.typing as npt
from modelscope import snapshot_download
from sentence_transformers import SentenceTransformer


# 以当前文件所在目录作为基准，避免从不同目录运行脚本时找不到索引文件
BASE_DIR = Path(__file__).resolve().parent

# build_index.py 产出的两个文件路径
EMBEDDINGS_PATH = BASE_DIR / "doc_embeddings.npy"
DOCUMENTS_PATH = BASE_DIR / "documents.json"

# 检索时必须使用和建索引时相同的 embedding 模型，否则向量空间不一致
MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"


def load_index() -> tuple[npt.NDArray[np.float32], list[dict]]:
    """加载已经保存好的向量索引和原始文档。"""

    # 读取所有文档的向量矩阵，形状通常是 (文档数, 向量维度)
    # 这里显式转成 float32，方便后面和 similarity 的类型要求对齐
    doc_embeddings = np.load(EMBEDDINGS_PATH).astype(np.float32)

    # 读取与向量一一对应的原始文档内容和 metadata
    with open(DOCUMENTS_PATH, "r", encoding="utf-8") as f:
        documents = json.load(f)

    return doc_embeddings, documents


def load_embedding_model() -> SentenceTransformer:
    """加载 embedding 模型。第一次运行时可能会下载模型。"""

    # 从 ModelScope 获取模型目录；如果本地已有缓存，会直接复用缓存
    model_dir = snapshot_download(MODEL_NAME)

    # 用 SentenceTransformer 包装模型，后续可直接调用 encode 和 similarity
    return SentenceTransformer(model_dir)


def search_documents(query: str, top_k: int = 3) -> list[dict]:
    """对查询语句做向量检索，返回最相关的 top_k 文档。"""

    # 先加载已有索引数据
    doc_embeddings, documents = load_index()

    # 再加载和建索引时相同的 embedding 模型
    model = load_embedding_model()

    # 把用户问题编码成查询向量
    # 这里使用 prompt_name="query"，表示按查询语句的方式编码
    # 同时显式要求返回 numpy，并统一转成 float32，避免 similarity 的类型重载报错
    query_embedding = model.encode(
        [query],
        prompt_name="query",
        convert_to_numpy=True,
    ).astype(np.float32)

    # 计算查询向量与每条文档向量的相似度
    # 返回结果是一个二维结构，这里取第 0 个查询对应的一行
    similarities = model.similarity(query_embedding, doc_embeddings).numpy()[0]



    # 按相似度从高到低排序，取最相关的 top_k 个文档下标
    top_indices = np.argsort(-similarities)[:top_k]

    results = []
    for idx in top_indices:
        # 把结果整理成结构化数据，方便命令行打印，也方便以后被 chatbot/agent 直接调用
        results.append(
            {
                "index": int(idx),
                "score": float(similarities[idx]),
                "title": documents[idx]["title"],
                "url": documents[idx]["url"],
                "text": documents[idx]["text"],
            }
        )

    return results


def main() -> None:
    """命令行入口：读取查询词，执行检索并打印结果。"""

    # 命令行至少需要一个查询参数
    if len(sys.argv) < 2:
        print("用法：python search.py <查询语句>")
        sys.exit(1)

    query = sys.argv[1]
    results = search_documents(query)

    print(f"\n查询：{query}")
    for rank, item in enumerate(results, 1):
        print(f"  Top {rank} 相似度 {item['score']:.3f} 下标 {item['index']}")
        print(f"    标题：{item['title']}")
        print(f"    链接：{item['url']}")
        print(f"    片段：{item['text']}")


if __name__ == "__main__":
    main()
