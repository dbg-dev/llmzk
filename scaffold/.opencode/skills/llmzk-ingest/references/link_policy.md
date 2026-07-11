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
[[005-projects/some/path/Target]]
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
