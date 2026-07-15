---
description: Help revert files associated with an llmzk passport/run
---

Use the **fast operating profile** from `.opencode/docs/OPERATING_PROFILES.md`.
Run dry-run first:

```bash
.opencode/bin/llmzk git revert-run "$ARGUMENTS" --dry-run
```

Only apply a revert after explicit user approval.
