# llmzk OpenCode harness

This directory contains the installed `llmzk` system layer for an Obsidian vault.

## What OpenCode discovers here

```text
.opencode/commands/   slash commands such as /llmzk-ingest
.opencode/skills/     llmzk skills loaded on demand
.opencode/agents/     specialist review/synthesis agents
.opencode/plugins/    optional plugins, if added later
```

Other files in `.opencode/` are ordinary support files. They are referenced by
`AGENTS.md`, `opencode.json`, commands, or skills.

## Boundary

```text
.opencode/        = system layer: commands, skills, agents, docs, tools
Templates/        = reusable note forms
00-09 folders     = vault-owned user/generated note content
Logs/             = generated passports, decision logs, review queues
```

## Tools

Run from the vault root:

```bash
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_doctor.py .
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_audit.py .
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_git_safety.py status
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_git_safety.py diff . --stat
```

Agents may inspect Git state freely, but must not stage, commit, reset, clean, or
revert without explicit user approval.
