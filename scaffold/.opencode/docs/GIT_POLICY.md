# Git policy

Git is the safety layer for this installed `llmzk` vault.

## Safety workflow

For broad `llmzk` operations, use Git as the transaction boundary:

```text
preflight -> candidate review -> user approval -> write approved -> cleanup -> audit -> diff -> stage -> commit/revert
```

Recommended procedure:

1. Run `/llmzk-git-preflight` or the command's built-in preflight step.
2. Stop if the working tree is dirty, unless the user explicitly approves mixing new generated changes with existing edits.
3. Produce a candidate review file in `Logs/Candidate Reviews/` before writing approved notes.
4. User reviews/edits checkboxes and reviewer notes.
5. Write approved `[x]` candidates only via `/llmzk-write-approved`.
6. Write notes, passports, and decision logs.
7. Run frontmatter cleanup where relevant.
8. Run audit.
9. Show a concise Git diff summary.
10. Stage only accepted files.
11. Commit with a message that references the candidate review, passport, and decision log.
12. Revert or discard changes that failed review.

## Strict preflight rule

Before broad commands such as `/llmzk-ingest-candidates`, `/llmzk-promote-candidates`, and `/llmzk-write-approved`, run:

```bash
.opencode/bin/llmzk git preflight .
```

If preflight fails, do not continue unless the user explicitly says to continue with mixed changes.

## Doctor check

Use `/llmzk-doctor` after installation, after updating the harness, and when command behaviour seems inconsistent.

The strict doctor mode is:

```bash
.opencode/bin/llmzk doctor . --fail-if-dirty
```

This checks the installed scaffold, OpenCode paths, templates, Git repo, folder placeholders, and config references.

## Agent rules

Agents may inspect Git state freely.
Agents must not stage, commit, reset, clean, or revert without explicit user approval.

Use RTK for token-efficient inspection when available:

- compact `git status`
- compact `git diff --stat`
- focused diffs for changed note files

RTK is an inspection aid; Git remains the source of truth.

## Default `.gitignore` stance

In an installed vault, generated durable notes and `Logs/` are tracked by default.
This is intentional: Git safety only works if generated notes, passports, decision logs, and review queues are visible to `git status` and `git diff`.

If a private vault should not track raw inputs or large media, add local ignore rules for `00 Inbox/`, `00 Fleeting Notes/`, or `09 Media/`.
Do not ignore durable output folders such as `01 Sources/`, `02 Literature Notes/`, `03 Permanent Notes/`, `04 Concept Notes/`, `05 Bridge Notes/`, `06 Contradiction Notes/`, `07 Index Notes/`, `08 Wiki Articles/`, or `Logs/` unless you deliberately disable Git review for generated output.

## Commit message shape

Use concise structured commits:

```text
llmzk: ingest Nielsen backpropagation source

Input:
- 00 Inbox/nielsen_backpropagation.md

Created/updated:
- source note
- literature note
- concept notes
- permanent notes
- bridge/index notes

Passport:
- Logs/Passports/<run>.yaml

Audit:
- passed / review queue updated
```

## Branches

For risky runs, use a branch:

```bash
git switch -c llmzk/ingest-topic-name
```

Merge only after the generated note graph is reviewed.


## Candidate review gate

`/llmzk-ingest` and `/llmzk-promote` are safe aliases that create candidate review files only. Durable notes are written by `/llmzk-write-approved <candidate-review-file>` after user review.

Candidate review files live in `Logs/Candidate Reviews/` and are tracked by Git by default. They form the human approval artifact before durable note writes.


## Operating profile

Git status, preflight, diff, commit-message drafting, and revert planning use the fast operating profile. They may inspect state and report mechanical changes, but must not stage, commit, reset, clean, or revert unless the user explicitly asks.
