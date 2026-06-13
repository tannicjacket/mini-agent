---
name: learning-note
description: Before coding any module/phase/feature in this repo, write a beginner-friendly learning-oriented pre-execution note so the user (who is not yet fluent in Python) can understand the change before it lands. Use BEFORE editing source files when the user opens a new unit of work — e.g. "let's start Phase A/B/C", "redesign the RAG module", "rewrite docs_search", "before you code, explain ...". The note must explain every new Python syntax / library / industry term / project-coined concept the FIRST time it appears (what / how / where / why), favor pseudocode over raw Python for explaining structure, and open with a "0. 概念预热" primer section. It covers concept primer, current architecture, current flow, goal, planned changes, files likely to change, what will NOT change, and open tradeoffs. Persist the note to `docs/<topic>-note.md` (default `docs/rag-note.md` for the active RAG track). Skip for trivial bugfixes, renames, dependency bumps, doc-only edits, or work the user has already approved in detail.
---

# Learning Note

## 用途 / Purpose

在动任何 module / phase / feature 的代码之前，先输出一份**面向学习的 pre-execution note**，帮用户理解这次要做什么、为什么、影响哪些文件，以及哪些事**故意不做**。**默认读者不熟悉 Python**，所以每一次出现新语法 / 新概念 / 新术语都要解释清楚。

这份 note 会同时被持久化为用户自己的 study/worklog。它**不是** harness memory：不要写入 `CLAUDE.md`、`.claude/project.md`、`.claude/progress/*` 或任何 `~/.claude` / `~/.codex` 目录。

## 触发场景

- "开始 Phase X" / "重构 / 重新设计 / 重写 Y 模块"
- "写代码之前先解释一下…"
- 用户提到 roadmap 阶段（如 `.claude/project.md` 里的 RAG Planning Phase A/B/C/D）。

**不触发**的情况：

- 用户已经在本次对话里详细确认了具体方案；
- 单行修复、重命名、依赖升级、纯文档改动；
- 用户明确说 "直接干 / 不用解释"。

## Workflow

按顺序执行；**第 5 步之前不要动任何源代码文件**。

1. **先读相关文件。** 找到 module 的入口、数据流入口和出口、以及项目自身的规划材料（如 `README.md`、`.claude/project.md`、`.claude/progress/current.md`）。note 必须基于真实当前代码，而不是回忆或猜测。
2. **按下面的 8-section 格式起草 note**（含必填的 "0. 概念预热"）。
3. **在 chat 里把 note 完整展示给用户。** 语言遵循仓库约定：本仓库的 `CLAUDE.md` 要求中文回复 + 英文技术词，note 也按这个习惯写。
4. **把 note 追加到 `docs/<topic>-note.md`。** 默认 topic = `rag`，即 `docs/rag-note.md`。如果文件不存在，先创建（同时初始化空的 global TOC）。新条目**插到文件顶部**（最近的在最上），并**同步在 global TOC 顶部追加一段对应 bullet 树**；详见下文「目录与锚点」一节。
5. **停下来等用户显式确认后再写代码。** 如果用户调整方向，**改同一条目**，不要追加新条目把历史搞乱。

## Note format（固定 8 个 section）

顺序固定。每节务求**短而具体**：写出真实文件名、函数名、tradeoff，不要套话；**但解释新概念时该展开就展开，不要省**。

