---
description: Show a concise Git diff summary for llmzk changes
---

Use the **fast operating profile** from `.opencode/docs/OPERATING_PROFILES.md`.
Use RTK for token-efficient diff inspection if available. Otherwise run:

```bash
.opencode/bin/llmzk git diff . --stat
```

For focused review, inspect changed note files before staging.
