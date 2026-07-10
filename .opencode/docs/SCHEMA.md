# SCHEMA.md

This schema defines llmzk-specific properties. For general Obsidian property/frontmatter syntax, rely on the installed `obsidian-markdown` skill.

## Core frontmatter fields

```yaml
type: concept | permanent | bridge | contradiction | index | source | literature | wiki-article
status: seed | active | reviewed | synthesized | archived | ingested | partial | deprecated
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

## Status conventions

Use status values narrowly. In particular:

- `00 Inbox/` contains raw material and usually does not need llmzk frontmatter.
- source notes in `01 Sources/` should use `status: ingested` once wrapped as source notes.
- source notes may use `status: partial` if only partly processed.
- source notes may use `status: deprecated` if superseded by another source note.
- concept, permanent, bridge, contradiction, and index notes usually use `seed`, `active`, or `reviewed`.
- synthesized article outputs may use `synthesized`.

Do not use `status: raw` for processed source notes in `01 Sources/`; raw material lives in `00 Inbox/`.

## Mathematical wording

When generalising backpropagation equations beyond sigmoid activations, prefer precise wording such as: “The equations are not specific to sigmoid activations; they apply to differentiable elementwise activation functions, with the activation derivative changed accordingly.” Avoid saying they hold for “any activation function.”

## Note types

- `source`: source metadata and orientation.
- `literature`: source-specific reading note.
- `concept`: reusable vocabulary.
- `permanent`: durable claim in your own words.
- `bridge`: connection between notes.
- `contradiction`: tension, contradiction, trade-off, disagreement.
- `index`: navigational map.
- `wiki-article`: synthesized output.
