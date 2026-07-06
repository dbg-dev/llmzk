# Git policy

Git is the safety layer for this installed `llmzk` vault.

## Safety workflow

For broad `llmzk` operations, use Git as the transaction boundary:

```text
inspect -> candidate inventory -> write -> audit -> diff -> stage -> commit/revert
```

Recommended procedure:

1. Start from a clean working tree where possible.
2. Run the `llmzk` command.
3. Run audit and any normalizers.
4. Inspect `git status` and `git diff`.
5. Stage only accepted files.
6. Commit with a message that references the passport and decision log.
7. Revert or discard changes that failed review.

## Agent rules

Agents may inspect Git state freely.
Agents must not stage, commit, reset, clean, or revert without explicit user approval.

Use RTK for token-efficient inspection when available:

- compact `git status`
- compact `git diff --stat`
- focused diffs for changed note files

RTK is an inspection aid; Git remains the source of truth.

## Default `.gitignore` stance

By default, generated content in numbered folders and `Logs/` is ignored so the scaffold stays clean.
This is appropriate for a reusable public scaffold.

If this is your real private vault and you want Git to version your notes, remove or relax those ignore rules.
A common private-vault policy is to track generated durable notes and logs, but keep raw inbox/media private.

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
