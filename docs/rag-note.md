# RAG Learning Note

本文件是 `mini-agent` 仓库 RAG 学习线的**个人 study/worklog**，由 `.claude/skills/learning-note` skill 维护。

- 每条 entry 对应一个 module / phase 在动手之前的 pre-execution 分析。
- 新条目放在文件**最上方**，旧条目向下沉。
- 这里**不是** harness memory，不进入 `CLAUDE.md` / `.claude/project.md` / `.claude/progress/*`。
- 默认阅读对象是**不熟悉 Python 的我自己**，所以新的语法、术语、概念第一次出现都会解释。

---

## 2026-06-12 — RAG Phase A: Retrieval Contract Cleanup

### 0. 概念预热（不熟悉这一段的话，下面几节会很难懂）

#### 0.1 什么是 "contract"（契约）

写代码的时候，两段代码要"对话"——一段代码产出一份数据，另一段代码消费它。**它们之间约好的"数据长什么样、字段叫什么、出现什么情况时各自怎么处理"，就叫 contract。**

举例：现在 `search_docs` 工具产出 `[{title, url, text, score}, ...]`，聊天循环 `chat/loop.py` 拿到这堆字典再交给模型——这个"产出这种结构、对方按这种结构理解"的默契就是当前的 contract。

contract **不一定是写在文档里的**，也可以是隐式的（"大家都这么用"）。Phase A 要做的就是**把现在这个隐式 contract 变成显式 contract**：用一个明确的类型 + 一组明确的规则。

#### 0.2 什么是 "envelope"（信封 / 外壳）

想象寄信：你不是把白纸直接扔到邮筒里，而是把信纸装进信封，信封外面写收件人、贴邮票、贴"易碎"标签。收件人**先看信封的标签，再决定怎么处理里面的信纸**。

在 Phase A 里我们要做一个类似的"信封"：

```
# 伪代码（不是真 Python）
RetrievalResult 信封:
  evidence            = [ E1, E2, E3 ]    # 信纸 - 真正的检索证据
  abstain             = False              # 标签1 - 这次检索可信吗？
  abstain_reason      = None               # 标签2 - 如果不可信，原因
  model_instructions  = "请用 [E1] 这种形式引用证据"  # 标签3 - 怎么用
```

模型先看 `abstain` 这种"信封标签"，再决定要不要相信 `evidence` 里面的内容。**裸列表没有标签，信封有。**

#### 0.3 什么是 `evidence_id`，要详细解释

**是什么。** `evidence_id` 是一个**短字符串标签**，挂在每一条检索证据上。本期约定生成成 `"E1"`、`"E2"`、`"E3"` 这种格式，就是字母 E 加一个序号。

**在哪里出现。**

```
# 伪代码
Evidence 一条证据:
  evidence_id = "E1"                       # ← 就是这里
  title       = "Pro 订阅"
  url         = "https://docs.example.com/billing/pro"
  text        = "Pro 订阅分为月度和年度..."
```

每次检索拿到 top-k（比如 3 条）证据，按顺序贴上 `E1`、`E2`、`E3`，**整个 envelope 一起送进模型上下文**。

**模型怎么用。** system prompt 里写一条规则："你的回答里凡是用到检索结果，必须用 `[E1]`、`[E2]` 这种方括号引用，并且只能引用 envelope 里出现过的 id"。然后模型回答会变成这样：

```
Pro 订阅有月度 38 元和年度 388 元两档 [E1]。
免费版每月最多创建 3 个项目 [E2]。
```

**为什么要用。** 四个原因：

1. **引用可校验。** 以后聊天循环可以扫一遍模型的回复，看看 `[E1]` 是不是真的对应到了 envelope 里某条 evidence。如果模型瞎编了 `[E7]` 但 envelope 里根本没有，可以直接报错。
2. **强迫模型 grounding（贴着证据回答）。** 模型如果回答里没有任何 `[E#]`，说明它没在用检索结果，而是凭直觉编。这种"有没有引用"本身就是质量信号。
3. **方便事后审计。** 看聊天记录的时候，能马上知道"这句话是依据哪条证据说的"。
4. **避免模型自己编 URL。** 现在的实现把 url 直接喂给模型，模型可能用 url 当引用——但 url 长、容易写错、对模型也是负担。短 id 既稳定又便宜。

**注意，本期只是"约定 + 让模型引用"，不做"检查模型有没有真的引用对"**——那个校验逻辑留给下一阶段。

#### 0.4 什么是 "abstain"（拒答）

