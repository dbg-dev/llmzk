---
description: Run llmzk regression benchmark expectations against the vault
---

Run the installed benchmark suite against the current vault:

```bash
.opencode/bin/llmzk benchmark .opencode/benchmarks --vault .
```

Run one case:

```bash
.opencode/bin/llmzk benchmark .opencode/benchmarks/nielsen-backpropagation --vault .
```

This does not call an LLM or regenerate notes. It checks an existing vault against
human-maintained expectations for required notes, forbidden notes, audit hygiene,
review artifacts, and known wording regressions.
