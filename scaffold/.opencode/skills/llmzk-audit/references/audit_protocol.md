# Audit Protocol

Check for:

- bad wikilink formatting;
- unresolved links;
- path-qualified links that do not resolve exactly;
- ambiguous durable links to titles that also exist in `00 Fleeting Notes/`;
- math inside code fences;
- missing source trails on concept/permanent/bridge notes;
- type/folder mismatches;
- empty index notes;
- missing decision logs/passports for recent runs when known.

Keep the audit lightweight. Do not generate notes automatically from every issue.


## Duplicate note-title warning

The audit reports `duplicate-note-titles` when a note basename appears in `00 Fleeting Notes/` and in a durable folder such as `04 Concept Notes/`. This is especially important for promoted notes, because unqualified wikilinks in `origin_trail` can accidentally resolve to the new durable note rather than the original fleeting note. Prefer path-qualified origin links such as `[[00 Fleeting Notes/Automatic differentiation|Automatic differentiation]]`.

## Path-qualified link warning

If a wikilink target contains a slash, audit treats it as an exact path. The path may be llmzk-local, e.g. `[[04 Concept Notes/Automatic differentiation]]`, or Obsidian-vault-relative when `.llmzk.yaml` configures `vault_relative_prefix`, e.g. `[[AI/04 Concept Notes/Automatic differentiation]]`. Unknown prefixes should be reported as unresolved, not silently resolved by basename.

## Ambiguous link warning

The audit reports `ambiguous-links` when a durable note links by basename to a title that also exists in `00 Fleeting Notes/`. Prefer path-qualified durable links with aliases, e.g. `[[04 Concept Notes/Vector-Jacobian Product (VJP)|VJP]]`.
