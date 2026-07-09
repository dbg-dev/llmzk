---
description: Ingest a source from 00 Inbox into the Zettelkasten
---

Run Git preflight first:

```bash
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_git_safety.py preflight .
```

If preflight reports a dirty working tree, stop before broad writes unless the user explicitly says to continue with mixed changes.

Use the `llmzk-ingest` skill on `$ARGUMENTS`.

Use installed Obsidian skills for Obsidian mechanics:

- `obsidian-markdown` for Markdown, wikilinks, frontmatter/properties, callouts, embeds, and MathJax-bearing notes.
- `obsidian-cli` only when live vault read/search/create/backlink operations are useful.

Follow the candidate inventory phase before writing final notes.

After notes are written, run:

```bash
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_fix_frontmatter.py . --apply
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_audit.py .
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_git_safety.py diff . --stat
```

End by summarising created/changed files and the audit result. Do not stage, commit, reset, clean, or revert unless the user explicitly asks.
