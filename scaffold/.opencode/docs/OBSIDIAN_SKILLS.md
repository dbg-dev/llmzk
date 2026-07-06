# Obsidian Skills Integration

`llmzk` assumes `kepano/obsidian-skills` is installed in OpenCode.

This file explains how llmzk should compose with those skills rather than duplicate them.

## Skills to rely on

### obsidian-markdown

Use for:

- Obsidian Flavored Markdown
- wikilinks
- embeds
- callouts
- frontmatter/properties
- internal vs external link style
- MathJax-bearing Markdown notes

llmzk should not maintain a full copy of Obsidian Markdown rules. When in doubt, use the installed `obsidian-markdown` skill as the syntax authority.

### obsidian-cli

Use for live vault operations when Obsidian is open:

- read notes
- create notes
- search vault content
- append to notes
- inspect backlinks
- set properties
- verify rendering where useful

The Python scripts remain useful for offline mechanical checks. The CLI skill is useful when the agent needs live vault context.

## llmzk-specific responsibilities

llmzk is responsible for Zettelkasten semantics:

- source notes
- literature notes
- concept notes
- permanent notes
- bridge notes
- contradiction/tension notes
- index notes
- candidate inventories
- passports
- decision logs

## Frontmatter boundary

The Obsidian skills know general frontmatter/property syntax.

llmzk adds domain-specific fields:

```yaml
type: concept
status: seed
source_trail:
  - "[[Source - Example]]"
origin_trail:
  - "[[Fleeting note title]]"
connects:
  - "[[Concept A]]"
  - "[[Concept B]]"
```

Always quote wikilinks in YAML values.

## Link boundary

Use Obsidian wikilinks for internal vault links:

```markdown
[[Backpropagation]]
[[Vector-Jacobian Product (VJP)|VJP]]
```

Use Markdown links for external URLs:

```markdown
[Nielsen chapter](http://neuralnetworksanddeeplearning.com/chap2.html)
```

## Audit boundary

Obsidian skills help write valid Obsidian notes.

llmzk scripts check Zettelkasten-specific invariants:

- missing source trails
- malformed llmzk frontmatter
- unresolved durable links
- empty index notes
- math mistakenly placed in code fences
- raw inbox links reported separately
