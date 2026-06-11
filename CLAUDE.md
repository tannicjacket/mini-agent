# CLAUDE.md

This file defines project-level guidance for Claude Code in this repository.

## Commands
See `.claude/runbook.md` for runnable entrypoints and workflow notes.

## Conventions
Keep this file short. Put stable project memory in `.claude/project.md` and short-lived progress in `.claude/progress/current.md`.

## Architecture
The main project lives under `src/mini_agent/` and currently includes `agent`, `chat`, `tools`, `rag`, and `mcp` modules.

## Hard Constraints

1. All responses to the user must be in Chinese.
2. Keep technical terms in English instead of forcing translation.
3. Any newly added code comments, explanatory notes, and change notes must be written in Chinese.
4. Treat `mini_demo/` as out of scope unless the user explicitly asks for it.
5. Ignore the `python-playground` branch unless the user explicitly asks for it.

## Known Gotchas
No project-specific gotchas are recorded yet.