**abstain** 是一个英文动词，含义偏向"弃权 / 不表态"。在 RAG 里指：**检索阶段发现这次找到的东西都不靠谱，主动告诉模型"这次别用"**。

举例：用户问"如何用 GraphQL 订阅事件"，但知识库里只有"账户注销""修改邮箱"这些无关文档。dense 检索仍然会算出"最相似的"3 条返回，但相似度可能只有 0.05——本质上是垃圾。

如果不管这一切硬塞给模型，模型会被迫**围绕垃圾发挥**，最后说出"根据资料，GraphQL 订阅是在账户设置页面修改的"这种幻觉。

abstain 的作用就是：检索阶段发现 top-1 相似度低于某个**阈值**（threshold，就是一个数字界限），把 envelope 标记成 `abstain=True`，evidence 列表清空，并在 `abstain_reason` 里写明原因。模型读到这个标签就**主动拒答**："抱歉，知识库里没有足够相关的内容"。

#### 0.5 什么是 "citation"（引用）

跟学术论文里的 "[1] Smith et al."、"[2] Jones 2020" 是一回事——**回答里某句话挂一个标签，标签指向它的出处**。Phase A 里这个标签就是 `[E1]`、`[E2]`，出处就是 envelope 里对应的 Evidence 对象。

#### 0.6 这次会反复用到的 Python 语法

**(a) type annotation（类型注解）**

Python 是一种**默认不检查类型**的语言。下面两种写法运行起来效果完全一样：

```python
def search_docs(query):              # 写法 A：没注解
    ...

def search_docs(query: str) -> str:  # 写法 B：有注解
    ...
```

写法 B 里：

- `query: str` 表示"`query` 这个参数我打算传字符串进来"；
- `-> str` 表示"我打算返回字符串"。

但是——**Python 不会因为你违反这个注解而报错**！你完全可以 `search_docs(123)` 传一个整数进去，运行时不会拦你。type annotation **只是给读者（人 + 编辑器 + linter + Claude）看的提示**。

这就是 **type annotation ≠ 数据验证** 的核心：

- **type annotation** = 注释（hint），运行时不强制；
- **数据验证（data validation）** = 运行时真的会去检查"这个值真的是字符串吗，符合规则吗"，不符合就主动报错。

**(b) `@dataclass` 装饰器**

装饰器（decorator）是 Python 的一种语法糖，写法是 `@xxx` 加在类或函数上方。`@dataclass` 是 Python 标准库给的，专门用来"快速定义一个只装数据的类"。

```python
# 伪代码角度，dataclass 替你自动写了 __init__ 等方法
@dataclass
class Evidence:
    evidence_id: str
    title: str
    url: str
    text: str

# 等价于（手写时要写很多样板代码）：
class Evidence:
    def __init__(self, evidence_id: str, title: str, url: str, text: str):
        self.evidence_id = evidence_id
        self.title = title
        self.url = url
        self.text = text
    # 还要补 __repr__、__eq__ ...
```

**`@dataclass` 帮你省样板代码**，不做数据验证（注意——和 type annotation 一样，传错类型也不会报错）。

**(c) `frozen=True`**

```python
@dataclass(frozen=True)
class Evidence:
    ...
```

`frozen=True` 让这个类的实例**变成不可修改的**——创建后再去改字段会报错。
适合存证据这种"创建后就应该是只读"的对象，防止下游代码不小心改了它。

**(d) `str | None`（可选类型）**

```python
abstain_reason: str | None
```

读作"字符串或者 None"——这个字段可以是字符串、也可以是 None（空值）。在 abstain 触发时填字符串解释原因，没触发时填 None。

**(e) pydantic vs dataclass**

`pydantic` 是另一个第三方库，写法跟 dataclass 很像，但**会做真正的数据验证**——传错类型直接报错。本期不引入 pydantic，理由是：

- 检索 → 工具边界 → 模型上下文，这条路径**完全内部可控**，没有从外部 API/用户输入注入数据的场景；
- 数据验证有运行成本（pydantic 每次创建对象都跑校验）；
- 学习项目优先用标准库的东西，把"第三方依赖"留到真的必要时再加。

### 1. Current Architecture（项目当前结构）

`src/mini_agent/` 下分四块：

- `chat/`：`loop.py` 是当前默认主流程（一个"本地 tool calling"风格的聊天循环），`prompts.py` 集中放 system prompt（系统提示词，给模型设定角色 / 规则的文本），`client.py` 初始化 OpenAI client。
- `tools/`：当前三个工具 `weather`、`web`、`docs_search`。它们都是普通 Python 函数，但通过"function calling"机制注册给模型，让模型自己决定什么时候调。
- `rag/`：`build_index.py`（离线脚本，把文档变成向量存到磁盘）和 `search.py`（在线查询，给定一个问题返回最相似的文档）。
- `mcp/`、`agent/`、`main.py`：本期不涉及，先无视。

