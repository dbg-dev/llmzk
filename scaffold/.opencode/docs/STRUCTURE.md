# llmzk structure

`llmzk` has two separate layers.

## Source repo

The upstream source repo contains:

```text
scripts/init-vault.sh
scaffold/
```

The source repo is not an installed vault and should not contain a top-level `.opencode/` harness.

## Installed vault

The install script creates a concrete vault:

```text
AGENTS.md
opencode.json
.opencode/
Templates/
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

The installed vault is the Git safety boundary.

## Runtime tools

Runtime Python tools live only here:

```text
.opencode/llmzk-tools/
```

That project exposes console scripts via `[project.scripts]`. OpenCode commands invoke them through:

```text
.opencode/bin/llmzk
```

The vault root is deliberately not a Python project.
