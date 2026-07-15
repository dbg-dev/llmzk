---
description: Check that the installed llmzk vault scaffold is healthy
---

Use the **fast operating profile** from `.opencode/docs/OPERATING_PROFILES.md`.
Run:

```bash
.opencode/bin/llmzk doctor .
```

Use this after installation, after updating the harness, and before debugging command failures.

For a stricter pre-run check that also fails on a dirty Git working tree, run:

```bash
.opencode/bin/llmzk doctor . --fail-if-dirty
```
