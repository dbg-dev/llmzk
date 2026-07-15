---
description: Safely ingest an inbox source by first creating a candidate review
---

Use the **careful operating profile** from `.opencode/docs/OPERATING_PROFILES.md`.
This command is safe-by-default. It is an alias for `/llmzk-ingest-candidates`.

Run `/llmzk-ingest-candidates $ARGUMENTS`.

Do not write approved notes directly from `/llmzk-ingest`. Durable notes are written only by `/llmzk-write-approved <candidate-review-file>` after the user reviews the candidate file.
