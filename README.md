# llmzk

`llmzk` is a lightweight OpenCode + Obsidian harness for building a Zettelkasten with LLM assistance.

This repository is now an **installer/source repo**, not the vault itself.

```text
llmzk repo        = upstream system, scaffold, init command
installed vault   = your Obsidian vault and Git safety boundary
```

## What it installs

The init command creates a vault with:

```text
AGENTS.md
opencode.json
.opencode/                 OpenCode commands, agents, skills, docs, and tools
Templates/                 reusable note templates
00 Inbox/                  raw source inputs
00 Fleeting Notes/         rough personal notes
01 Sources/
02 Literature Notes/
03 Permanent Notes/
04 Concept Notes/
05 Bridge Notes/
06 Contradiction Notes/
07 Index Notes/
08 Wiki Articles/
09 Media/
Logs/                      passports, decision logs, review queues
```

The numbered folders and `Logs/` are real vault-owned output folders. They are checked in empty via `.gitkeep`; generated content is ignored by default in the scaffold `.gitignore`.

## Install into a vault

From a clone of this repository:

```bash
uv run llmzk-init ~/Vaults/MyResearchVault --mode copy --git
```

For development, you can symlink the system layer instead:

```bash
uv run llmzk-init ~/Vaults/MyResearchVault --mode symlink --git
```

Use `copy` for portability. Use `symlink` when actively developing `llmzk` and wanting the vault to use the local upstream files.

## Git safety

The installed vault is initialized as its own Git repository unless you pass `--no-git`.

The intended workflow is:

```text
candidate inventory -> apply changes -> audit -> git diff -> review -> stage -> commit/revert
```

Agents may inspect Git status and diffs, but must not stage, commit, reset, clean, or revert without explicit user approval.

## Main OpenCode commands in an installed vault

```text
/llmzk-ingest <path>
/llmzk-promote <path-or-folder>
/llmzk-audit
/llmzk-normalize-links --dry-run
/llmzk-fix-frontmatter --apply
/llmzk-git-status
/llmzk-git-preflight
/llmzk-git-diff
/llmzk-git-commit-message <passport>
/llmzk-git-revert-run <passport>
/llmzk-synthesize <topic>
```

## Design boundary

```text
obsidian-skills       = Obsidian mechanics
llmzk skills          = Zettelkasten judgement
.opencode/llmzk-tools = deterministic audit, cleanup, Git safety helpers
Git                   = vault safety and rollback boundary
```

## Repository layout

```text
scaffold/             files installed into a vault
src/llmzk/init.py     init command
pyproject.toml        upstream installer project
```
