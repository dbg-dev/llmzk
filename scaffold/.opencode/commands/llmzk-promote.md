---
description: Promote selected fleeting notes into durable Zettelkasten notes
---

Run Git preflight first:

```bash
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_git_safety.py preflight .
```

If preflight reports a dirty working tree, stop before broad writes unless the user explicitly says to continue with mixed changes.

Use the `llmzk-promote` skill on `$ARGUMENTS`.

Use installed `obsidian-markdown` for Obsidian syntax. Classify fleeting notes before promoting. Do not convert all fleeting notes into concept notes.

After notes are written, run:

```bash
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_fix_frontmatter.py . --apply
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_audit.py .
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_git_safety.py diff . --stat
```

End by summarising created/changed files and the audit result. Do not stage, commit, reset, clean, or revert unless the user explicitly asks.
