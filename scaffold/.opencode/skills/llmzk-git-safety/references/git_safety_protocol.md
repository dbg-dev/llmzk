# Git safety protocol

## Preflight

Before a broad write command, inspect Git state.

- Clean tree: proceed.
- Dirty tree: ask before proceeding.
- Untracked generated notes: warn that a previous run may be unreviewed.

## Post-run

After an ingest, promotion, synthesis, normalization, or frontmatter-fix run:

1. run or recommend audit;
2. inspect `git status`;
3. inspect a concise diff;
4. summarize created, modified, and deleted files;
5. wait for user instruction before staging or committing.

## Staging

Stage only files the user accepts. Prefer explicit paths rather than `git add .` when generated output is mixed with user edits.

## Commit

Commit only after explicit approval. Include the passport and decision log in the message when available.

## Revert

Always dry-run first. Reverting a run should be based on the passport output list plus Git status. Do not delete user-created files unless the user explicitly approves.