调用关系（运行时一条线）：

```
main.py
  → agent/runner.py            （挑选默认 runner）
  → chat/loop.run_tool_chat    （进入聊天主循环）
  → TOOLS 表里的 search_docs   （模型决定调用时触发）
  → rag/search.search_documents（真正去算相似度）
```

### 2. Current Flow（当前 RAG 端到端怎么走）

**用伪代码看一眼**，去掉真实 Python 的细节：

```
循环：
  user_input = 用户输入
  把 user_input append 到 messages 里
  response = 调 OpenAI API(messages, tools=TOOLS)

  if response 里模型决定调 search_docs:
      result_str = search_docs(query)                  # 当前返回纯 JSON 字符串
      把 result_str append 到 messages，role="tool"
      response = 再调一次 OpenAI API(messages, tools=TOOLS)

  打印 response.content
```

`search_docs` 里面发生了什么：

```
search_docs(query):
    1. 加载 doc_embeddings.npy （已经存在磁盘的向量矩阵）
    2. 加载 documents.json    （和向量一一对应的原始文档）
    3. 加载 embedding 模型     （Qwen3-Embedding-0.6B，每次都重新 load，这是 Phase B 才修的事）
    4. 把 query 编码成查询向量
    5. 用 cosine similarity 算 query 跟所有文档的相似度
    6. 排序，取前 3 个
    7. 把这 3 个组成 [{index, score, title, url, text}, ...]
    8. json.dumps 把它转成字符串
    9. return 这个字符串
```

> **新名词科普**：
> - **embedding**：把一段文本压缩成一串数字（一个向量），让"意思接近的文本"在数学上距离也近。本项目用的是 Qwen3-Embedding-0.6B 这个开源模型。
> - **similarity（相似度）**：两个向量"有多近"的一个分数，通常在 0~1 之间。0 不像，1 一模一样。
> - **top-k**：取相似度最高的前 k 条结果，k 这里固定为 3。

**Phase A 关心的当前问题**：

- 模型看到的只是裸 JSON 字符串，**没有 evidence_id**：没法引用，也没法事后校验。
- **没有 abstain 信号**：哪怕 top-1 相似度只有 0.05（基本不相关），模型仍会被迫围绕这些垃圾结果作答 → 幻觉。
- **没有引用语法约束**：现在的 system prompt 没要求模型"引用来源"，也没说"找不到时拒答"。
- 原始相似度分数（`score`）直接喂给模型，对模型是噪声——它对这些数字没感觉。

### 3. Goal（这一步具体要做什么）

**核心一句话**：把 RAG 层和 chat 层之间这条"裸 JSON 列表 → 模型自由发挥"的**隐式 contract**，换成一个**显式、可校验、带 abstain 的 envelope**。

对比一下 contract 改变前后的**形状**（伪代码）：

```
# 改之前（目前）
search_docs(query)  →  "[{score: 0.5, title: ..., url: ..., text: ...}, ...]"
                       裸 JSON，没有 evidence_id，没有 abstain，没有给模型的规则

# 改之后（Phase A 目标）
search_docs(query)  →  {
    "evidence": [
        { "evidence_id": "E1", "title": ..., "url": ..., "text": ... },
        { "evidence_id": "E2", "title": ..., "url": ..., "text": ... }
    ],
    "abstain": false,
    "abstain_reason": null,
    "model_instructions": "请只用 [E1]、[E2] 这种格式引用；abstain=true 时拒答..."
}
```

**Scope 划尖**：

- Phase A 只动"接口形状 + 行为约定"——**不动**检索质量（不加 reranker、不加 hybrid retrieval）；
- **不动**模型生命周期（每次仍然重新加载，这是 Phase B）；
- **不动**存储（仍然两个文件 `doc_embeddings.npy` + `documents.json`）。

也就是说，Phase A 之后**检索召回不会变好**——但模型会"第一次知道自己在做 RAG"，知道要引用证据、知道找不到时该拒答。

### 4. Planned Changes（具体要改什么）

#### 4.1 新增小模块：`src/mini_agent/rag/contract.py`

里面放两个 dataclass。**先伪代码看形状**：

