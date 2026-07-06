# llmzk Git safety

Use this skill when a task involves vault writes, staging, committing, reverting, or reviewing generated note changes.

## Purpose

Git is the safety boundary for llmzk-generated vault changes.

The intended cycle is:

```text
inspect -> candidate inventory -> write -> audit -> diff -> stage -> commit or revert
```

## Rules

- Check Git status before broad writes.
- Warn before mixing a new llmzk run into a dirty working tree.
- After broad writes, show a concise diff summary.
- Never stage, commit, reset, clean, or revert without explicit user approval.
- Prefer dry-runs before destructive actions.
- Use RTK for token-efficient status/diff review when available.

## Useful commands

```bash
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_git_safety.py status
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_git_safety.py diff --stat
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_git_safety.py preflight
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_git_safety.py commit-message Logs/Passports/<run>.yaml
```

Read `references/git_safety_protocol.md` for the full protocol.
