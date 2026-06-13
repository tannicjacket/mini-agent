# Example Pre-Execution Note — RAG Phase A

这是一份**真实的** pre-execution note 样例，对应 `mini-agent` 仓库 RAG Phase A 的开篇分析。它是 `learning-note` skill 想要复现的目标风格：

- 7 个 section 顺序固定；
- 每节都点出真实的文件、函数、类型；
- Section 3 把 scope 划得很尖（"contract cleanup, not quality improvement"）；
- Section 6 明列非目标，是 scope 的护城河；
- Section 7 每条都给出默认倾向 + 理由，而不是只抛问题。

每次为新 module / phase 写 note 时，**复用这个 shape，但不要照抄文字**。每个模块的现状、目标和 tradeoff 都不同。

---

## Calibration sample（原文）

### 1. Current Architecture

`src/mini_agent/` 下分四块：

- `chat/`：`loop.py` 是当前默认主流程（local tool-calling chat loop），`prompts.py` 集中放 system prompt，`client.py` 初始化 OpenAI client。
- `tools/`：`weather`、`web`、`docs_search` 三个工具，作为 function calling 的 callable。
- `rag/`：`build_index.py`（离线产出 `data/doc_embeddings.npy` + `data/documents.json`）和 `search.py`（在线查询）。
- `mcp/`、`agent/`、`main.py`：本期不涉及。

调用链：`main.py → agent/runner.py → chat/loop.run_tool_chat → TOOLS 表 → search_docs → rag.search.search_documents`。

### 2. Current Flow

1. `chat/loop.py` 把 `search_docs` 注册为 function tool，描述写在 TOOLS 表里。
2. 模型决定调用后，`loop.py` 通过 `TOOL_FUNCTIONS["search_docs"]` 同步执行 `search_docs(query)`。
3. `search_docs` 调用 `search_documents(query, top_k=3)`，后者每次都会：load 索引 → load embedding 模型 → encode query → 算 similarity → 排序取 top-k。
4. 返回值是 `list[dict]`：`{index, score, title, url, text}`，被 `json.dumps` 后塞回 messages 中当 `role=tool` 的 content。
5. 模型再发一轮，直接基于这段 JSON 文本作答。

**当前限制**（仅讲和 Phase A 有关的）：

- 模型看到的只是裸 JSON，**没有 evidence_id**：无法被引用、无法被校验。
- **没有 abstain 信号**：哪怕 top-1 相似度只有 0.05，模型仍会被迫围绕这段无关内容作答 → 易幻觉。
- **没有引用语法约束**：prompt 没要求模型 cite 来源，也没说"找不到就拒答"。
- 原始 similarity score 直接喂给模型，对模型是噪声，对未来校准不利。

### 3. Goal

在本仓库的语境里，"Retrieval Contract Cleanup" 是：**只重写 RAG 层和 chat 层之间的"接口形状 + 行为约定"**，不动检索质量、不动模型生命周期、不动存储。

具体说，是把现在这种"裸 JSON 列表 → 模型自由发挥"的隐式契约，换成一个**显式、可校验、带 abstain 的 envelope**：

- 检索结果有稳定的 `evidence_id`（`E1`、`E2`…），未来可以做 citation 校验。
- 有 `abstain` 字段，让模型知道"这次检索别用"。
- envelope 里自带 `model_instructions`，把"必须用 `[E#]` 引用 / abstain 时拒答"的规则直接随数据下发，不只靠 system prompt。

这是契约层的清理，**不是质量改进**。Phase A 之后检索召回不会变好——但模型会第一次"知道自己在做 RAG"。

### 4. Planned Changes

**4.1 新增一个小模块：`src/mini_agent/rag/contract.py`**

放典型的两个 `@dataclass`：

```
@dataclass(frozen=True)
class Evidence:
    evidence_id: str    # "E1", "E2", ...
    title: str
    url: str
    text: str

@dataclass(frozen=True)
class RetrievalResult:
    evidence: list[Evidence]
    abstain: bool
    abstain_reason: str | None
    model_instructions: str

    def to_tool_payload(self) -> str:  # 在工具边界做 JSON 序列化
        ...
```

理由：envelope 类型独立于 `search.py` 更清晰，未来 chat 层做 citation 校验时也能 `import Evidence` 复用。**不用 pydantic**，按用户指示用 dataclass。

**4.2 修改 `src/mini_agent/rag/search.py`**

- 保留现有 `search_documents(query, top_k) -> list[dict]`（CLI 还能跑）。
- 新增 `retrieve(query: str, top_k: int = 3) -> RetrievalResult`：
  - 复用现有 dense top-k。
  - 用一个**占位阈值**（写成模块常量，例如 `ABSTAIN_THRESHOLD = 0.3`，配中文注释明确说"占位值，Phase 后期会用 eval set 标定"）。
  - top-1 score 低于阈值 → `abstain=True`、`evidence=[]`、`abstain_reason="top-1 similarity below threshold"`。
  - 否则按顺序生成 `E1..En`，**不把 raw score 写进 evidence**（按 project.md 的长期方向）。
  - 嵌入固定的 `model_instructions` 文本（中文，规则：必须用 `[E#]` 引用、abstain 时禁止编造）。

