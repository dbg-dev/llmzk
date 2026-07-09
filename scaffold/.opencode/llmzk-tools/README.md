# llmzk tools

Small Python utilities used by OpenCode commands for audit, link normalization,
frontmatter cleanup, run logs, install checks, Git safety, and smoke tests.

Run from the vault root, for example:

```bash
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_doctor.py .
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_audit.py .
```

## Git safety helper

```bash
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_git_safety.py status .
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_git_safety.py preflight .
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_git_safety.py diff . --stat
```
