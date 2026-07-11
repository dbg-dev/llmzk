# llmzk source repo instructions

This repository is the upstream `llmzk` source repo, not an installed Obsidian vault.

Do not run installed-vault commands such as `/llmzk-ingest` in this source repo. Installed vault assets live under `scaffold/`.

## Boundaries

- `scripts/init-vault.sh` creates a concrete installed vault from `scaffold/`.
- `scaffold/AGENTS.md`, `scaffold/opencode.json`, `scaffold/.opencode/`, and `scaffold/Templates/` are copied or symlinked into installed vaults.
- `scaffold/.opencode/llmzk-tools/` is the only Python project used at runtime in an installed vault.
- The installed vault, not this source repo, is the Git safety boundary for generated notes and logs.

When changing installed-vault behaviour, edit files under `scaffold/`.
When changing installation behaviour, edit `scripts/init-vault.sh`.
