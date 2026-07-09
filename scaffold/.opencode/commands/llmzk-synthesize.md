---
description: Synthesize a wiki/article output from existing notes
---

Run Git preflight first:

```bash
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_git_safety.py preflight .
```

If preflight reports a dirty working tree, stop before broad writes unless the user explicitly says to continue with mixed changes.

Use the `llmzk-synthesize` skill on `$ARGUMENTS`.

Use installed `obsidian-markdown` for Obsidian note syntax.

Only synthesize from existing notes. Do not synthesize directly from raw sources.

After writing wiki/article output, run:

```bash
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_audit.py .
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_git_safety.py diff . --stat
```

End by summarising created/changed files and the audit result. Do not stage, commit, reset, clean, or revert unless the user explicitly asks.
