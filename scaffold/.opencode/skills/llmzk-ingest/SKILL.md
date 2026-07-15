# llmzk-ingest skill

Use for source material in `00 Inbox/`: papers, articles, book chapters, or substantial markdown sources.

This skill is a Zettelkasten workflow. For Obsidian Markdown syntax, properties/frontmatter, wikilinks, embeds, and callouts, rely on the installed `obsidian-markdown` skill. For live vault read/search/create/backlink operations, use `obsidian-cli` where appropriate.

## Operating profile

Use the **careful operating profile** from `.opencode/docs/OPERATING_PROFILES.md` for both candidate-review mode and write-approved mode.

## Inputs

- one source file or a small set of related source files from `00 Inbox/`

## Outputs

In candidate-review mode, create only:

- one candidate review file in `Logs/Candidate Reviews/`

In write-approved mode, create or update approved items only:

- source notes in `01 Sources/`
- literature notes in `02 Literature Notes/`
- a passport in `Logs/Passports/`
- a decision log in `Logs/Decision Logs/`

Create approved notes when warranted:

- concept notes in `04 Concept Notes/`
- permanent notes in `03 Permanent Notes/`
- bridge notes in `05 Bridge Notes/`
- contradiction/tension notes in `06 Contradiction Notes/`
- an index note in `07 Index Notes/`

## Required process

1. Read `AGENTS.md`, `.opencode/docs/SOUL.md`, and `.opencode/docs/OBSIDIAN_SKILLS.md`.
2. Inspect the source.
3. Produce a candidate inventory.
4. If running in candidate-review mode, write a candidate review file in `Logs/Candidate Reviews/` and stop before durable notes.
5. If running in write-approved mode, read the candidate review and write only approved `[x]` candidates using the templates in `Templates/`.
6. Use the installed `obsidian-markdown` skill for Obsidian syntax details.
7. Use wikilinks with link context.
8. Use MathJax for math.
9. Apply `references/high_judgement_notes_protocol.md` before creating bridge or contradiction/tension notes.
10. Do not force bridge notes or contradiction/tension notes. It is valid to record `No bridge note warranted` or `No durable contradiction/tension note warranted` in the decision log.
11. For source notes in `01 Sources/`, use `status: ingested`, not `status: raw`; raw material lives in `00 Inbox/`.
12. When generalising backpropagation equations beyond sigmoid activations, say “differentiable elementwise activation functions” rather than “any activation function.”
13. Preserve exact candidate filenames in passports and decision logs. Do not retype abbreviations from memory; for example, keep `JVP`, not `JJP`.
14. In write-approved mode, write passport and decision log.
15. Run or recommend a light audit.

## Read these llmzk references

- `references/source_ingest_protocol.md`
- `references/candidate_inventory_protocol.md`
- `references/candidate_review_gate_protocol.md`
- `references/note_writing_protocol.md`
- `references/high_judgement_notes_protocol.md`
- `references/link_policy.md`
- `references/frontmatter_protocol.md`
- `references/math_formatting_protocol.md`
