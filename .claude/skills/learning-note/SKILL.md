---
name: learning-note
description: Before coding any module/phase/feature in this repo, write a short learning-oriented pre-execution note so the user can understand the change before it lands. Use BEFORE editing source files when the user opens a new unit of work — e.g. "let's start Phase A/B/C", "redesign the RAG module", "rewrite docs_search", "before you code, explain ...". The note covers current architecture, current flow, goal, planned changes, files likely to change, what will NOT change, and open tradeoffs. Persist the note to `docs/<topic>-note.md` (default `docs/rag-note.md` for the active RAG track). Skip for trivial bugfixes, renames, dependency bumps, doc-only edits, or work the user has already approved in detail.
---

# Learning Note

## 用途 / Purpose

在动任何 module / phase / feature 的代码之前，先输出一份**面向学习的 pre-execution note**，帮用户理解这次要做什么、为什么、影响哪些文件，以及哪些事**故意不做**。这份 note 同时被持久化为用户自己的 study/worklog。

这不是 harness memory：不要写入 `CLAUDE.md`、`.claude/project.md`、`.claude/progress/*` 或任何 `~/.claude` / `~/.codex` 目录。

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
2. **按 7-section 格式起草 note。** 见下文「Note format」。
3. **在 chat 里把 note 完整展示给用户。** 语言遵循仓库约定：本仓库的 `CLAUDE.md` 要求中文回复 + 英文技术词，note 也按这个习惯写。
4. **把 note 追加到 `docs/<topic>-note.md`。** 默认 topic = `rag`，即 `docs/rag-note.md`。如果文件不存在，先创建。新条目**插到文件顶部**（最近的在最上），便于回看。
5. **停下来等用户显式确认后再写代码。** 如果用户调整方向，**改同一条目**，不要追加新的条目把历史搞乱。

## Note format

固定 7 个 section，顺序不变。每节务求**短而具体**：写出真实文件名、函数名、tradeoff，不要套话。

1. **Current Architecture** — 简述周边系统现状，只够铺垫这次改动即可。
2. **Current Flow** — 这个 module 当前端到端怎么走，包括它跟调用方的当前 contract。
3. **Goal** — 用项目自己的语言说清这一步要做什么。**把 scope 划尖**（例：「契约清理，不是质量改进」）。
4. **Planned Changes** — 逐条列具体改动。每条都点出文件 / 符号 / 新形状（类型、返回值、prompt 子句等）。
5. **Files Likely To Change** — 表格列出文件 + 一句话改动；新增文件也在此列出。
6. **What Will Not Change** — 显式列非目标。这一节是 scope 的护城河，**不能省**。
7. **Questions or Tradeoffs To Confirm** — 写代码前需要用户拍板的开放问题。每条要给出**我的默认倾向 + 理由**，不要光抛问题。

完整的 calibration 样例见 `references/example-phase-a-overview.md`。**第一次在本仓库触发该 skill 时务必先读这个样例**，让 note 的风格、深度和语气与用户已经接受过的 Phase A 概述保持一致。

## 存储规则

- **路径：** `docs/<topic>-note.md`。当前 active RAG track → `docs/rag-note.md`。其他模块按同样模式取名（例如未来的 chat loop → `docs/chat-note.md`）。
- **每条目标题：** `## <YYYY-MM-DD> — <module / phase 短标题>`，例如 `## 2026-06-12 — RAG Phase A: Retrieval Contract Cleanup`。
- **排序：** 新的条目放最上面。
- **绝对不要**把这份 note 写进 `CLAUDE.md`、`.claude/project.md`、`.claude/progress/*`，也不要写进 `~/.claude/` / `~/.codex/` 的任何 memory 目录。
- 如果仓库有路径禁区，向用户确认改放哪里，不要自己悄悄改路径。

## 输出语言

本仓库 `CLAUDE.md` 硬约束：响应使用中文，技术词保留英文。Note 的散文部分按这个规则写；section 标题保留英文以维持稳定；文件路径、类型、flag 等标识符永远保持原样。

## 反模式（不要这样做）

- 把 note 写成完整的设计文档 —— 这是 **pre-execution 草图**，不是 spec。
- 重复 `CLAUDE.md` / `.claude/project.md` 已经写过的内容 —— 引用即可。
- 「Files Likely To Change」列出全仓库文件 —— 只列这一步真的会动的。
- 跳过 section 6 —— 那是 scope 的核心。
- 用户回复之前就开始改代码 —— 哪怕你觉得方案显然正确。
