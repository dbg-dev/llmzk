# llmzk-audit skill

Use for lightweight structural review of the llmzk vault.

This skill does not replace the installed Obsidian skills. Use `obsidian-markdown` for Obsidian syntax guidance and `obsidian-cli` for live vault inspection. llmzk audit focuses on Zettelkasten-specific structure and local script output.

## Process

1. Run or inspect:

```bash
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_audit.py .
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
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_normalize_links.py . --dry-run
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_fix_frontmatter.py . --apply
```
