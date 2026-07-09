---
description: Check that the installed llmzk vault scaffold is healthy
---

Run:

```bash
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_doctor.py .
```

Use this after installation, after updating the harness, and before debugging command failures.

For a stricter pre-run check that also fails on a dirty Git working tree, run:

```bash
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_doctor.py . --fail-if-dirty
```
