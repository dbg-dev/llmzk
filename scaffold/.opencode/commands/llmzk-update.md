---
description: Report or update the installed llmzk system layer from an upstream scaffold
---

Use the **fast operating profile** from `.opencode/docs/OPERATING_PROFILES.md`.

This command is for system-layer maintenance only. It must not touch durable notes or logs.

The preferred update path is from the upstream source checkout because it assembles the generated scaffold package first:

```bash
./scripts/update-vault.sh /path/to/vault
./scripts/update-vault.sh /path/to/vault --apply
```

Direct wrapper use is supported only after the source scaffold has been assembled:

```bash
cd /path/to/llmzk
python3 scripts/build-scaffold.py

cd /path/to/vault
.opencode/bin/llmzk update . --source /path/to/llmzk
.opencode/bin/llmzk update . --source /path/to/llmzk --apply
```

For a symlink-mode vault:

```bash
./scripts/update-vault.sh /path/to/vault --mode symlink --apply
```

Then run:

```bash
.opencode/bin/llmzk doctor .
.opencode/bin/llmzk git diff . --stat
```

Do not use `--allow-dirty` unless the dirty Git state has already been reviewed.
