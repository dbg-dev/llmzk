---
description: Report or update the installed llmzk system layer from an upstream scaffold
---

Use the **fast operating profile** from `.opencode/docs/OPERATING_PROFILES.md`.

This command is for system-layer maintenance only. It must not touch durable notes or logs.

Dry-run first:

```bash
.opencode/bin/llmzk update . --source /path/to/llmzk
```

Apply after reviewing the plan:

```bash
.opencode/bin/llmzk update . --source /path/to/llmzk --apply
```

For a symlink-mode vault:

```bash
.opencode/bin/llmzk update . --source /path/to/llmzk --mode symlink --apply
```

Then run:

```bash
.opencode/bin/llmzk doctor .
.opencode/bin/llmzk git diff . --stat
```

Do not use `--allow-dirty` unless the dirty Git state has already been reviewed.
