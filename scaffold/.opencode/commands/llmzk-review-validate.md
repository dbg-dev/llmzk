---
description: Validate a candidate review file before writing approved notes
---

Use the **fast operating profile** from `.opencode/docs/OPERATING_PROFILES.md`.
Validate `$ARGUMENTS`:

```bash
.opencode/bin/llmzk review-validate "$ARGUMENTS"
```

If validation fails, explain what needs to be fixed in the candidate review file before `/llmzk-write-approved` is run.
