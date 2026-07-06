---
description: Draft a structured commit message from an llmzk passport
---

Run:

```bash
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_git_safety.py commit-message "$ARGUMENTS"
```

This drafts a commit message only. Do not commit unless the user explicitly asks.
