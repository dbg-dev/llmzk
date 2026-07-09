# Changelog

## 0.5.1

- Added `llmzk-doctor` for installed-vault health checks.
- Added installed command `/llmzk-doctor`.
- `llmzk-init` now runs doctor by default after scaffold installation.
- Install docs now recommend `--commit` so the initial scaffold starts from a clean Git preflight state.
- Main broad-write commands now require Git preflight before writing.
- `/llmzk-ingest`, `/llmzk-promote`, and `/llmzk-synthesize` now spell out the post-write cleanup/audit/diff sequence.
- Updated Git policy to make the dirty-tree stop rule explicit.
- Changed installed-vault `.gitignore` so generated durable notes and Logs are Git-visible by default.
- Doctor now checks that generated durable outputs are not ignored by Git.
- Added installed `llmzk_doctor.py` under `.opencode/llmzk-tools/scripts/`.

## 0.5.0

- Converted release into an upstream installer/source repository.
- Added `llmzk-init` to create a separate vault repository.
- Moved installed operating docs under `.opencode/docs/`.
- Keeps `AGENTS.md` at installed vault root as the OpenCode project instruction entry point.
- Adds `opencode.json` with explicit instruction paths.
- Supports copy and symlink install modes for `.opencode/` and `Templates/`.
- Includes Git safety commands and `llmzk_git_safety.py`.
- Creates real numbered output folders and `Logs/` with `.gitkeep`; generated contents are ignored by default.
