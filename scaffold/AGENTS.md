# llmzk vault instructions

This vault uses the `llmzk` OpenCode/Obsidian Zettelkasten harness.

Read these before making broad changes:

- `.opencode/docs/SOUL.md`
- `.opencode/docs/STRUCTURE.md`
- `.opencode/docs/STYLE.md`
- `.opencode/docs/SCHEMA.md`
- `.opencode/docs/GIT_POLICY.md`
- `.opencode/docs/OBSIDIAN_SKILLS.md`

Use `.opencode/commands/`, `.opencode/agents/`, and `.opencode/skills/` as the OpenCode harness.
Use `Templates/` as note templates.
Treat the numbered folders and `Logs/` as vault-owned working content.

Before any broad write operation, run Git preflight. If the working tree is dirty, stop unless the user explicitly says to continue with mixed changes.

For ingest and promote, use the candidate review gate: create a candidate review file first, let the user review/edit it, then write durable notes only via `/llmzk-write-approved`.

After any durable write operation, run frontmatter cleanup when relevant, run audit, and show a concise Git diff summary.

Use `/llmzk-doctor` after installation, after harness updates, or when command behaviour looks inconsistent.

Do not stage, commit, reset, clean, or revert Git changes unless the user explicitly asks.
