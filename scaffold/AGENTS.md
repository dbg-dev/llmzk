# llmzk vault instructions

This vault uses the `llmzk` OpenCode/Obsidian Zettelkasten harness.

Read these before making broad changes:

- `.opencode/docs/SOUL.md`
- `.opencode/docs/STRUCTURE.md`
- `.opencode/docs/STYLE.md`
- `.opencode/docs/SCHEMA.md`
- `.opencode/docs/GIT_POLICY.md`
- `.opencode/docs/OPERATING_PROFILES.md`
- `.opencode/docs/OBSIDIAN_SKILLS.md`

Use `.opencode/commands/`, `.opencode/agents/`, and `.opencode/skills/` as the OpenCode harness.
Use `Templates/` as note templates.
Treat the numbered folders and `Logs/` as vault-owned working content.

Before any broad write operation, run Git preflight. If the working tree is dirty, stop unless the user explicitly says to continue with mixed changes.

For ingest and promote, use the **careful operating profile** and the candidate review gate: create a candidate review file first, let the user review/edit it, then write durable notes only via `/llmzk-write-approved`.

For candidate-review critique, use the **review operating profile**: inspect the proposal, flag missing or weak candidates, and suggest checkbox edits without writing durable notes.

For audit, benchmark, link cleanup, frontmatter cleanup, and Git inspection, use the **fast operating profile**: make only mechanical changes and do not reinterpret concepts.

After any durable write operation, run frontmatter cleanup when relevant, run audit, and show a concise Git diff summary.

Use `/llmzk-doctor` after installation, after harness updates, or when command behaviour looks inconsistent.

Do not stage, commit, reset, clean, or revert Git changes unless the user explicitly asks.
