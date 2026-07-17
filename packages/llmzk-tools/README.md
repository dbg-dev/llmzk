# llmzk-tools

Deterministic utilities used inside an installed `llmzk` vault.

This directory is the authoritative source package in the llmzk monorepo. `scripts/build-scaffold.py` copies it into `.opencode/llmzk-tools/` when assembling an installed vault, so the vault root itself does not need to be a Python project.

## CLI entry points

The package exposes console scripts:

```bash
llmzk-audit
llmzk-doctor
llmzk-fix-frontmatter
llmzk-git-safety
llmzk-new-run
llmzk-normalize-links
```

The installed vault normally invokes these through the wrapper:

```bash
.opencode/bin/llmzk audit .
.opencode/bin/llmzk doctor .
.opencode/bin/llmzk git preflight .
```

The CLIs use `tyro`. Git-facing operations use `GitPython`.


## v0.5.3.1 fixes

- Audit resolver no longer uses `Path.stem` on raw wikilink targets.
- Review Queue audit reports are regenerated each run.
- Candidate review mark command normalises YAML booleans and ISO timestamps.

## Benchmark

`llmzk-benchmark` checks an existing vault against benchmark YAML files. It does not run an LLM.

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



## Tests

The update/maintenance workflow has unit tests for dry-run/apply behaviour, copy-mode and symlink-mode updates, protected durable folders, and doctor version-metadata checks.

Run from `.opencode/llmzk-tools/`:

```bash
uv run --group dev pytest
```

These tests are intentionally scoped to deterministic tooling. They do not call an LLM and they do not modify durable vault notes.
