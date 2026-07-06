# LINT_RULES.md

llmzk linting is intentionally light. It checks Zettelkasten-specific issues and leaves full Obsidian syntax knowledge to the installed `obsidian-markdown` skill.

## Checks

- malformed llmzk frontmatter
- nested frontmatter list artifacts such as `- - -`
- unquoted wikilinks in llmzk frontmatter fields
- missing `source_trail` or `origin_trail` where expected
- unresolved links in durable notes
- raw inbox unresolved links reported separately
- math-like content inside code fences
- empty index notes
- obvious bad link formatting such as `\|`, `.md` suffixes, or project-prefixed links

## Non-goals

- Do not enforce tags.
- Do not create concept stubs automatically.
- Do not turn authors or sources into concepts.
- Do not replace Obsidian's own rendering and property semantics.
