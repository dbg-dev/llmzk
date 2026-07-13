---
type: candidate_review
status: proposed
mode: ingest
input:
  - "00 Inbox/example.md"
created: YYYY-MM-DD
applied: false
schema_version: 1
---

# Candidate Review - Example

## Source

Input:
- `00 Inbox/example.md`

Mode:
- ingest

## Proposed notes

Edit checkboxes before writing durable notes. Approved `[x]` candidates are eligible to be written; unchecked `[ ]` candidates should not be written.

### Source notes

- [x] `01 Sources/Source - Example.md` — create processed source wrapper.

### Literature notes

- [x] `02 Literature Notes/Literature - Example.md` — create source-specific compression.

### Concept notes

- [x] `04 Concept Notes/Example concept.md` — reusable vocabulary or definition.

### Permanent notes

- [x] `03 Permanent Notes/Example durable claim.md` — claim-shaped note in the user's words.

### Bridge notes

- [ ] `05 Bridge Notes/Example bridge.md` — only approve if this captures a transformation, translation, equivalence, representation shift, or conceptual transfer.

### Contradiction/tension notes

- [ ] `06 Contradiction Notes/Example tension.md` — only approve if this captures a real two-sided tension, trade-off, limitation, ambiguity, or apparent conflict.

### Index notes

- [x] `07 Index Notes/Index - Example.md` — map of the created/updated cluster.

## Deliberately not created

- [ ] `Author name` — author/source metadata, not a concept.
- [ ] `Generic background topic` — too broad or not central to this ingest.

## Reviewer instructions

Before writing durable notes:

- Change `[x]` to `[ ]` to reject a candidate.
- Edit a filename/title to rename a candidate.
- Add a new `[x]` item under the appropriate section to request an extra note.
- Add constraints or instructions under `## Reviewer notes`.

## Reviewer notes

<!-- Add user instructions for the write-approved step here. -->