```
Evidence:
  evidence_id : 短字符串，"E1"、"E2" ...
  title       : 文档标题
  url         : 文档链接
  text        : 文档正文片段

RetrievalResult:
  evidence            : Evidence 的列表
  abstain             : 真/假
  abstain_reason      : 字符串 或 空
  model_instructions  : 字符串，给模型读的规则
  + 一个方法 to_tool_payload() : 把自己 dump 成 JSON 字符串
```

**真实 Python 大致这样**：

```python
from dataclasses import dataclass, asdict
import json

@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    title: str
    url: str
    text: str

@dataclass(frozen=True)
class RetrievalResult:
    evidence: list[Evidence]
    abstain: bool
    abstain_reason: str | None
    model_instructions: str

    def to_tool_payload(self) -> str:
        # asdict 把 dataclass 递归转成 dict；json.dumps 再转成字符串
        return json.dumps(asdict(self), ensure_ascii=False)
```

**为什么单独放 contract.py 而不是塞进 search.py**：

- 这两个 dataclass 是"契约"，定义后变化频率应该很低；
- `search.py` 里是检索算法的实现，变化频率会更高；
- 分开能让"改契约"和"改算法"在 git 历史里互不污染。

#### 4.2 改 `src/mini_agent/rag/search.py`

加一个新函数 `retrieve`，保留旧的 `search_documents`（CLI 调试还在用）。

伪代码：

```
ABSTAIN_THRESHOLD = 0.3   # 占位阈值，注释里要写明"未校准，Phase 后期再调"

retrieve(query):
    top = 跑现有 dense 检索 拿到 top-k 结果，每个带 score
    if top 为空 或 top[0].score < ABSTAIN_THRESHOLD:
        return RetrievalResult(
            evidence=[],
            abstain=True,
            abstain_reason="top-1 similarity below threshold",
            model_instructions=MODEL_INSTRUCTIONS,
        )
    evidence_list = []
    for i, item in enumerate(top, start=1):
        evidence_list.append(Evidence(
            evidence_id=f"E{i}",       # i=1 → "E1", i=2 → "E2"
            title=item.title,
            url=item.url,
            text=item.text,
        ))
    return RetrievalResult(
        evidence=evidence_list,
        abstain=False,
        abstain_reason=None,
        model_instructions=MODEL_INSTRUCTIONS,
    )
```

**几个新东西要解释**：

- `f"E{i}"` 是 Python 的 **f-string**，把变量直接插进字符串里。`i=1` 时结果是 `"E1"`，`i=2` 时是 `"E2"`。
- `enumerate(top, start=1)` 给每个元素配一个序号，从 1 开始。等价于"`i` 从 1 数到 len(top)"。
- `ABSTAIN_THRESHOLD = 0.3` 是**全大写模块常量**——Python 里约定俗成"大写 = 不要随便改的常量"。
- **`raw score` 不进 evidence**：envelope 里没有 `score` 字段，按 `project.md` 的长期方向"不要把原始相似度喂给模型"。

#### 4.3 改 `src/mini_agent/tools/docs_search.py`

```python
def search_docs(query: str) -> str:
    from mini_agent.rag.search import retrieve
    result = retrieve(query)
    return result.to_tool_payload()
```

**关键点**：函数签名 `search_docs(query: str) -> str` 完全没变。这样 `chat/loop.py` 里那张 `TOOL_FUNCTIONS` 表完全不动——loop 层对契约升级是**透明**的。

#### 4.4 改 `src/mini_agent/chat/prompts.py`

在 `TOOL_CHAT_SYSTEM_PROMPT` 里追加两条规则（用中文写）：

1. 调用 `search_docs` 后，如果 envelope 里 `abstain=true`，直接告诉用户"知识库里没有足够相关的内容"，**不要凭弱证据硬答**。
2. 其余情况，回答里引用证据必须用 `[E1]`、`[E2]` 这种方括号格式；**只能引用 envelope `evidence` 里实际出现过的 id**；不要编造没出现过的 id。

#### 4.5 abstain 行为的设计

- **触发条件**：仅看 top-1 similarity 是否低于 `ABSTAIN_THRESHOLD`。简单、可解释、以后想换更复杂的策略也只改这一行。
- **触发后**：envelope 里 `evidence=[]`、`abstain=True`，但 `model_instructions` 仍然保留——让模型读到"abstain 时拒答"的规则。
- **阈值是占位值**，源码注释里要中文标注"未经 eval set 校准，Phase 后期再换"。

#### 4.6 `chat/loop.py` 要不要改？

**本期不动 `loop.py`。**

