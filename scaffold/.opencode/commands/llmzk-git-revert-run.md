---
description: Help revert files associated with an llmzk passport/run
---

Run dry-run first:

```bash
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_git_safety.py revert-run "$ARGUMENTS" --dry-run
```

Only apply a revert after explicit user approval.
