# v5.6.1 — Update workflow unit tests

- Added pytest unit tests for the v5.6 maintenance/update code path.
- Covered dry-run behaviour, copy-mode updates, symlink-mode updates, protected durable folders, dirty-Git blocking, and doctor update metadata checks.
- Added a dev dependency group for pytest and documented the test command.
- Fixed `.llmzk.yaml` scalar writing so YAML document-end markers are not emitted between fields.

# v5.6 — maintenance and update workflow

- Added `scripts/update-vault.sh` for updating an installed vault from the upstream scaffold.
- Added `.opencode/bin/llmzk update` / `llmzk-update` for dry-run drift detection and system-layer updates.
- Added `.opencode/docs/MAINTENANCE.md` with copy-mode and symlink-mode update guidance.
- Added version/install metadata to `.llmzk.yaml`: `installed_version`, `install_mode`, and `source_path`.
- Extended doctor checks for version mismatch, install-mode consistency, source-path availability, and update-tool registration.
- Kept updates limited to system paths; durable notes and `Logs/` are not touched.

# Changelog

## v5.5.4 - Semantic benchmark matching

- Added alias-aware benchmark expectations: `path_any_of`, `glob_any_of`, and `target_any_of`.
- Added `role` labels and `target_mode: any` for semantic checks where several filenames are acceptable.
- Added `exclude`/`exclude_globs` support for broad text checks, so durable-note wording checks can ignore provenance logs.
- Updated installed benchmark cases to avoid hard-coding one exact note title when generated alternatives are substantively equivalent.
- Kept benchmarks read-only: they still check existing vault output and do not call an LLM or rewrite notes.

## v5.5.3 - Benchmark glob hygiene

- Fixed benchmark globs so broad patterns only return readable files.
- Excluded directories, `.git`, `.venv`, cache folders, `node_modules`, and macOS metadata from benchmark glob matches.
- Prevented text/artifact checks from calling `read_text()` on directories or repository internals.
- Added a smoke test for broad benchmark globs such as `**/*`.

## v5.5.2 - CLI positional-argument ergonomics

- Mark vault paths, review files, benchmark paths, passports, and new-run arguments as Tyro positional arguments.
- Keeps common commands such as `.opencode/bin/llmzk audit .`, `.opencode/bin/llmzk review validate Logs/Candidate\ Reviews/foo.md`, and `.opencode/bin/llmzk git diff . --stat` working without `--path`/`--review-file` flags.
- Documents using the standard `--` separator for unusual paths that begin with a dash.


## v5.5.1

- Added `.llmzk.yaml` instance config with `instance_name`, `vault_relative_prefix`, and `link_style`.
- Added `--vault-prefix` and `--link-style` to `scripts/init-vault.sh`.
- Added `.opencode/docs/MULTI_INSTANCE.md` for multiple llmzk instances inside one Obsidian vault.
- Made audit prefix-aware so configured vault-relative links such as `[[AI/04 Concept Notes/X]]` resolve against the current llmzk instance.
- Made normalize-links and fix-frontmatter respect the configured link style instead of blindly stripping subfolder prefixes.
- Made benchmarks canonicalize configured-prefix paths and wikilinks.
- Updated doctor to check `.llmzk.yaml`.

## v5.5

- Added `.opencode/docs/OPERATING_PROFILES.md` with careful, review, and fast operating profiles.
- Added `/llmzk-review-candidates` for critiquing candidate reviews before `/llmzk-write-approved`.
- Updated ingest/promote/write-approved commands to reference the careful profile.
- Updated audit/cleanup/benchmark/Git commands to reference the fast profile.
- Updated review validation and candidate-review docs to distinguish mechanical validation from review-profile critique.
- No note-taxonomy changes and no benchmark-logic changes.

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
