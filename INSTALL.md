# Install

Clone this repository, then initialize a vault.

```bash
git clone <your-llmzk-repo-url> llmzk
cd llmzk
uv run llmzk-init ~/Vaults/MyResearchVault --mode copy --git --commit
```

Use symlink mode while developing the scaffold:

```bash
uv run llmzk-init ~/Vaults/MyResearchVault --mode symlink --git --commit
```

The vault is initialized as its own Git repository. Git safety commands operate on the vault repo, not the upstream `llmzk` repo. Generated durable notes and Logs are Git-visible by default so diffs can be reviewed. Use `--commit` to create the initial scaffold checkpoint; otherwise create one manually before the first broad llmzk run.


After install, from inside the vault:

```bash
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_doctor.py .
```

For a stricter pre-run check that also fails when the Git working tree is dirty:

```bash
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_doctor.py . --fail-if-dirty
```

Before broad write operations, use:

```bash
uv run --project .opencode/llmzk-tools python .opencode/llmzk-tools/scripts/llmzk_git_safety.py preflight .
```

If preflight fails, commit/revert existing work first or explicitly choose to continue with mixed changes.
