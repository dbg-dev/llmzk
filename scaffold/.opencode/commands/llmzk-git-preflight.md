---
description: Check whether the vault is safe for a broad llmzk write operation
---

Use the **fast operating profile** from `.opencode/docs/OPERATING_PROFILES.md`.
Run:

```bash
.opencode/bin/llmzk git preflight .
```

If the working tree is dirty, ask before mixing new generated changes with existing edits.
