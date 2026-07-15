---
description: Critique a candidate review before approved notes are written
---

Use the **review operating profile** from `.opencode/docs/OPERATING_PROFILES.md`.

Input: `$ARGUMENTS` should be a candidate review file in `Logs/Candidate Reviews/`.

First validate the file mechanically:

```bash
.opencode/bin/llmzk review-validate "$ARGUMENTS"
```

Then read the candidate review and critique it. Do **not** write durable notes. Do **not** edit the file unless the user explicitly asks.

Assess:

- missing central concepts, permanent claims, bridges, contradictions/tensions, or index notes
- weak bridge candidates that only state loose relatedness
- weak contradiction/tension candidates that only state pedagogical difficulty
- note-sludge candidates such as authors, model names, source titles, or generic background terms
- duplicate candidates or candidates that should be merged
- candidates that should be deferred because the source does not support them
- reviewer notes that should be added before `/llmzk-write-approved`

Return concise recommendations grouped as:

```text
Keep
Reject
Rename / merge
Consider adding
Reviewer notes to add
Risks before write-approved
```

End with the next command:

```text
/llmzk-write-approved <candidate-review-file>
```

only if the review looks ready to apply.
