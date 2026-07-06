# Structure

`llmzk` separates the installed OpenCode system from vault-owned output.

## Installed vault layout

```text
AGENTS.md                root project instructions loaded by OpenCode
opencode.json            optional OpenCode instruction config
.opencode/               system layer
  commands/              slash commands
  agents/                specialist agents
  skills/                llmzk skills
  docs/                  llmzk reference docs
  llmzk-tools/           uv-based Python utilities
Templates/               reusable note templates
Logs/                    generated workflow output
00-09 folders            vault-owned input/output content
```

## Ownership

- `.opencode/` is the llmzk/OpenCode system layer.
- `Templates/` is installed scaffold material.
- `00 Inbox/`, `00 Fleeting Notes/`, `01 Sources/` ... `09 Media/` are real vault folders.
- `Logs/` is real workflow output.

Numbered note folders and `Logs/` are created as real directories with `.gitkeep` files.
Generated contents are ignored by Git by default so the repository can remain a clean scaffold.
Remove or adjust `.gitignore` if you want the vault repository to track actual notes.

## Upstream vs installed vault

The upstream `llmzk` repository is not itself the vault. It provides an init command and a scaffold.
The installed vault is a separate Git repository used as the safety boundary for note changes.
