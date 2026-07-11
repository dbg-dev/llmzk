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
