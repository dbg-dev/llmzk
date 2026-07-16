# llmzk OpenCode harness

This folder is installed into a concrete Obsidian vault by `scripts/init-vault.sh` from the upstream source repo.

## Contents

```text
commands/       OpenCode slash commands
agents/         Optional specialist agents
skills/         llmzk domain skills
docs/           llmzk operating docs, including operating profiles
bin/llmzk       Wrapper for deterministic tools
llmzk-tools/    Python package for audit, doctor, update, cleanup, candidate review validation, and Git safety
```

## Tool wrapper

Use the wrapper from the vault root:

```bash
.opencode/bin/llmzk audit .
.opencode/bin/llmzk doctor .
.opencode/bin/llmzk update . --source /path/to/llmzk
.opencode/bin/llmzk git preflight .
.opencode/bin/llmzk git diff . --stat
.opencode/bin/llmzk review-validate "Logs/Candidate Reviews/example.md"
```

The wrapper invokes console scripts from `.opencode/llmzk-tools`, whose CLIs use `tyro`. Git-facing commands use `GitPython`.

## Operating profiles

Read `.opencode/docs/OPERATING_PROFILES.md` when choosing task posture:

```text
careful = knowledge creation and write-approved
review  = candidate-review critique before writing
fast    = deterministic cleanup, audit, benchmark, and Git inspection
```

These profiles are instruction overlays, not OpenCode permission modes.

## Candidate review gate

`/llmzk-ingest` and `/llmzk-promote` create candidate review files first. Durable notes are written only by `/llmzk-write-approved <candidate-review-file>`.

## Benchmarks

Run `.opencode/bin/llmzk benchmark .opencode/benchmarks --vault .` to check an existing generated vault against deterministic regression expectations.

## CLI positional arguments

The installed `.opencode/bin/llmzk` wrapper uses Tyro-backed tools whose main path arguments are positional. Common commands should work as:

```bash
.opencode/bin/llmzk audit .
.opencode/bin/llmzk benchmark .opencode/benchmarks --vault .
.opencode/bin/llmzk review validate "Logs/Candidate Reviews/example.md"
.opencode/bin/llmzk git diff . --stat
```

For a path that begins with `-`, use the standard end-of-options separator:

```bash
.opencode/bin/llmzk review validate -- "Logs/Candidate Reviews/-example.md"
```


## Maintenance

See `.opencode/docs/MAINTENANCE.md` for copy-mode and symlink-mode update workflows.
