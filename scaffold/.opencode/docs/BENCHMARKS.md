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


## Semantic matching and aliases

Benchmarks should test roles and behaviours, not one brittle filename when several
valid titles are acceptable. Use alias-aware fields for notes whose title may
reasonably vary between model runs:

```yaml
checks:
  required_files:
    - role: forward_mode_ad
      path_any_of:
        - "04 Concept Notes/Forward-mode automatic differentiation.md"
        - "04 Concept Notes/Forward mode automatic differentiation.md"

  required_text:
    - role: distillation_claim
      path_any_of:
        - "03 Permanent Notes/Distillation propagates reasoning capability rather than creating frontier capability.md"
        - "03 Permanent Notes/Distillation is cheap and effective for small models but depends on stronger teacher models.md"
      target_mode: any
      contains_any:
        - "stronger teacher"
        - "teacher model"

  required_wikilinks:
    - path: "07 Index Notes/Index - Reasoning LLMs.md"
      links:
        - target_any_of:
            - "04 Concept Notes/Model distillation|Model distillation"
            - "04 Concept Notes/LLM distillation|LLM distillation"

  review_artifacts:
    candidate_reviews:
      - glob_any_of:
          - "Logs/Candidate Reviews/*automatic*differentiation*candidate-review.md"
          - "Logs/Candidate Reviews/*ad*cluster*candidate-review.md"
        status: applied
```

Supported alias fields:

- `path_any_of`: any one path may satisfy a required file or text target.
- `glob_any_of`: any one glob family may satisfy an artifact or glob check.
- `target_any_of`: any one wikilink target may satisfy an index/provenance link.
- `role`: human-readable label for a semantic expectation.
- `target_mode: any`: for aliased text checks, at least one matching target must
  satisfy the text condition instead of every alias target needing to do so.

Use these sparingly. Aliases are for genuinely equivalent notes, not for hiding
missing concepts.

## Excluding provenance/log folders from broad text checks

Broad text checks can exclude non-durable provenance folders such as `Logs/`:

```yaml
forbidden_text:
  - glob: "**/*.md"
    exclude:
      - "Logs"
    contains:
      - "known bad durable-note wording"
```

Candidate reviews and decision logs can mention rejected wording or reviewer
rationale. Keep durable-note wording checks focused on durable notes unless the
case is explicitly testing log hygiene.

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
