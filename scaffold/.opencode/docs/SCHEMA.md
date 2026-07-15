# SCHEMA.md

This schema defines llmzk-specific properties. For general Obsidian property/frontmatter syntax, rely on the installed `obsidian-markdown` skill.

## Core frontmatter fields

```yaml
type: concept | permanent | bridge | contradiction | index | source | literature | wiki-article | candidate_review
status: seed | active | reviewed | synthesized | archived | ingested | partial | deprecated | proposed | edited | applied | rejected | superseded
schema_version: 1
```

## Provenance fields

Use `source_trail` for external sources:

```yaml
source_trail:
  - "[[Source - Example]]"
```

Use `origin_trail` for promoted fleeting notes or internal notes. When the origin is in `00 Fleeting Notes/`, path-qualify it and use an alias so provenance does not become ambiguous if the promoted durable note has the same title:

```yaml
origin_trail:
  - "[[00 Fleeting Notes/Automatic differentiation|Automatic differentiation]]"
```

Avoid ambiguous origin trails such as `"[[Automatic differentiation]]"` when both a fleeting note and durable concept/permanent note share that basename.

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

## Link disambiguation

If a durable note links to a title that also exists in `00 Fleeting Notes/`, path-qualify the durable target and use an alias:

```markdown
[[04 Concept Notes/Automatic differentiation|Automatic differentiation]]
```

If a wikilink contains a slash, the audit treats it as an exact path. The path may be local to the llmzk instance, or it may include the configured `.llmzk.yaml` `vault_relative_prefix`. Unknown prefixes should be normalised or fixed.

## Mathematical wording

When generalising backpropagation equations beyond sigmoid activations, prefer precise wording such as: “The equations are not specific to sigmoid activations; they apply to differentiable elementwise activation functions, with the activation derivative changed accordingly.” Avoid saying they hold for “any activation function.”

When comparing finite differences with backpropagation, do not describe backpropagation as “exponentially” cheaper or say that backpropagation cost is independent of parameter count. Prefer: “finite differences require work proportional to the number of parameters, while backpropagation computes all gradients with one backward pass through the existing computation graph.”

When describing distillation in reasoning models, avoid overly absolute titles such as “distillation cannot produce the next generation of reasoning models.” Prefer: “distillation propagates reasoning capability rather than creating frontier capability” or “distillation is cheap and effective for small models but depends on stronger teacher models.”


## Candidate review frontmatter

Candidate review files live in `Logs/Candidate Reviews/` and use:

```yaml
type: candidate_review
status: proposed # proposed | edited | applied | rejected | superseded
mode: ingest # ingest | promote
input:
  - "00 Inbox/example.md"
created: "YYYY-MM-DD"
applied: false
schema_version: 1
```

Candidate review files are workflow artifacts, not durable knowledge notes. They are still tracked by Git because they are the approval record for durable writes.

## Note types

- `source`: source metadata and orientation.
- `literature`: source-specific reading note.
- `concept`: reusable vocabulary.
- `permanent`: durable claim in your own words.
- `bridge`: connection between notes.
- `contradiction`: tension, contradiction, trade-off, disagreement.
- `index`: navigational map.
- `wiki-article`: synthesized output.
- `candidate_review`: proposed/approved note candidates used as a pre-write review gate.
