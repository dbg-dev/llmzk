# Candidate Review Gate Protocol

The candidate review gate is the approval boundary before durable note writes.

## Workflow

```text
source or fleeting material
→ candidate review file
→ user edits/approves/rejects candidates
→ write approved notes
→ audit
→ Git diff
```

## Candidate review file

Create candidate reviews in:

```text
Logs/Candidate Reviews/
```

Use `Templates/candidate-review.md` as the form.

Naming convention:

```text
Logs/Candidate Reviews/YYYY-MM-DD-<slug>-candidate-review.md
```

Candidate review frontmatter:

```yaml
type: candidate_review
status: proposed
mode: ingest # or promote
input:
  - "00 Inbox/example.md"
created: "YYYY-MM-DD"
applied: false
schema_version: 1
```

Allowed statuses:

```text
proposed
edited
applied
rejected
superseded
```

## Candidate review mode

When a command asks for candidates, do not write approved notes.

Allowed writes:

- one candidate review file in `Logs/Candidate Reviews/`
- no durable notes in `01 Sources/` through `08 Wiki Articles/`
- no passport or decision log unless explicitly requested as a placeholder

## Write-approved mode

When a command asks to write approved notes from a candidate review:

- treat the candidate review as the source of truth
- write `[x]` candidates only
- do not write `[ ]` candidates
- respect renamed candidate paths/titles
- consider extra `[x]` candidates added by the reviewer
- follow `## Reviewer notes`
- write passport and decision log
- mark and normalize the candidate review as applied after successful writes

## Exact filename preservation

When writing passports and decision logs, preserve candidate review paths and filenames exactly. Do not retype technical abbreviations from memory. For example, keep `Jacobian-Vector Product (JVP)`, not `Jacobian-Vector Product (JJP)`.

## Decision log requirements after write-approved

The decision log should include:

```markdown
## Candidate review used

- `Logs/Candidate Reviews/...md`

## Accepted candidates

- ...

## Rejected candidates

- ...

## Reviewer edits

- Renamed, added, removed, or constrained candidates.
```

## Passport requirements after write-approved

The passport should include the candidate review path, for example:

```yaml
candidate_review: "Logs/Candidate Reviews/2026-07-13-example-candidate-review.md"
```

## High-judgement candidates

Bridge and contradiction/tension candidates must still pass `high_judgement_notes_protocol.md`.

Weak bridge or contradiction candidates should be unchecked by default and explained under `Deliberately not created` or reviewer notes.
