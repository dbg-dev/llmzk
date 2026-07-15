---
description: Propose candidate Zettelkasten notes for an inbox source without writing approved notes
---

Use the **careful operating profile** from `.opencode/docs/OPERATING_PROFILES.md`.
Run Git preflight first:

```bash
.opencode/bin/llmzk git preflight .
```

If preflight reports a dirty working tree, stop unless the user explicitly says to continue with mixed changes.

Use the `llmzk-ingest` skill on `$ARGUMENTS`, but run it in **candidate-review mode**:

- inspect the source
- produce a candidate inventory
- write exactly one candidate review file in `Logs/Candidate Reviews/`
- do **not** write approved notes in `01 Sources/` through `08 Wiki Articles/`
- do **not** write passport or decision log yet, except if explicitly needed as placeholders

Use `Templates/candidate-review.md` as the form. Include proposed source, literature, concept, permanent, bridge, contradiction/tension, and index notes. Include deliberately-not-created candidates and reviewer notes.

After the candidate review file is written, run:

```bash
.opencode/bin/llmzk review-validate "Logs/Candidate Reviews/<candidate-review-file>.md"
.opencode/bin/llmzk git diff . --stat
```

End by telling the user to edit checkboxes / reviewer notes and then run `/llmzk-write-approved <candidate-review-file>`.
