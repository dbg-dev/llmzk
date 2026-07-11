---
description: Ingest a source from 00 Inbox into the Zettelkasten
---

Run Git preflight first:

```bash
.opencode/bin/llmzk git preflight .
```

If preflight reports a dirty working tree, stop before broad writes unless the user explicitly says to continue with mixed changes.

Use the `llmzk-ingest` skill on `$ARGUMENTS`.

Use installed Obsidian skills for Obsidian mechanics:

- `obsidian-markdown` for Markdown, wikilinks, frontmatter/properties, callouts, embeds, and MathJax-bearing notes.
- `obsidian-cli` only when live vault read/search/create/backlink operations are useful.

Follow the candidate inventory phase before writing final notes.

After notes are written, run:

```bash
.opencode/bin/llmzk fix-frontmatter . --apply
.opencode/bin/llmzk audit .
.opencode/bin/llmzk git diff . --stat
```

End by summarising created/changed files and the audit result. Do not stage, commit, reset, clean, or revert unless the user explicitly asks.
