# SCHEMA.md

This schema defines llmzk-specific properties. For general Obsidian property/frontmatter syntax, rely on the installed `obsidian-markdown` skill.

## Core frontmatter fields

```yaml
type: concept | permanent | bridge | contradiction | index | source | literature | wiki-article
status: raw | seed | active | reviewed | synthesized | archived
schema_version: 1
```

## Provenance fields

Use `source_trail` for external sources:

```yaml
source_trail:
  - "[[Source - Example]]"
```

Use `origin_trail` for promoted fleeting notes or internal notes:

```yaml
origin_trail:
  - "[[Automatic differentiation]]"
```

Use `connects` for bridge and contradiction notes:

```yaml
connects:
  - "[[Concept A]]"
  - "[[Concept B]]"
```

Use `derived_from` for synthesized wiki/article outputs:

```yaml
derived_from:
  - "[[Permanent note]]"
  - "[[Bridge note]]"
```

All wikilinks in frontmatter must be quoted strings of the form `"[[...]]"`.
Do not use nested YAML list syntax such as `- - - Source`.

## Note types

- `source`: source metadata and orientation.
- `literature`: source-specific reading note.
- `concept`: reusable vocabulary.
- `permanent`: durable claim in your own words.
- `bridge`: connection between notes.
- `contradiction`: tension, contradiction, trade-off, disagreement.
- `index`: navigational map.
- `wiki-article`: synthesized output.