原因：本期所有新增的"行为约束"（必须用 `[E#]` 引用、abstain 时拒答）都是**模型行为**的约束，靠 `prompts.py` + envelope 里自带的 `model_instructions` 就够了。`loop.py` 现在做的事——执行工具 → 把字符串塞回 messages → 让模型再发一轮——和新契约完全兼容（payload 仍然是字符串）。

真正需要 `loop.py` 改动的是**校验**："模型这一轮的回复里 `[E1]` 是不是真的对应到 envelope 里某条 evidence？"。这属于"contract 强制执行"，是 Phase A 之后的事，不在本期范围。Phase A 先**说清契约**，校验留给下一阶段。

### 5. Files Likely To Change（本期会动的文件清单）

| 文件 | 改动 |
|---|---|
| `src/mini_agent/rag/contract.py` | **新增**，放两个 dataclass + 固定的 `model_instructions` 文本 |
| `src/mini_agent/rag/search.py` | 加一个新函数 `retrieve(query)`，保留旧的 `search_documents` |
| `src/mini_agent/tools/docs_search.py` | 内部改成调 `retrieve` 并 `to_tool_payload()`，外部签名不变 |
| `src/mini_agent/chat/prompts.py` | system prompt 末尾追加两条规则（引用语法 + abstain 时拒答） |
| `.claude/progress/current.md` | Phase A 落地之后再补一两行（非本次） |

### 6. What Will Not Change（明确不做什么）

**代码层面不动的**：

- `src/mini_agent/chat/loop.py`：本期不改任何一行。
- `src/mini_agent/rag/build_index.py`：本期不改。
- 检索仍然每次重新加载 embedding 模型（性能问题，留给 Phase B）。
- `mcp/`、`agent/`、`examples/`、`mini_demo/` 都不动。
- 不写任何新的 plan / memory / notes 到 `.claude/` 或 `~/.claude/`。

**不引入的"高级 RAG 套件"**（顺手解释下每个是什么，免得以后看不懂）：

- **chunking（切块）**：把长文档切成小段再分别做 embedding。本期不做，文档单元仍然是整篇。
- **pydantic**：第三方的数据验证库。本期用标准库 dataclass 就够了。
- **数据库 / pgvector / sqlite-vss**：把向量存到数据库里（pgvector 是 PostgreSQL 的向量扩展，sqlite-vss 是 SQLite 的）。本期仍然两文件存盘。
- **reranker（重排器）**：拿到 top-k 之后再用一个更慢更准的模型重新打分。本期不引入。
- **hybrid retrieval（混合检索）**：向量检索 + 关键词检索（如 BM25 / FTS = Full-Text Search）一起跑再合并。本期纯向量。
- **async / 并发**：让检索异步跑。本期同步。
- **observability**：metrics、tracing、结构化日志。本期没有。
- **evaluation harness**：用一组标注好的"问题 → 应该返回什么"来自动评测召回率/准确率。Phase 后期才加。
- **confidence_band**：把分数分桶（如 high/medium/low）暴露给模型。本期 envelope 字段尽量少。
- **Protocol / 服务化**：用 Python 的 Protocol（一种"接口"机制）抽象 backend、或者把 RAG 拆成独立服务。两者都是远期考虑。

### 7. Questions or Tradeoffs To Confirm（动手前需要你拍板）

每条都给了我自己的默认倾向 + 理由，你认同就 yes，不认同直接指出。

1. **envelope 类型放新文件 `rag/contract.py` 还是塞进 `rag/search.py` 顶部？**
   倾向**新建文件**。理由：契约稳定性 > 检索算法稳定性，分文件方便后续 review。
2. **占位阈值 `ABSTAIN_THRESHOLD` 取多少？**
   倾向 `0.3`。Qwen3-Embedding-0.6B 的相似度大致在 cosine 区间，0.3 是个保守起点。源码注释会明确写"未校准"。
3. **`model_instructions` 文本用中文还是中英双语？**
   倾向**纯中文**，跟仓库现有 prompt 风格一致；短一段就够。
4. **`search.py` 的 CLI `main()` 也切到 envelope 输出吗？**
   倾向**不切**。CLI 是给开发者人肉调试用的，应该保留 `score` 字段。新契约只在工具边界（`search_docs`）生效，CLI 透明。
5. **`model_instructions` 里要不要写"禁止编造 evidence_id"？**
   倾向**写**。一行话成本几乎为零，能减少一类幻觉。
6. **旧的 `search_documents(query, top_k) -> list[dict]` 要不要保留？**
   倾向**保留**。CLI 在用，未来 evaluation 也可能用，先并存。