0. **概念预热 / Concept Primer**（必填）—— 把这份 note 后面会反复用到的术语（contract / envelope / evidence_id / abstain / citation 等）和 Python 语法（`type annotation`、`@dataclass`、`frozen=True`、`str | None`、`f"..."`、`enumerate` 等）**一次性统一解释**。每一项遵循"是什么 / 怎么用 / 在哪用 / 为什么用"四问。
1. **Current Architecture** —— 周边系统现状，只够铺垫这次改动即可。涉及新模块/库时一句话点明它是什么。
2. **Current Flow** —— 这个 module 当前端到端怎么走，包括它跟调用方的当前 contract。**优先用伪代码画一遍流程**。
3. **Goal** —— 这一步要做什么，用项目自己的语言。**用伪代码贴 before/after 形状对比**，让 contract 改动一眼可见。把 scope 划尖（例：「契约清理，不是质量改进」）。
4. **Planned Changes** —— 逐条列具体改动。每条**先伪代码画形状，再贴真实 Python**；每出现一个新语法都加一行说明。
5. **Files Likely To Change** —— 表格列出文件 + 一句话改动；新增文件也在此列出。
6. **What Will Not Change** —— 显式列非目标。涉及读者可能不熟的术语（pgvector / BM25 / reranker / hybrid retrieval 等）时**顺手一句解释"是什么、为什么本期不引入"**。这一节是 scope 的护城河，不能省。
7. **Questions or Tradeoffs To Confirm** —— 写代码前需要用户拍板的开放问题。每条要给出**我的默认倾向 + 理由**，不要光抛问题。

**参考资料的分工**：

- `references/example-phase-a-overview.md` —— 简短 calibration 样例，看 7 个核心 section 的**骨架**与气质（不含 section 0）。**第一次在本仓库触发该 skill 时务必先读**。
- `docs/rag-note.md`（仓库内已有的第一条 entry）—— 完整 8-section beginner-friendly 样例，**展示新标准下"section 0 概念预热 + 伪代码 + 解释颗粒度"的实际深度**。需要看具体写法时读它。

## 解释风格（强制标准）

读者**默认不熟悉 Python**。以下规则是强制的，不是 nice-to-have。

1. **每一个新东西第一次出现都要解释**，并回答四问：是什么 / 怎么用 / 在哪用 / 为什么用。覆盖范围包括：
   - **Python 语法**：type annotation（`query: str`、`-> str`）、`@dataclass`、`frozen=True`、`list[X]`、`Optional` / `str | None`、`@property`、`__init__`、`async`/`await`、decorator、context manager、`with`、`f"..."` 字符串、`enumerate`、`zip`、解构赋值、生成器、import 形式（`from x import y` 与 `import x.y`）等。
   - **行业术语**：embedding、cosine similarity、tool calling / function calling、JSON schema、system prompt、token、retrieval、reranker、BM25、FTS、hybrid retrieval、abstain、citation、envelope、contract、grounding、chunking 等。
   - **第三方库**：pydantic、sentence-transformers、numpy、modelscope、openai SDK、mcp 等——第一次提到时一句话说"这是什么、在做什么"。
   - **项目自创概念**：`evidence_id`、`RetrievalResult`、`ABSTAIN_THRESHOLD`、`model_instructions` 等——一定要解释 **是什么、怎么用、在哪用、为什么用** 四个角度。
2. **优先伪代码，后真实 Python**。伪代码用来画"形状"；真实 Python 用来落地。读者先理解形状再看代码，比直接读代码更不容易卡。
3. **重要术语集中在第 0 节"概念预热"统一定义**，不要散落各处反复解释。后面的 section 只用这些已经定义的词。
4. **数据验证 vs type annotation 必须讲清楚**：
   - **type annotation**（`x: str`、`-> int`）= 注释 / hint，Python 默认**不强制**——传错类型不会报错；
   - **数据验证（data validation）**（pydantic 之类）= 运行时真正检查类型/规则，违反会主动报错。
   - 涉及二选一（如 dataclass vs pydantic）时必须解释为什么这样选。
5. 不要写得像高级工程师内部备忘录。**写得像在教自己**：每一句话问一下"我下个月再看这句话，需要回查什么吗？" 如果需要——就在原地解释。

## 存储规则

