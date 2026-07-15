# llmzk-tools

Deterministic utilities used inside an installed `llmzk` vault.

This is the runtime Python project for the installed vault. It intentionally lives under `.opencode/llmzk-tools/` so the vault root does not need to be a Python project.

## CLI entry points

The package exposes console scripts:

```bash
llmzk-audit
llmzk-doctor
llmzk-fix-frontmatter
llmzk-git-safety
llmzk-new-run
llmzk-normalize-links
llmzk-smoke-test
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
