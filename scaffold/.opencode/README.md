# llmzk OpenCode harness

This folder is installed into a concrete Obsidian vault by `scripts/init-vault.sh` from the upstream source repo.

## Contents

```text
commands/       OpenCode slash commands
agents/         Optional specialist agents
skills/         llmzk domain skills
docs/           llmzk operating docs
bin/llmzk       Wrapper for deterministic tools
llmzk-tools/    Python package for audit, doctor, cleanup, candidate review validation, and Git safety
```

## Tool wrapper

Use the wrapper from the vault root:

```bash
.opencode/bin/llmzk audit .
.opencode/bin/llmzk doctor .
.opencode/bin/llmzk git preflight .
.opencode/bin/llmzk git diff . --stat
.opencode/bin/llmzk review-validate "Logs/Candidate Reviews/example.md"
```

The wrapper invokes console scripts from `.opencode/llmzk-tools`, whose CLIs use `tyro`. Git-facing commands use `GitPython`.

## Candidate review gate

`/llmzk-ingest` and `/llmzk-promote` create candidate review files first. Durable notes are written only by `/llmzk-write-approved <candidate-review-file>`.
