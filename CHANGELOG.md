# Changelog

## 0.5.0

- Converted release into an upstream installer/source repository.
- Added `llmzk-init` to create a separate vault repository.
- Moved installed operating docs under `.opencode/docs/`.
- Keeps `AGENTS.md` at installed vault root as the OpenCode project instruction entry point.
- Adds `opencode.json` with explicit instruction paths.
- Supports copy and symlink install modes for `.opencode/` and `Templates/`.
- Includes Git safety commands and `llmzk_git_safety.py`.
- Creates real numbered output folders and `Logs/` with `.gitkeep`; generated contents are ignored by default.
