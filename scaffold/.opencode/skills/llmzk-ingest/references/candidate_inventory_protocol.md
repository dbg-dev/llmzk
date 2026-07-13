# Candidate Inventory Protocol

Before writing durable notes, produce a candidate inventory. In v5.3 this inventory is normally materialised as a candidate review file in `Logs/Candidate Reviews/` before any durable note writes. During write-approved mode, the final decision log should record the accepted/rejected version of the inventory.

## Inventory sections

```markdown
## Candidate inventory

### Concept notes to create or update
- `[[...]]` — why this is a reusable concept.

### Permanent notes to create or update
- `[[...]]` — claim and why it is durable.

### Bridge notes to create or update
- `[[...]]` — what ideas it connects, what transformation/translation it captures, and why this is not just an ordinary relationship.
- If none are warranted: `No bridge note warranted — ...`.

### Contradiction/tension notes to create or update
- `[[...]]` — what two-sided tension, trade-off, limitation, or apparent conflict it preserves, and why it is durable.
- If none are warranted: `No durable contradiction/tension note warranted — ...`.

### Index notes to create or update
- `[[...]]` — why an index is warranted.

### Notes deliberately not created
- `...` — reason.

### Uncertainties
- ...
```

## Selection rules

- Prefer atomic notes.
- Do not collapse a technical cluster into one mega-note.
- Do not create every possible note.
- Create concept notes for reusable vocabulary.
- Create permanent notes for claims.
- Create bridge notes only for meaningful transformations, translations, equivalences, representation shifts, or conceptual transfers.
- Do not create bridge notes for ordinary relationships; use index notes or link context instead.
- Create contradiction notes only for real two-sided tensions, trade-offs, disagreements, limitations, ambiguities, or apparent conflicts.
- Do not force contradiction notes; weak tensions should be folded into literature notes, concept caveats, or decision-log non-created notes.
- Create an index note when the source opens or updates a topic area.
- Before finalising bridge or contradiction candidates, apply `high_judgement_notes_protocol.md`.


## Candidate review gate

For `/llmzk-ingest-candidates` and `/llmzk-promote-candidates`, the candidate inventory must be written into a candidate review file and the workflow must stop before durable notes are created.

For `/llmzk-write-approved`, the approved `[x]` items in the candidate review file are the source of truth. Unchecked `[ ]` candidates must not be written.
