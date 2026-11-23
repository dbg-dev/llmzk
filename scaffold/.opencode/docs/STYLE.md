# STYLE.md

Use this file for llmzk writing taste. Use the installed `obsidian-markdown` skill for the full Obsidian Markdown syntax rules.

## General style

- Write newly authored note prose in ASD-STE100 Simplified Technical English, using the applicable edition's writing rules and approved dictionary.
- Use short, direct sentences, active voice, and one clear idea per sentence. Use approved words with their approved meanings and parts of speech.
- Handle necessary technical names and verbs according to the standard. Preserve precise definitions, uncertainty, and mathematical meaning; do not replace a technical term with an inaccurate simplification.
- Preserve direct quotations, source titles, proper names, equations, code, and required link targets exactly. Distinguish quoted source text from newly authored prose.
- Check compliance against the applicable edition of the standard and its dictionary. Do not claim verified compliance without that check; flag uncertainty when the standard is unavailable.
- Prefer bullets for main points.
- Use short paragraphs only when needed.
- Avoid generic AI summary language.
- Keep notes scannable in Obsidian.
- Use callouts sparingly for important, warning, example, or question blocks.
- Do not use callouts as the default container for equations.

## Math

- Use `$...$` for inline math.
- Use `$$...$$` for display math.
- Do not put math in code fences.
- Use code fences only for code, shell commands, YAML, JSON, Mermaid, or literal file content.

## Links

- Use `[[Target]]` and `[[Target|Alias]]` for internal notes.
- Use Markdown links for external URLs.
- Add context to important links.
- Do not link authors, book titles, or paper titles as concept notes unless they are intentionally maintained as source/person notes.

## Frontmatter style

- Frontmatter must be valid YAML.
- In frontmatter, write wikilinks as quoted strings: `"[[Backpropagation]]"`.
- Use `source_trail` for external sources and `origin_trail` for fleeting/internal note origins.
- Never write nested list frontmatter such as `- - - Source - Example`.
- Run `.opencode/bin/llmzk fix-frontmatter . --apply` if frontmatter becomes malformed.
