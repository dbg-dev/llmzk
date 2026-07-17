# llmzk

Current version: v5.7.1

`llmzk` is a lightweight OpenCode + Obsidian harness for building a Zettelkasten with LLM assistance.

This repository is an **installer/source repo**, not the vault itself.

```text
llmzk repo        = upstream scaffold, skills, commands, templates, install script
installed vault   = your Obsidian vault and Git safety boundary
```

## What it installs

The install script creates a vault with:

```text
AGENTS.md
opencode.json
.llmzk.yaml               llmzk instance config
.opencode/                 OpenCode commands, agents, skills, docs, wrapper, tools
Templates/                 reusable note templates
00 Inbox/                  raw source inputs
00 Fleeting Notes/         rough personal notes
01 Sources/
02 Literature Notes/
03 Permanent Notes/
04 Concept Notes/
05 Bridge Notes/
06 Contradiction Notes/
07 Index Notes/
08 Wiki Articles/
09 Media/
Logs/                      candidate reviews, passports, decision logs, review queues
```

The numbered folders and `Logs/` are real vault-owned folders. They are created with `.gitkeep` placeholders, and generated durable notes/logs are Git-visible by default so vault safety can use `git status` and `git diff`.

## Install into a vault

From a clone of this repository:

```bash
./scripts/init-vault.sh ~/Vaults/MyResearchVault --mode copy --git --commit
```

For development, you can symlink the system layer instead:

```bash
./scripts/init-vault.sh ~/Vaults/MyResearchVault --mode symlink --git --commit
```

Use `copy` for portability. Use `symlink` when actively developing `llmzk` and wanting the vault to use the local upstream files.


## Multi-instance / subfolder installs

An Obsidian vault can contain multiple llmzk instances, for example `Vault/AI/` and `Vault/Maths/`. Use `--vault-prefix` when the llmzk instance lives inside a larger Obsidian vault:

```bash
./scripts/init-vault.sh ~/Obsidian/AI --vault-prefix AI --mode copy --git --commit
```

This writes `.llmzk.yaml` so audit, normalize-links, fix-frontmatter, and benchmark can understand Obsidian-vault-relative links such as `[[AI/04 Concept Notes/Automatic differentiation|Automatic differentiation]]`.


## Updating an installed vault

Use `scripts/update-vault.sh` from the upstream source checkout. It assembles the generated Python tooling before invoking the installed updater.

From the upstream source checkout, run a dry-run first:

    ./scripts/update-vault.sh ~/Vaults/MyResearchVault

Then apply after reviewing the planned system-layer changes:

    ./scripts/update-vault.sh ~/Vaults/MyResearchVault --apply

Updates are limited to the installed system layer: `AGENTS.md`, `opencode.json`, `.gitignore`, `.llmzk.yaml` metadata, `.opencode/`, and `Templates/`. Durable note folders and `Logs/` are not touched.

## Git safety

The installed vault is initialized as its own Git repository unless you pass `--no-git`.

The intended workflow is:

```text
git preflight -> candidate review -> user approval -> write approved -> cleanup -> audit -> git diff -> stage -> commit/revert
```

Agents may inspect Git status and diffs, but must not stage, commit, reset, clean, or revert without explicit user approval.

## Main OpenCode commands in an installed vault

```text
/llmzk-ingest <path>                  # safe alias for candidate review
/llmzk-ingest-candidates <path>       # create candidate review only
/llmzk-promote <path-or-folder>       # safe alias for candidate review
/llmzk-promote-candidates <path>      # create candidate review only
/llmzk-write-approved <review-file>   # write approved [x] candidates
/llmzk-review-validate <review-file>
/llmzk-review-candidates <review-file>
/llmzk-audit
/llmzk-normalize-links --dry-run
/llmzk-fix-frontmatter --apply
/llmzk-doctor
/llmzk-update
/llmzk-git-status
/llmzk-git-preflight
/llmzk-git-diff
/llmzk-git-commit-message <passport>
/llmzk-git-revert-run <passport>
/llmzk-synthesize <topic>
```



## Operating profiles

