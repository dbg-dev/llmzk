# llmzk maintenance and updates

`llmzk` separates the vault-owned knowledge graph from the installed system layer.

## What an update may touch

The update workflow may update only these system paths:

```text
AGENTS.md
opencode.json
.gitignore
.llmzk.yaml metadata fields
.opencode/
Templates/
```

It must not copy, delete, or rewrite durable knowledge folders:

```text
00 Inbox/
00 Fleeting Notes/
01 Sources/
02 Literature Notes/
03 Permanent Notes/
04 Concept Notes/
05 Bridge Notes/
06 Contradiction Notes/
07 Index Notes/
08 Wiki Articles/
09 Media/
Logs/
```

## Copy-mode users

Copy mode is portable and stable. The installed vault owns its own copy of `.opencode/` and `Templates/`.

Recommended update flow from the upstream source checkout:

```bash
./scripts/update-vault.sh ~/Vaults/AI
./scripts/update-vault.sh ~/Vaults/AI --apply
```

Or from inside the installed vault:

```bash
.opencode/bin/llmzk update . --source /path/to/llmzk
.opencode/bin/llmzk update . --source /path/to/llmzk --apply
.opencode/bin/llmzk doctor .
```

Do not apply an update over a dirty vault unless you have reviewed the dirty state.
Use `--allow-dirty` only when the dirty files are intentional.

## Symlink-mode users

Symlink mode is for active development. The installed vault points `.opencode/` and `Templates/` at the upstream source checkout.

Recommended update flow:

```bash
cd /path/to/llmzk
git pull
./scripts/update-vault.sh ~/Vaults/AI --mode symlink --apply
```

In symlink mode, the vault normally receives source changes immediately through the symlinks. The update command mainly repairs links, root files, and `.llmzk.yaml` metadata.

## Drift detection

Use dry-run update to detect system-layer drift:

```bash
.opencode/bin/llmzk update . --source /path/to/llmzk
```

Use doctor to check installed-version metadata, source path, install mode, tool registration, Git visibility, and vault structure:

```bash
.opencode/bin/llmzk doctor .
```

A version mismatch between `.llmzk.yaml` and the installed tools is a warning that the system layer may not be fully updated.

## Git safety

The update workflow is a system-layer operation. It should still be reviewed with Git:

```bash
.opencode/bin/llmzk git preflight .
.opencode/bin/llmzk update . --source /path/to/llmzk
.opencode/bin/llmzk update . --source /path/to/llmzk --apply
.opencode/bin/llmzk doctor .
.opencode/bin/llmzk git diff . --stat
.opencode/bin/llmzk git diff .
```
