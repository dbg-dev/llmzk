# llmzk-promote skill

Use for promoting rough notes from `00 Fleeting Notes/` into durable Zettelkasten notes.

This skill decides what the notes should become. For Obsidian Markdown syntax and frontmatter mechanics, rely on the installed `obsidian-markdown` skill.

## Inputs

- one fleeting note, or
- a small related cluster of fleeting notes

## Outputs

Create or update only what is warranted:

- concept notes in `04 Concept Notes/`
- permanent notes in `03 Permanent Notes/`
- bridge notes in `05 Bridge Notes/`
- contradiction/tension notes in `06 Contradiction Notes/`
- index notes in `07 Index Notes/`
- passport and decision log in `Logs/`

## Required process

1. Read `AGENTS.md`, `.opencode/docs/SOUL.md`, and `.opencode/docs/OBSIDIAN_SKILLS.md`.
2. Inspect the fleeting note or cluster.
3. Produce a candidate inventory before writing final notes.
4. Classify each candidate as concept, permanent claim, bridge, contradiction/tension, index entry, defer, merge, or archive.
5. Do not promote all fleeting notes into concepts.
6. Do not collapse a technical cluster into one mega-note.
7. Use `origin_trail` for notes whose provenance is your own fleeting material rather than an external source.
8. Write passport and decision log.
9. Run or recommend frontmatter fix + light audit.

## Read these references

- `references/fleeting_promotion_protocol.md`
- `references/promotion_cluster_protocol.md`
- `../llmzk-ingest/references/candidate_inventory_protocol.md`
- `../llmzk-ingest/references/note_writing_protocol.md`
- `../llmzk-ingest/references/frontmatter_protocol.md`
