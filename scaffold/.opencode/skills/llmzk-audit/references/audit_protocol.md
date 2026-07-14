# Audit Protocol

Check for:

- bad wikilink formatting;
- unresolved links;
- math inside code fences;
- missing source trails on concept/permanent/bridge notes;
- type/folder mismatches;
- empty index notes;
- missing decision logs/passports for recent runs when known.

Keep the audit lightweight. Do not generate notes automatically from every issue.


## Duplicate note-title warning

The audit reports `duplicate-note-titles` when a note basename appears in `00 Fleeting Notes/` and in a durable folder such as `04 Concept Notes/`. This is especially important for promoted notes, because unqualified wikilinks in `origin_trail` can accidentally resolve to the new durable note rather than the original fleeting note. Prefer path-qualified origin links such as `[[00 Fleeting Notes/Automatic differentiation|Automatic differentiation]]`.
