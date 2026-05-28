# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

This project is an unimplemented skeleton. As of this writing, all files are
empty: there is no code, no declared dependencies, no build/test/lint
configuration, and no commits. The notes below describe the intended layout only
— update this file with real commands and architecture once code exists.

## Layout

- `src/mini_agent/` — Python package (`src` layout). `main.py` is the intended
  entry point; `__init__.py` marks the package.
- `pyproject.toml` — package metadata and dependencies (currently empty).
- `README.md` — project documentation (currently empty).

## Conventions

- Uses the `src/` layout, so the package must be installed (e.g. an editable
  install) to be importable rather than relying on the working directory.
