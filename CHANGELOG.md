# Changelog

## v5.4

- Added deterministic regression benchmark tool: `llmzk-benchmark`.
- Added `/llmzk-benchmark` OpenCode command and wrapper support: `.opencode/bin/llmzk benchmark`.
- Added installed benchmark cases for Nielsen backpropagation, AD fleeting-note promotion, and reasoning LLMs.
- Added benchmark documentation under `.opencode/docs/BENCHMARKS.md`.
- Benchmarks check required/forbidden notes, audit cleanliness, candidate-review/decision-log/passport traces, known bad wording, and high-judgement manual rubrics.

## v5.3.3 — path-qualified link audit and duplicate-title cleanup

- Fixed audit resolution for path-qualified wikilinks: links with slashes now must resolve as exact vault-relative paths.
- Added `ambiguous-links` audit report for durable-note links to titles that also exist in `00 Fleeting Notes/`.
- Updated link normalization to remove accidental project/test prefixes while preserving valid vault-relative folders.
- Updated link normalization to path-qualify durable links when a title is duplicated between fleeting and durable notes.
- Added smoke tests for `test/04 Concept Notes/...` path bugs and ambiguous duplicate-title links.
- Clarified link policy and schema guidance for path-qualified links.
- Added guidance to avoid `JJP` typo in JVP-related passports/decision logs by preserving exact candidate filenames.

## v5.3.2 — provenance and wording cleanup

- Path-qualified `origin_trail` entries from `00 Fleeting Notes/` during frontmatter cleanup.
- Added `duplicate-note-titles` audit report for fleeting/durable basename collisions.
- Preserved frontmatter during body link normalization so provenance paths are not stripped.
- Added candidate-review `normalize` command and run it after `mark` in `/llmzk-write-approved`.
- Normalized candidate-review booleans and date/timestamp strings consistently.
- Tightened wording guidance for finite differences vs backpropagation cost.
- Softened reasoning-model distillation contradiction wording guidance.


## v5.3.1 — audit and review-gate bugfixes

- Fixed unresolved-link false positives for note titles containing periods such as `w.r.t.`.
- Regenerated audit Review Queue files from scratch each audit run to avoid stale reports.
- Normalised candidate review frontmatter booleans and timestamps when marking reviews.
- Renamed source-note `Candidate notes` sections to `Derived notes` after the candidate-review gate.
- Added finite-difference/backpropagation wording guidance to avoid incorrect “exponentially cheaper/worse” claims.


## v5.3 — Candidate review gate

- Added candidate review gate for ingest and promote workflows.
- Added `Logs/Candidate Reviews/` to installed vaults.
- Added `Templates/candidate-review.md`.
- Added safe candidate commands: `/llmzk-ingest-candidates` and `/llmzk-promote-candidates`.
- Changed `/llmzk-ingest` and `/llmzk-promote` into safe aliases that create candidate reviews only.
- Added `/llmzk-write-approved` to write durable notes from approved `[x]` candidates.
- Added `/llmzk-review-validate` and `llmzk-review` deterministic validation/marking tool.
- Updated ingest/promote skills with candidate-review mode and write-approved mode.
- Kept synthesis out of scope for this review gate.

## v5.2.1 — Bash init + scaffold-owned tools cleanup

- Replaced the root Python `llmzk-init` package with `scripts/init-vault.sh`.
- Removed root `src/llmzk`, root `pyproject.toml`, root `.python-version`, and root `uv.lock` from the source-repo design.
- Kept the source repo as scaffold + install script, not a partially installed vault.
- Added root `AGENTS.md` explaining source-repo vs installed-vault boundaries.
- Moved all installed-vault deterministic tools into `scaffold/.opencode/llmzk-tools/src/llmzk_tools/`.
- Converted `scaffold/.opencode/llmzk-tools` into a real Python package with `[project.scripts]` entries.
- Added `.opencode/bin/llmzk` wrapper so command files do not need raw `uv run --project ...` commands.
- Updated OpenCode command files to call the wrapper.
- Kept `tyro` as the CLI layer for scaffold tools.
- Kept `GitPython` as the Git layer for scaffold tools.
- Kept the high-judgement bridge/contradiction skill improvements from v5.2.

## v5.2 — Tyro + GitPython migration

- Migrated upstream Python CLIs toward `tyro` and `GitPython`.
- Added source status and activation-function wording fixes.

## v5.1 — Git safety hardening

- Added `llmzk-doctor`.
- Added Git safety command set.
- Strengthened broad-write preflight guidance.

## v5 — OpenCode init + Git safety architecture

- Split upstream repo from installed vault.
- Added scaffold-based install model.
