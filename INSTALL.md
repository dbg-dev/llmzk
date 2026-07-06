# Install

Clone this repository, then initialize a vault.

```bash
git clone <your-llmzk-repo-url> llmzk
cd llmzk
uv run llmzk-init ~/Vaults/MyResearchVault --mode copy --git
```

Use symlink mode while developing the scaffold:

```bash
uv run llmzk-init ~/Vaults/MyResearchVault --mode symlink --git
```

The vault is initialized as its own Git repository. Git safety commands operate on the vault repo, not the upstream `llmzk` repo.
