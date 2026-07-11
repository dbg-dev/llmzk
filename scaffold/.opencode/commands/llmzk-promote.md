---
description: Promote selected fleeting notes into durable Zettelkasten notes
---

Run Git preflight first:

```bash
.opencode/bin/llmzk git preflight .
```

If preflight reports a dirty working tree, stop before broad writes unless the user explicitly says to continue with mixed changes.

Use the `llmzk-promote` skill on `$ARGUMENTS`.

Use installed `obsidian-markdown` for Obsidian syntax. Classify fleeting notes before promoting. Do not convert all fleeting notes into concept notes.

After notes are written, run:

```bash
.opencode/bin/llmzk fix-frontmatter . --apply
.opencode/bin/llmzk audit .
.opencode/bin/llmzk git diff . --stat
```

End by summarising created/changed files and the audit result. Do not stage, commit, reset, clean, or revert unless the user explicitly asks.
