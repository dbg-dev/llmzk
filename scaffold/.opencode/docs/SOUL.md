# SOUL.md

`llmzk` exists to help build a personal Zettelkasten, not a generic AI wiki.

## Objective

Create a durable, inspectable note graph from two inputs:

- source material in `00 Inbox/`;
- personal rough notes in `00 Fleeting Notes/`.

## Core principle

The system should produce useful Zettelkasten notes, not merely summaries.

## Good output

Good output has:

- source notes that preserve provenance;
- literature notes that compress one source;
- concept notes that stabilize vocabulary;
- permanent notes that make durable claims;
- bridge notes that explain meaningful connections;
- contradiction notes that preserve tensions and trade-offs;
- index notes that make the graph navigable;
- passports and decision logs that explain what happened.

## Operating taste

- Prefer a few good notes over many weak notes.
- Do not collapse a technical cluster into one oversized concept note.
- Do not turn every unresolved link into a concept note.
- Do not create author/person notes as concepts.
- Do not synthesize wiki articles directly from raw sources.
- Use candidate inventories before writing final notes.
- Use Obsidian wikilinks and MathJax cleanly.
- Use Python scripts for mechanical checks, not Zettelkasten judgement.

## Boundaries

- `obsidian-skills` handles Obsidian mechanics.
- `llmzk` handles Zettelkasten judgement.
- `.opencode/llmzk-tools` handles deterministic audit/normalization utilities.
