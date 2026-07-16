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
--vault-prefix PATH   Obsidian-vault-relative prefix, e.g. AI or test
--link-style STYLE    local|vault_relative
--doctor              Run llmzk doctor after install
--source-path PATH     Record source repo path for future updates
--no-doctor           Skip llmzk doctor
--force               Overwrite installed system paths in an existing vault
```


## Installing inside a larger Obsidian vault

If your Obsidian vault contains multiple llmzk instances, install each instance into its own folder and set the vault-relative prefix:

```bash
./scripts/init-vault.sh ~/Obsidian/AI --vault-prefix AI --mode copy --git --commit
./scripts/init-vault.sh ~/Obsidian/Maths --vault-prefix Maths --mode copy --git --commit
```

The installer writes `.llmzk.yaml`. With `--vault-prefix AI`, links such as `[[AI/04 Concept Notes/Automatic differentiation|Automatic differentiation]]` are treated as valid Obsidian-vault-relative links for the `AI` llmzk instance.

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


## Audit notes

Review Queue reports are regenerated on each audit run. Treat `Logs/Review Queue/` as machine-generated output, not hand-maintained notes.


## v5.5 operating profiles

After generating a candidate review, you can ask OpenCode to critique it before writing approved notes:

```text
/llmzk-review-candidates Logs/Candidate Reviews/<file>.md
```

Use the careful profile for ingest/promote/write-approved, the review profile for candidate review critique, and the fast profile for audit/cleanup/benchmark/Git inspection. See `.opencode/docs/OPERATING_PROFILES.md` in the installed vault.

## CLI positional arguments

The installed `.opencode/bin/llmzk` wrapper uses Tyro-backed tools whose main path arguments are positional. Common commands should work as:

```bash
.opencode/bin/llmzk audit .
.opencode/bin/llmzk benchmark .opencode/benchmarks --vault .
.opencode/bin/llmzk review validate "Logs/Candidate Reviews/example.md"
.opencode/bin/llmzk git diff . --stat
```

For a path that begins with `-`, use the standard end-of-options separator:

```bash
.opencode/bin/llmzk review validate -- "Logs/Candidate Reviews/-example.md"
```



## Updating an existing installed vault

From the upstream `llmzk` checkout, dry-run first:

```bash
./scripts/update-vault.sh ~/Vaults/MyResearchVault
```

Apply only after reviewing the plan:

```bash
./scripts/update-vault.sh ~/Vaults/MyResearchVault --apply
```

Copy-mode users get updated copies of `.opencode/` and `Templates/`. Symlink-mode users can repair links and metadata with:

```bash
./scripts/update-vault.sh ~/Vaults/MyResearchVault --mode symlink --apply
```

The update workflow avoids durable notes and `Logs/`. Review the resulting Git diff before committing.
