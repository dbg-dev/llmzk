---
description: Check whether the vault is safe for a broad llmzk write operation
---

Run:

```bash
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_git_safety.py preflight
```

If the working tree is dirty, ask before mixing new generated changes with existing edits.
