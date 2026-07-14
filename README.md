# llmzk

Current version: v5.3.3

`llmzk` is a lightweight OpenCode + Obsidian harness for building a Zettelkasten with LLM assistance.

This repository is an **installer/source repo**, not the vault itself.

```text
llmzk repo        = upstream scaffold, skills, commands, templates, install script
installed vault   = your Obsidian vault and Git safety boundary
```

## What it installs

The install script creates a vault with:

```text
AGENTS.md
opencode.json
.opencode/                 OpenCode commands, agents, skills, docs, wrapper, tools
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
Logs/                      candidate reviews, passports, decision logs, review queues
```

The numbered folders and `Logs/` are real vault-owned folders. They are created with `.gitkeep` placeholders, and generated durable notes/logs are Git-visible by default so vault safety can use `git status` and `git diff`.

## Install into a vault

From a clone of this repository:

```bash
./scripts/init-vault.sh ~/Vaults/MyResearchVault --mode copy --git --commit
```

For development, you can symlink the system layer instead:

```bash
./scripts/init-vault.sh ~/Vaults/MyResearchVault --mode symlink --git --commit
```

Use `copy` for portability. Use `symlink` when actively developing `llmzk` and wanting the vault to use the local upstream files.

## Git safety

The installed vault is initialized as its own Git repository unless you pass `--no-git`.

The intended workflow is:

```text
git preflight -> candidate review -> user approval -> write approved -> cleanup -> audit -> git diff -> stage -> commit/revert
```

Agents may inspect Git status and diffs, but must not stage, commit, reset, clean, or revert without explicit user approval.

## Main OpenCode commands in an installed vault

```text
/llmzk-ingest <path>                  # safe alias for candidate review
/llmzk-ingest-candidates <path>       # create candidate review only
/llmzk-promote <path-or-folder>       # safe alias for candidate review
/llmzk-promote-candidates <path>      # create candidate review only
/llmzk-write-approved <review-file>   # write approved [x] candidates
/llmzk-review-validate <review-file>
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


## Candidate review gate

In v5.3, ingest and promote are review-gated by default:

```text
/llmzk-ingest <source>
  -> creates `Logs/Candidate Reviews/...md` only

# edit checkboxes and reviewer notes

/llmzk-write-approved <candidate-review-file>
  -> writes approved durable notes, passport, decision log, audit, and Git diff
```

Synthesize is intentionally out of scope for the v5.3 review gate.

## Installed-vault tool wrapper

The installed vault includes a small wrapper:

```bash
.opencode/bin/llmzk audit .
.opencode/bin/llmzk doctor .
.opencode/bin/llmzk git preflight .
.opencode/bin/llmzk git diff . --stat
.opencode/bin/llmzk review-validate "Logs/Candidate Reviews/example.md"
```

The wrapper hides the `uv run --project .opencode/llmzk-tools ...` implementation detail from OpenCode command files.

## Design boundary

```text
obsidian-skills       = Obsidian mechanics
llmzk skills          = Zettelkasten judgement
.opencode/llmzk-tools = deterministic audit, cleanup, doctor, Git safety helpers
Git                   = vault safety and rollback boundary
```

## Python CLI implementation

There is no root Python package in this source repo. Runtime Python tools live only in the scaffold at:

```text
scaffold/.opencode/llmzk-tools/
```

That package exposes console scripts with `[project.scripts]`, uses `tyro` for CLIs, and uses `GitPython` for Git-facing operations.

## Repository layout

```text
scripts/init-vault.sh             Bash installer for creating a concrete vault
scaffold/                         files installed into a vault
scaffold/.opencode/llmzk-tools/   installed-vault Python tools package
scaffold/.opencode/bin/llmzk      installed-vault wrapper
scaffold/Templates/               reusable note templates
```


## v5.3.3 bugfix notes

This release fixes audit false positives for wikilinks whose titles contain periods such as `w.r.t.`, regenerates Review Queue reports on each audit, and normalises candidate-review status timestamps when reviews are marked applied/rejected/superseded.


## v5.3.3 fixes

- Path-qualified `origin_trail` links for promoted notes from `00 Fleeting Notes/`.
- Audit warning for duplicate note basenames across fleeting and durable folders.
- Candidate-review frontmatter normalization for lowercase booleans and quoted ISO timestamps.
- Backpropagation cost wording guardrails.
- Softer reasoning-distillation contradiction wording guidance.
