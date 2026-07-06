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
```

Common `status` values:

```text
raw
seed
active
reviewed
synthesized
archived
```

## Provenance fields

For notes derived from external sources:

```yaml
source_trail:
  - "[[Source - Example]]"
```

For notes promoted from your own fleeting notes:

```yaml
origin_trail:
  - "[[Fleeting note title]]"
```

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
- If no provenance is available, say so in the decision log rather than inventing it.

## Repair command

```bash
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_fix_frontmatter.py . --apply
```
