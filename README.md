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

The numbered folders and `Logs/` are real vault-owned folders. They are created with `.gitkeep` placeholders, and generated durable notes/logs are Git-visible by default so vault safety can use `git status` and `git diff`.

## Install into a vault

From a clone of this repository:

```bash
uv run llmzk-init ~/Vaults/MyResearchVault --mode copy --git --commit
```

For development, you can symlink the system layer instead:

```bash
uv run llmzk-init ~/Vaults/MyResearchVault --mode symlink --git --commit
```

Use `copy` for portability. Use `symlink` when actively developing `llmzk` and wanting the vault to use the local upstream files.

## Git safety

The installed vault is initialized as its own Git repository unless you pass `--no-git`. `llmzk-init` also runs a doctor check by default; disable it with `--no-doctor` if needed.

The intended workflow is:

```text
git preflight -> candidate inventory -> apply changes -> cleanup -> audit -> git diff -> review -> stage -> commit/revert
```

Agents may inspect Git status and diffs, but must not stage, commit, reset, clean, or revert without explicit user approval.

## Main OpenCode commands in an installed vault

```text
/llmzk-ingest <path>
/llmzk-promote <path-or-folder>
/llmzk-audit
/llmzk-normalize-links --dry-run
/llmzk-fix-frontmatter --apply
/llmzk-doctor
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

## Python CLI implementation

The Python CLIs use:

```text
tyro      = typed command-line interfaces
GitPython = Git status, init, diff, ignore, checkout, and commit helpers
```

The installed vault tools under `.opencode/llmzk-tools/scripts/` follow the same convention.

## Repository layout

```text
scaffold/             files installed into a vault
src/llmzk/init.py     tyro-based init command
src/llmzk/doctor.py   tyro + GitPython installed-vault doctor command
pyproject.toml        upstream installer project
```
