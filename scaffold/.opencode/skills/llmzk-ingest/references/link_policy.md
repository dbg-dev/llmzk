# llmzk Link Policy

Use the installed `obsidian-markdown` skill as the syntax authority for Obsidian links.

llmzk adds these Zettelkasten rules:

## Internal links

Use Obsidian wikilinks for internal vault notes:

```markdown
[[Backpropagation]]
[[Vector-Jacobian Product (VJP)|VJP]]
```

Use links with context in note bodies:

```markdown
- [[Neuron error delta]] — defines the local error signal used by the recurrence.
```

## Path-qualified links

Path-qualified wikilinks are allowed when they are vault-relative and point to an existing note:

```markdown
[[04 Concept Notes/Automatic differentiation|Automatic differentiation]]
[[00 Fleeting Notes/Automatic differentiation|Automatic differentiation]]
```

If a wikilink target contains a slash, it is treated as an exact vault-relative path. Do not include temporary project prefixes such as `test/`, local repo names, or external folder paths:

```markdown
# Bad
[[test/04 Concept Notes/Automatic differentiation]]

# Good
[[04 Concept Notes/Automatic differentiation|Automatic differentiation]]
```

When a title exists both in `00 Fleeting Notes/` and a durable note folder, path-qualify links from durable notes to the durable target. This avoids Obsidian ambiguity while keeping the alias readable.

## External links

Use standard Markdown links for external URLs:

```markdown
[Nielsen chapter](http://neuralnetworksanddeeplearning.com/chap2.html)
```

## Frontmatter links

Quote wikilinks in YAML frontmatter:

```yaml
source_trail:
  - "[[Source - Example]]"
connects:
  - "[[Concept A]]"
  - "[[Concept B]]"
```

## Avoid

```markdown
[[Target\|Alias]]
[[Target.md]]
[[test/04 Concept Notes/Target]]
```

Use the normalizer for obvious formatting issues:

```bash
.opencode/bin/llmzk normalize-links . --dry-run
.opencode/bin/llmzk normalize-links . --apply
```

## Do not create stubs blindly

Unresolved links are not automatically concepts. Classify them first:

- concept candidate
- source candidate
- person/author candidate
- typo or bad link
- intentionally deferred
