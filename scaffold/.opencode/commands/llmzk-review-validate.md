---
description: Validate a candidate review file before writing approved notes
---

Validate `$ARGUMENTS`:

```bash
.opencode/bin/llmzk review-validate "$ARGUMENTS"
```

If validation fails, explain what needs to be fixed in the candidate review file before `/llmzk-write-approved` is run.