**4.3 修改 `src/mini_agent/tools/docs_search.py`**

改成调用 `retrieve(query)` 并返回 `result.to_tool_payload()`（JSON 字符串），签名保持 `search_docs(query: str) -> str` 不变。这样 `chat/loop.py` 里 `TOOL_FUNCTIONS` 那张表完全不动。

**4.4 修改 `src/mini_agent/chat/prompts.py`**

在 `TOOL_CHAT_SYSTEM_PROMPT` 里补两条：

- 调 `search_docs` 后，回答中引用必须用 `[E1]`、`[E2]` 这种标记，且只能用 envelope 里出现过的 id。
- 如果 envelope 的 `abstain` 为 true，直接告诉用户"目前知识库没有足够相关内容"，**不要**根据弱证据硬答。

**4.5 abstain 行为**

- 触发条件：**仅看 top-1 similarity** 是否低于阈值。简单、可解释、易于后期替换。
- 触发后返回的 envelope 中 `evidence=[]`、`abstain=True`，但 `model_instructions` 依然带回（让模型读到"abstain 时拒答"的规则）。
- 阈值是占位值，注释中文标注"非校准结果，Phase 后期会用 eval set 重选"。

**4.6 `chat/loop.py` 要不要改？**

**建议本期不动 `loop.py`。**

理由：本期所有新增约束（citation 形态、abstain 时拒答）都是模型行为约束，靠 `prompts.py` + envelope 自带的 `model_instructions` 就够了。`loop.py` 现在做的事——执行 tool、把字符串塞回 messages——和新契约完全兼容（payload 仍是字符串）。真正需要 `loop.py` 改动的是 **"校验模型回复里 `[E#]` 是否合法"**——但那属于"contract enforcement"，是 Phase A 之后的事，不在本期范围。Phase A 先把契约**说清楚**，校验留给下一阶段。

### 5. Files Likely To Change

| 文件 | 改动 |
|---|---|
| `src/mini_agent/rag/contract.py` | **新增**，放 `Evidence` / `RetrievalResult` dataclass + `model_instructions` 文本 |
| `src/mini_agent/rag/search.py` | 新增 `retrieve(query)`，老 `search_documents` 保留 |
| `src/mini_agent/tools/docs_search.py` | 改成调用 `retrieve` 并序列化 envelope |
| `src/mini_agent/chat/prompts.py` | `TOOL_CHAT_SYSTEM_PROMPT` 加 citation + abstain 规则 |
| `.claude/progress/current.md` | Phase A 落地后再更新一两行（非本次） |

### 6. What Will Not Change

- `src/mini_agent/chat/loop.py`：本期不动。
- `src/mini_agent/rag/build_index.py`：本期不动；不引入 chunking、不改文档来源、不改两文件 artifact。
- embedding 模型生命周期（每次 `retrieve` 仍会重新加载）——这是 Phase B。
- 不引入 pydantic、不引入服务化 / Protocol、不引入数据库 / pgvector / sqlite-vss。
- 不引入 reranker、hybrid retrieval、async、observability。
- 不引入 evaluation harness。
- 不引入 confidence_band（保持 envelope 字段尽量少；以后真要再加）。
- 不动 `mcp/`、`agent/`、`examples/`、`mini_demo/`。
- 不写任何新的 plan / memory / notes 文件，不动 `~/.claude/`。

### 7. Questions or Tradeoffs To Confirm

1. **envelope 放新文件还是塞进 `search.py`？** 倾向新建 `rag/contract.py`，理由是契约的稳定性应该比检索实现更高，分文件能让"契约改动"和"检索改动"在 git 历史里分开。如果觉得 Phase A 还嫌重，可以临时放 `search.py` 顶部。
2. **占位阈值的具体数值？** Qwen3-Embedding-0.6B 在 `model.similarity` 下大约是 cosine 空间，倾向 `0.3` 作为占位（注释里写明非校准）。
3. **`model_instructions` 文本写中文还是中英双语？** 仓库其他注释是中文、prompt 也是中文，倾向纯中文，简短一段。
4. **`search.py` 的 CLI `main()` 要不要也切到 envelope 输出？** 倾向**不切**——CLI 是给开发者看相似度的，应保留 score 字段方便人肉调试。新契约只在工具边界生效，对人类调试入口透明。
5. **是否在本期就给 `model_instructions` 加"禁止编造 evidence_id"这一条？** 倾向加，成本几乎为零。
6. **`search_documents` 老函数要不要留？** 倾向留作过渡，CLI 和未来的 eval 都可能复用它；如果更激进可以直接换签名。
