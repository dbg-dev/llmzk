# STYLE.md

Use this file for llmzk writing taste. Use the installed `obsidian-markdown` skill for the full Obsidian Markdown syntax rules.

## General style

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
- Run `uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_fix_frontmatter.py . --apply` if frontmatter becomes malformed.