- **路径：** `docs/<topic>-note.md`。当前 active RAG track → `docs/rag-note.md`。其他模块按同样模式取名（例如未来的 chat loop → `docs/chat-note.md`）。
- **每条目标题：** `## <YYYY-MM-DD> — <module / phase 短标题>`，例如 `## 2026-06-12 — RAG Phase A: Retrieval Contract Cleanup`。
- **排序：** 新的条目放最上面。
- **绝对不要**把这份 note 写进 `CLAUDE.md`、`.claude/project.md`、`.claude/progress/*`，也不要写进 `~/.claude/` / `~/.codex/` 的任何 memory 目录。
- 如果仓库有路径禁区，向用户确认改放哪里，不要自己悄悄改路径。

## 目录与锚点 / TOC and anchor rules

每个 `docs/<topic>-note.md` 文件**顶部必须有一份 file-level 的全局 TOC**，按 module / phase 浏览所有 entry。规则如下：

1. **位置**：放在文件标题段（intro 段）之后、第一个 `---` 之前。标题用 `## 目录 / Table of Contents`，附一句简短的说明。
2. **形态**：每个 entry 是一层 bullet（顶层带日期 + entry 标题，链接指向 entry 的 anchor），里面再缩进展开它自己的 section + 子节链接。新 entry 加在 TOC **最上面**，与正文 entry 顺序对齐。
3. **anchor 命名空间**：每个 entry 用 **phase 标识做前缀**，避免多 phase 之间 anchor id 冲突。
   - Phase A 的所有 section anchor 都是 `phase-a-sec-X` 形式（例：`phase-a-sec-0`、`phase-a-sec-4-2`）；
   - Phase B 用 `phase-b-sec-X`，以此类推；
   - 每个 entry 的日期标题本身也带一个顶层 anchor（例如 `<a id="phase-a"></a>`），TOC 顶层 bullet 链向它。
4. **anchor 实现**：统一用 **HTML `<a id="..."></a>` 标签嵌在标题文字前**，例：`### <a id="phase-a-sec-0"></a>0. 概念预热（...）`。不要依赖各家 Markdown 渲染器对中文 / 标点的 auto-anchor 处理差异——GitHub、VSCode preview、本地编辑器需要都稳定可点。
5. **加新 entry 时**：
   - 先在正文最上面插入新 entry（按存储规则的日期标题格式）；
   - 再在 global TOC 最上面追加一段对应的 bullet 树；
   - 新 entry 的所有 anchor 用**新 phase 前缀**；
   - **不要去改老 entry 的 anchor id** —— 已经发出去 / 引用过的链接还要继续有效。
6. **示例**：参见 `docs/rag-note.md` 当前的形态。

## 输出语言

本仓库 `CLAUDE.md` 硬约束：响应使用中文，技术词保留英文。Note 的散文按这个规则写；section 标题保留英文以维持稳定；文件路径、类型、flag、库名等标识符永远保持原样。

## 反模式（不要这样做）

- 把 note 写成完整的设计文档 —— 这是 **pre-execution 草图**，不是 spec。
- **省略 "0. 概念预热" 一节** —— 读者会被术语和语法堵住，note 失效。
- **真实 Python 直接上而不先伪代码** —— 不熟 Python 的读者立刻卡住。
- 新术语不解释 / 假定读者懂 —— 哪怕 `@dataclass`、`f"..."`、`enumerate` 这种"常识"也要解释。
- 重复 `CLAUDE.md` / `.claude/project.md` 已经写过的内容 —— 引用即可。
- 「Files Likely To Change」列出全仓库文件 —— 只列这一步真的会动的。
- 跳过 section 6 —— 那是 scope 的护城河。
- **省略 global TOC / 标题不挂 `<a id="...">` anchor** —— 多 entry 后这份 worklog 没法跳转浏览。
- **回头去改老 entry 的 anchor id** —— 已经发出去的链接会失效；新 phase 用新前缀就行。
- 用户回复之前就开始改代码 —— 哪怕你觉得方案显然正确。
