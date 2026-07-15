# Multi-instance and subfolder-aware linking

An Obsidian vault can contain more than one llmzk instance. For example:

```text
Vault/
  AI/
    00 Inbox/
    04 Concept Notes/
    ...
  Maths/
    00 Inbox/
    04 Concept Notes/
    ...
```

In that layout, the llmzk **instance root** is `Vault/AI`, but Obsidian resolves links relative to the outer **Obsidian vault root** `Vault`.

## Instance config

Each installed llmzk instance has `.llmzk.yaml`:

```yaml
schema_version: 1
instance_name: "AI"
vault_relative_prefix: "AI"
link_style: "vault_relative"
```

For a root-level install, use:

```yaml
schema_version: 1
instance_name: "root"
vault_relative_prefix: ""
link_style: "local"
```

## Link policy

If `link_style: local`, internal links should look like:

```markdown
[[04 Concept Notes/Automatic differentiation|Automatic differentiation]]
```

If `link_style: vault_relative` and `vault_relative_prefix: AI`, internal links should look like:

```markdown
[[AI/04 Concept Notes/Automatic differentiation|Automatic differentiation]]
```

Both forms can resolve during audit when the configured prefix is known, but the normalizer should make links consistent with the configured `link_style`.

## Tool behaviour

- `llmzk audit` treats configured-prefix links as valid vault-relative links.
- `llmzk normalize-links` preserves or adds the configured prefix when `link_style: vault_relative`.
- `llmzk fix-frontmatter` path-qualifies provenance links using the configured prefix.
- `llmzk benchmark` canonicalizes expected links and files so local and configured-prefix paths compare correctly.

Unknown prefixes should not be silently accepted. For example, if `vault_relative_prefix: AI`, then `[[Maths/04 Concept Notes/X]]` should resolve only if the `Maths/...` file exists inside the current llmzk instance, which normally it should not.

## Installing into a subfolder

Use:

```bash
./scripts/init-vault.sh ~/Obsidian/AI --vault-prefix AI --mode copy --git
```

For a root-level install:

```bash
./scripts/init-vault.sh ~/Obsidian --mode copy --git
```
