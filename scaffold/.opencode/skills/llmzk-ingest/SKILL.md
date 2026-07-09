# llmzk-ingest skill

Use for source material in `00 Inbox/`: papers, articles, book chapters, or substantial markdown sources.

This skill is a Zettelkasten workflow. For Obsidian Markdown syntax, properties/frontmatter, wikilinks, embeds, and callouts, rely on the installed `obsidian-markdown` skill. For live vault read/search/create/backlink operations, use `obsidian-cli` where appropriate.

## Inputs

- one source file or a small set of related source files from `00 Inbox/`

## Outputs

Always create or update:

- one source note in `01 Sources/`
- one literature note in `02 Literature Notes/`
- a passport in `Logs/Passports/`
- a decision log in `Logs/Decision Logs/`

Create when warranted:

- concept notes in `04 Concept Notes/`
- permanent notes in `03 Permanent Notes/`
- bridge notes in `05 Bridge Notes/`
- contradiction/tension notes in `06 Contradiction Notes/`
- an index note in `07 Index Notes/`

## Required process

1. Read `AGENTS.md`, `.opencode/docs/SOUL.md`, and `.opencode/docs/OBSIDIAN_SKILLS.md`.
2. Inspect the source.
3. Produce a candidate inventory before writing final notes.
4. Write notes using the templates in `Templates/`.
5. Use the installed `obsidian-markdown` skill for Obsidian syntax details.
6. Use wikilinks with link context.
7. Use MathJax for math.
8. For source notes in `01 Sources/`, use `status: ingested`, not `status: raw`; raw material lives in `00 Inbox/`.
9. When generalising backpropagation equations beyond sigmoid activations, say “differentiable elementwise activation functions” rather than “any activation function.”
10. Write passport and decision log.
11. Run or recommend a light audit.

## Read these llmzk references

- `references/source_ingest_protocol.md`
- `references/candidate_inventory_protocol.md`
- `references/note_writing_protocol.md`
- `references/link_policy.md`
- `references/frontmatter_protocol.md`
- `references/math_formatting_protocol.md`
