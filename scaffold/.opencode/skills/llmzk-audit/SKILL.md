# llmzk-audit skill

Use for lightweight structural review of the llmzk vault.

This skill does not replace the installed Obsidian skills. Use `obsidian-markdown` for Obsidian syntax guidance and `obsidian-cli` for live vault inspection. llmzk audit focuses on Zettelkasten-specific structure and local script output.

## Operating profile

Use the **fast operating profile** from `.opencode/docs/OPERATING_PROFILES.md`. Audit and cleanup are mechanical; do not reinterpret concepts or create durable notes.

## Process

1. Run or inspect:

```bash
.opencode/bin/llmzk audit .
```

2. Review files in `Logs/Review Queue/`.
3. Distinguish raw inbox issues from durable note-graph issues.
4. Recommend targeted fixes only.

## Checks

- malformed llmzk frontmatter
- missing source trails / origin trails
- unresolved durable links
- raw inbox unresolved links, separated from durable graph links
- math inside code fences
- empty index notes
- obvious link-formatting problems

## Related commands

```bash
.opencode/bin/llmzk normalize-links . --dry-run
.opencode/bin/llmzk fix-frontmatter . --apply
```
