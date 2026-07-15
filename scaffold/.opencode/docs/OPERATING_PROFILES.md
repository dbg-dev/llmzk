# llmzk Operating Profiles

Operating profiles are instruction overlays for agent behaviour. They are not OpenCode permission modes and they are not just command groupings.

OpenCode controls what the agent is allowed to do. llmzk operating profiles describe what the agent should optimise for while doing a task.

```text
OpenCode plan/build/explore/scout = tool access and execution posture
llmzk operating profiles          = judgement style and quality posture
```

## Careful profile

Use the careful profile when creating or applying knowledge-graph changes:

- `/llmzk-ingest`
- `/llmzk-ingest-candidates`
- `/llmzk-promote`
- `/llmzk-promote-candidates`
- `/llmzk-write-approved`

Optimise for durable understanding.

Rules:

- Prefer fewer, stronger notes over broad coverage.
- Preserve mathematical notation and definitions.
- Produce or use a candidate review before durable writes.
- Avoid author, model, organisation, and source-title concept notes unless they are themselves the subject.
- Bridge notes must capture a transformation, equivalence, translation, or representation shift.
- Contradiction/tension notes must capture a real technical, epistemic, economic, or design trade-off.
- Do not force bridge or contradiction/tension notes.
- When uncertain, defer and record the uncertainty in the candidate review or decision log.
- Respect reviewer checkbox edits and reviewer notes during write-approved.

Failure modes to avoid:

- note sludge from every named entity or background term
- weak bridge notes that only say two ideas are related
- weak contradiction notes that only say notation is difficult
- overconfident generalisations, especially in mathematical notes
- rewriting the user's own ideas into generic summaries

## Review profile

Use the review profile when critiquing a candidate review before notes are written:

- `/llmzk-review-candidates`
- manual review of `Logs/Candidate Reviews/*.md`

Optimise for approval quality.

Rules:

- Do not write durable notes.
- Do not modify the candidate review unless the user explicitly asks.
- Identify missing central concepts or claims.
- Identify weak bridge or contradiction/tension candidates.
- Identify note sludge, duplicate candidates, and author/model/source-title stubs.
- Suggest concrete checkbox edits: keep, reject, rename, merge, defer, or add.
- Suggest reviewer-note wording when useful.
- Preserve uncertainty: recommend deferral when the source does not support a durable note.

A good review answer should help the user decide what to approve before `/llmzk-write-approved`.

## Fast profile

Use the fast profile for deterministic maintenance and checks:

- `/llmzk-audit`
- `/llmzk-fix-frontmatter`
- `/llmzk-normalize-links`
- `/llmzk-review-validate`
- `/llmzk-benchmark`
- Git status/diff/preflight commands

Optimise for mechanical correctness.

Rules:

- Do not create new durable notes.
- Do not reinterpret concepts.
- Do not rewrite prose unless the requested fix is purely mechanical.
- Fix or report frontmatter, link, path, and formatting issues.
- Prefer reporting over guessing.
- Separate raw inbox/fleeting issues from durable graph issues.
- After cleanup, rerun audit and show a concise Git diff summary.

Failure modes to avoid:

- using a cleanup command as an excuse to rewrite content
- silently changing note semantics
- treating raw inbox issues as durable graph failures
- staging, committing, resetting, cleaning, or reverting without explicit user approval

## Pairing with OpenCode modes

A practical pairing is:

```text
OpenCode plan  + llmzk review profile  = critique candidates without writing
OpenCode build + llmzk careful profile = create/write approved notes
OpenCode build + llmzk fast profile    = run deterministic cleanup/audit tools
OpenCode explore/scout                 = inspect vault/docs/external references before deciding
```

When in doubt:

```text
knowledge creation -> careful
candidate critique -> review
mechanical cleanup -> fast
```
