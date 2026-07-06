---
description: Show a concise Git diff summary for llmzk changes
---

Use RTK for token-efficient diff inspection if available. Otherwise run:

```bash
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_git_safety.py diff --stat
```

For focused review, inspect changed note files before staging.
