---
description: Safely ingest an inbox source by first creating a candidate review
---

This command is safe-by-default. It is an alias for `/llmzk-ingest-candidates`.

Run `/llmzk-ingest-candidates $ARGUMENTS`.

Do not write durable notes directly from `/llmzk-ingest`. Durable notes are written only by `/llmzk-write-approved <candidate-review-file>` after the user reviews the candidate file.
