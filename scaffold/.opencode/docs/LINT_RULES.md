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


## Duplicate note-title warning

The audit reports `duplicate-note-titles` when a note basename appears in `00 Fleeting Notes/` and in a durable folder such as `04 Concept Notes/`. This is especially important for promoted notes, because unqualified wikilinks in `origin_trail` can accidentally resolve to the new durable note rather than the original fleeting note. Prefer path-qualified origin links such as `[[00 Fleeting Notes/Automatic differentiation|Automatic differentiation]]`.
