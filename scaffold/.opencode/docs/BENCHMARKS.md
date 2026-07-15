# llmzk Benchmarks

`llmzk` benchmarks are regression checks for generated vaults. They do not run an
LLM. They check whether an existing output still satisfies the behaviours the
project cares about.

Use them to catch regressions such as:

- missing central concept notes
- weak or missing bridge/contradiction notes
- forbidden author/model-name stubs
- unresolved or ambiguous durable links
- missing candidate reviews, decision logs, or passports
- known bad wording such as “exponentially worse” for finite differences

## Run

From an installed vault:

```bash
.opencode/bin/llmzk benchmark .opencode/benchmarks --vault .
```

Run one case:

```bash
.opencode/bin/llmzk benchmark .opencode/benchmarks/nielsen-backpropagation --vault .
```

JSON output:

```bash
.opencode/bin/llmzk benchmark .opencode/benchmarks --vault . --json
```

## Structure

Each case lives in a folder with `benchmark.yaml`:

```text
.opencode/benchmarks/
  nielsen-backpropagation/
    benchmark.yaml
  automatic-differentiation-fleeting/
    benchmark.yaml
  reasoning-llms/
    benchmark.yaml
```

The benchmark file should prefer semantic/structural checks over exact full-file
snapshots. It is fine for wording to vary; it is not fine for central concepts,
provenance, or graph hygiene to regress.

## Case schema

Common checks:

```yaml
name: Example
checks:
  required_files:
    - "04 Concept Notes/Example.md"
  forbidden_files:
    - "04 Concept Notes/Author Name.md"
  required_text:
    - path: "04 Concept Notes/Example.md"
      contains:
        - "important phrase"
      contains_any:
        - "acceptable phrase A"
        - "acceptable phrase B"
  forbidden_text:
    - glob: "**/*.md"
      contains:
        - "known bad phrase"
  required_wikilinks:
    - path: "07 Index Notes/Index - Example.md"
      links:
        - "04 Concept Notes/Example|Example"
  review_artifacts:
    candidate_reviews:
      - glob: "Logs/Candidate Reviews/*example*candidate-review.md"
        status: applied
    decision_logs:
      - glob: "Logs/Decision Logs/*example*.md"
    passports:
      - glob: "Logs/Passports/*example*.yaml"
  audit:
    zero:
      - unresolved-links
      - ambiguous-links
      - bad-link-formatting
      - frontmatter-issues
```

## Manual rubric

A case may include `manual_rubric` items. These are printed as warnings and are
for human review, not automated pass/fail. Use them for high-judgement checks
such as whether a bridge note captures a representation shift rather than a mere
association.


## Operating profile

Run benchmarks under the fast operating profile. Benchmarking checks an existing generated vault and should not create, rewrite, or reinterpret durable notes.

## Subfolder-aware benchmark paths

Benchmarks are evaluated from the llmzk instance root. If `.llmzk.yaml` sets a `vault_relative_prefix`, benchmark file paths and wikilinks are canonicalized before comparison.

For example, with:

```yaml
vault_relative_prefix: "AI"
link_style: "vault_relative"
```

these are equivalent for benchmark purposes:

```text
04 Concept Notes/Automatic differentiation.md
AI/04 Concept Notes/Automatic differentiation.md
```

and these link targets are equivalent:

```markdown
[[04 Concept Notes/Automatic differentiation|Automatic differentiation]]
[[AI/04 Concept Notes/Automatic differentiation|Automatic differentiation]]
```

This keeps benchmark expectations stable whether the llmzk instance is installed at the Obsidian vault root or inside a subfolder.
