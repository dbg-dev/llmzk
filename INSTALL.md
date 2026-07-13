# Installing llmzk

Clone this repository, then create a concrete Obsidian/OpenCode vault from the scaffold.

```bash
git clone https://github.com/dbg-dev/llmzk.git
cd llmzk
./scripts/init-vault.sh ~/Vaults/MyResearchVault --mode copy --git --commit
```

For active scaffold development, use symlink mode:

```bash
./scripts/init-vault.sh ~/Vaults/MyResearchVault --mode symlink --git --commit
```

Use copy mode for portability. Symlink mode is convenient on macOS/Linux when iterating on this repo.

## Options

```text
--mode copy|symlink   Install .opencode and Templates by copy or symlink
--git                 Initialize a Git repository in the vault
--no-git              Do not initialize Git
--commit              Create an initial scaffold commit
--doctor              Run llmzk doctor after install
--no-doctor           Skip llmzk doctor
--force               Overwrite installed system paths in an existing vault
```

## After install

```bash
cd ~/Vaults/MyResearchVault
opencode
/llmzk-doctor
/llmzk-git-status
```

The vault itself is the Git safety boundary. The source repo is only the upstream scaffold and installer.


## First ingest workflow

```text
/llmzk-ingest 00 Inbox/<source>.md
```

This creates a candidate review in `Logs/Candidate Reviews/` and stops before durable notes. Edit the review file, then run:

```text
/llmzk-write-approved Logs/Candidate Reviews/<candidate-review-file>.md
```