v5.5 adds llmzk operating profiles. These are instruction overlays for agent behaviour, not OpenCode permission modes.

```text
careful = ingest, promote, and write-approved knowledge creation
review  = critique candidate reviews before durable notes are written
fast    = audit, benchmark, Git inspection, frontmatter/link cleanup
```

See `.opencode/docs/OPERATING_PROFILES.md` in an installed vault.

## Candidate review gate

In v5.3, ingest and promote are review-gated by default:

```text
/llmzk-ingest <source>
  -> creates `Logs/Candidate Reviews/...md` only

# edit checkboxes and reviewer notes

/llmzk-write-approved <candidate-review-file>
  -> writes approved durable notes, passport, decision log, audit, and Git diff
```

Synthesize is intentionally out of scope for the v5.3 review gate.

## Installed-vault tool wrapper

The installed vault includes a small wrapper:

```bash
.opencode/bin/llmzk audit .
.opencode/bin/llmzk doctor .
.opencode/bin/llmzk git preflight .
.opencode/bin/llmzk git diff . --stat
.opencode/bin/llmzk review-validate "Logs/Candidate Reviews/example.md"
```

The wrapper hides the `uv run --project .opencode/llmzk-tools ...` implementation detail from OpenCode command files.

## Design boundary

```text
obsidian-skills       = Obsidian mechanics
llmzk skills          = Zettelkasten judgement
.opencode/llmzk-tools = deterministic audit, cleanup, doctor, Git safety helpers
Git                   = vault safety and rollback boundary
```

## Python CLI implementation

The deterministic Python tools have one editable source location:

    packages/llmzk-tools/

Before installation or update, `scripts/build-scaffold.py` generates the installed-vault copy at `scaffold/.opencode/llmzk-tools/`. The generated directory is ignored by Git and must not be edited directly.

The installed copy remains self-contained, exposes console scripts with `[project.scripts]`, uses `tyro` for CLIs, and uses `GitPython` for Git-facing operations.
## Repository layout

    packages/llmzk-tools/             authoritative Python tools package
    scripts/build-scaffold.py         assemble the distributable scaffold
    scripts/init-vault.sh             create a concrete vault
    scripts/update-vault.sh           update an installed vault
    scaffold/                         static installed-vault files
    scaffold/.opencode/llmzk-tools/   generated installed-vault package
    scaffold/.opencode/bin/llmzk      installed-vault wrapper
    scaffold/Templates/               reusable note templates
    tests/integration/                source/distribution boundary tests
## v5.5.1 notes

This release adds subfolder-aware linking through `.llmzk.yaml`, `--vault-prefix`, prefix-aware audit/normalization, and benchmark canonicalisation for vault-relative links.

## v5.5 notes

This release adds operating profiles and `/llmzk-review-candidates` to make the candidate review gate easier to use. It does not change the note taxonomy or deterministic benchmark logic.

## v5.3.3 bugfix notes

This release fixes audit false positives for wikilinks whose titles contain periods such as `w.r.t.`, regenerates Review Queue reports on each audit, and normalises candidate-review status timestamps when reviews are marked applied/rejected/superseded.


## v5.3.3 fixes

- Path-qualified `origin_trail` links for promoted notes from `00 Fleeting Notes/`.
- Audit warning for duplicate note basenames across fleeting and durable folders.
- Candidate-review frontmatter normalization for lowercase booleans and quoted ISO timestamps.
- Backpropagation cost wording guardrails.
- Softer reasoning-distillation contradiction wording guidance.

## CLI positional arguments

The installed `.opencode/bin/llmzk` wrapper uses Tyro-backed tools whose main path arguments are positional. Common commands should work as:

```bash
.opencode/bin/llmzk audit .
.opencode/bin/llmzk benchmark .opencode/benchmarks --vault .
.opencode/bin/llmzk review validate "Logs/Candidate Reviews/example.md"
.opencode/bin/llmzk git diff . --stat
```

For a path that begins with `-`, use the standard end-of-options separator:

```bash
.opencode/bin/llmzk review validate -- "Logs/Candidate Reviews/-example.md"
```

