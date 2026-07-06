---
description: Fix malformed YAML frontmatter in llmzk notes
---

Run:

```bash
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_fix_frontmatter.py . $ARGUMENTS
```

Use `--apply` to modify files.
