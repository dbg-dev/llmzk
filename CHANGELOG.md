# Changelog

## v5.2.1 — Bash init + scaffold-owned tools cleanup

- Replaced the root Python `llmzk-init` package with `scripts/init-vault.sh`.
- Removed root `src/llmzk`, root `pyproject.toml`, root `.python-version`, and root `uv.lock` from the source-repo design.
- Kept the source repo as scaffold + install script, not a partially installed vault.
- Added root `AGENTS.md` explaining source-repo vs installed-vault boundaries.
- Moved all installed-vault deterministic tools into `scaffold/.opencode/llmzk-tools/src/llmzk_tools/`.
- Converted `scaffold/.opencode/llmzk-tools` into a real Python package with `[project.scripts]` entries.
- Added `.opencode/bin/llmzk` wrapper so command files do not need raw `uv run --project ...` commands.
- Updated OpenCode command files to call the wrapper.
- Kept `tyro` as the CLI layer for scaffold tools.
- Kept `GitPython` as the Git layer for scaffold tools.
- Kept the high-judgement bridge/contradiction skill improvements from v5.2.

## v5.2 — Tyro + GitPython migration

- Migrated upstream Python CLIs toward `tyro` and `GitPython`.
- Added source status and activation-function wording fixes.

## v5.1 — Git safety hardening

- Added `llmzk-doctor`.
- Added Git safety command set.
- Strengthened broad-write preflight guidance.

## v5 — OpenCode init + Git safety architecture

- Split upstream repo from installed vault.
- Added scaffold-based install model.
