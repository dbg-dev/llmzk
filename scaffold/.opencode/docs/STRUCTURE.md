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
.llmzk.yaml
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
  Candidate Reviews/
  Decision Logs/
  Passports/
  Review Queue/
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

## Candidate review gate

Ingest and promote workflows write candidate review artifacts to `Logs/Candidate Reviews/` first. Durable notes are written only after `/llmzk-write-approved` consumes an approved candidate review.


## Operating profiles

See `.opencode/docs/OPERATING_PROFILES.md` for the careful, review, and fast instruction overlays used by commands and skills.


## Multi-instance installs

An llmzk instance may live inside a subfolder of a larger Obsidian vault. In that case `.llmzk.yaml` records the `vault_relative_prefix` and `link_style`. See `.opencode/docs/MULTI_INSTANCE.md`.


## Maintenance boundary

Updates operate on the system layer only: `AGENTS.md`, `opencode.json`, `.gitignore`, `.llmzk.yaml` metadata, `.opencode/`, and `Templates/`. Durable note folders and `Logs/` are vault-owned and must not be touched by scaffold updates. See `.opencode/docs/MAINTENANCE.md`.
