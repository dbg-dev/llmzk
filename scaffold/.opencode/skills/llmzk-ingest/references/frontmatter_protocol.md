# llmzk Frontmatter Protocol

Use the installed `obsidian-markdown` skill as the general authority for Obsidian properties/frontmatter.

This protocol only defines llmzk-specific fields and formatting constraints.

## Required fields

Most llmzk notes should include:

```yaml
---
type: concept
status: seed
---
```

Allowed `type` values:

```text
source
literature
concept
permanent
bridge
contradiction
index
wiki-article
candidate_review
```

Common `status` values:

```text
seed
active
reviewed
synthesized
archived
ingested
partial
deprecated
proposed
edited
applied
rejected
superseded
```

## Provenance fields

For notes derived from external sources:

```yaml
source_trail:
  - "[[Source - Example]]"
```

For notes promoted from your own fleeting notes, path-qualify the origin and use an alias:

```yaml
origin_trail:
  - "[[00 Fleeting Notes/Fleeting note title|Fleeting note title]]"
```

This avoids ambiguous provenance when a durable note has the same basename as the fleeting note.

For bridge and contradiction notes:

```yaml
connects:
  - "[[Concept A]]"
  - "[[Concept B]]"
```

For wiki/article outputs:

```yaml
derived_from:
  - "[[Permanent note]]"
  - "[[Bridge note]]"
```

## Formatting rules

- Quote wikilinks in YAML: `"[[Note title]]"`.
- Use flat lists only.
- Do not create nested list artifacts such as `- - - Note title`.
- Use `origin_trail` rather than empty `source_trail` for promoted fleeting notes.
- Path-qualify `origin_trail` entries from `00 Fleeting Notes/`, for example `"[[00 Fleeting Notes/Automatic differentiation|Automatic differentiation]]"`.
- If no provenance is available, say so in the decision log rather than inventing it.

## Repair command

```bash
.opencode/bin/llmzk fix-frontmatter . --apply
```
