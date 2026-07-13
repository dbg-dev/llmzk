# llmzk-promote skill

Use for promoting rough notes from `00 Fleeting Notes/` into durable Zettelkasten notes.

This skill decides what the notes should become. For Obsidian Markdown syntax and frontmatter mechanics, rely on the installed `obsidian-markdown` skill.

## Inputs

- one fleeting note, or
- a small related cluster of fleeting notes

## Outputs

In candidate-review mode, create only one candidate review file in `Logs/Candidate Reviews/`.

In write-approved mode, create or update approved items only:

- concept notes in `04 Concept Notes/`
- permanent notes in `03 Permanent Notes/`
- bridge notes in `05 Bridge Notes/`
- contradiction/tension notes in `06 Contradiction Notes/`
- index notes in `07 Index Notes/`
- passport and decision log in `Logs/`

## Required process

1. Read `AGENTS.md`, `.opencode/docs/SOUL.md`, and `.opencode/docs/OBSIDIAN_SKILLS.md`.
2. Inspect the fleeting note or cluster.
3. Produce a candidate inventory.
4. If running in candidate-review mode, write a candidate review file in `Logs/Candidate Reviews/` and stop before durable notes.
5. If running in write-approved mode, read the candidate review and write only approved `[x]` candidates.
6. Classify each candidate as concept, permanent claim, bridge, contradiction/tension, index entry, defer, merge, or archive.
7. Apply `../llmzk-ingest/references/high_judgement_notes_protocol.md` before creating bridge or contradiction/tension notes.
8. Do not force bridge notes or contradiction/tension notes. It is valid to record `No bridge note warranted` or `No durable contradiction/tension note warranted` in the decision log.
9. Do not promote all fleeting notes into concepts.
10. Do not collapse a technical cluster into one mega-note.
11. Use `origin_trail` for notes whose provenance is your own fleeting material rather than an external source.
12. In write-approved mode, write passport and decision log.
13. Run or recommend frontmatter fix + light audit.

## Read these references

- `references/fleeting_promotion_protocol.md`
- `references/promotion_cluster_protocol.md`
- `../llmzk-ingest/references/candidate_inventory_protocol.md`
- `../llmzk-ingest/references/candidate_review_gate_protocol.md`
- `../llmzk-ingest/references/note_writing_protocol.md`
- `../llmzk-ingest/references/high_judgement_notes_protocol.md`
- `../llmzk-ingest/references/frontmatter_protocol.md`
