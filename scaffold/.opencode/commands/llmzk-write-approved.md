---
description: Write approved notes from an approved candidate review file
---

Input: `$ARGUMENTS` must be a candidate review file from `Logs/Candidate Reviews/`.

Run Git preflight first:

```bash
.opencode/bin/llmzk git preflight .
```

If preflight reports a dirty working tree, stop unless the user explicitly says to continue. Applying an approved candidate review is a broad write operation.

Validate the candidate review:

```bash
.opencode/bin/llmzk review-validate "$ARGUMENTS"
```

Read the candidate review file carefully. Treat it as the source of truth:

- `[x]` candidates are approved for writing.
- `[ ]` candidates must not be written.
- renamed candidates should be written under the edited name/path.
- extra `[x]` candidates added by the reviewer should be considered approved.
- `## Reviewer notes` are instructions for this apply step.

Use the appropriate skill based on review frontmatter `mode`:

- `mode: ingest` → use `llmzk-ingest` in **write-approved mode**.
- `mode: promote` → use `llmzk-promote` in **write-approved mode**.

During write-approved mode:

1. Write only approved durable notes.
2. Preserve high-judgement quality for bridge and contradiction/tension notes.
3. Write a passport in `Logs/Passports/` referencing the candidate review path.
4. Write a decision log in `Logs/Decision Logs/` summarising accepted, rejected, renamed, and user-added candidates.
5. Mark the candidate review as applied after successful writes:

```bash
.opencode/bin/llmzk review mark "$ARGUMENTS" --status applied
```

Then run:

```bash
.opencode/bin/llmzk fix-frontmatter . --apply
.opencode/bin/llmzk audit .
.opencode/bin/llmzk git diff . --stat
```

End by summarising created/changed files, rejected candidates, the audit result, and the Git diff summary. Do not stage, commit, reset, clean, or revert unless the user explicitly asks.
