#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path

from llmzk_tools.normalize_links import normalize_text
from llmzk_tools.audit import audit
from llmzk_tools.fix_frontmatter import fix_text
from llmzk_tools.review import Normalize, run_normalize, validate_review


def test_normalize_links():
    text = "[[Jacobian-Vector Product (JVP)\\|JVP]] and [[04 Concept Notes/Backpropagation.md]]"
    new, changes = normalize_text(text)
    assert "[[Jacobian-Vector Product (JVP)|JVP]]" in new
    assert "[[04 Concept Notes/Backpropagation]]" in new
    assert len(changes) == 2


def test_normalize_ignores_code_fences():
    text = "```markdown\n[[Target\\|Alias]]\n```\n\n[[Target\\|Alias]]"
    new, changes = normalize_text(text)
    assert "```markdown\n[[Target\\|Alias]]\n```" in new
    assert "[[Target|Alias]]" in new
    assert len(changes) == 1


def test_audit_math_fence():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        p = root / "04 Concept Notes" / "Bad Math.md"
        p.parent.mkdir(parents=True)
        p.write_text("---\ntype: concept\n---\n\n```latex\n\\frac{a}{b}\n```\n", encoding="utf-8")
        issues = audit(root)
        assert issues["math-formatting"]


def test_fix_frontmatter_nested_lists():
    text = """---
type: bridge
connects:
  - - - Neuron error delta
source_trail:
  - - - Source - How the backpropagation algorithm works
---

# Example
"""
    new, changed, error = fix_text(text)
    assert error is None
    assert changed
    assert 'connects:\n  - "[[Neuron error delta]]"' in new
    assert 'source_trail:\n  - "[[Source - How the backpropagation algorithm works]]"' in new
    assert "- - -" not in new


def test_audit_frontmatter_issues():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        p = root / "05 Bridge Notes" / "Bad Bridge.md"
        p.parent.mkdir(parents=True)
        p.write_text("""---
type: bridge
connects:
  - - - Neuron error delta
---

# Bad Bridge
""", encoding="utf-8")
        issues = audit(root)
        assert issues["frontmatter-issues"]


def test_audit_wrt_title_not_truncated():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        src = root / "01 Sources" / "Source - Example.md"
        src.parent.mkdir(parents=True)
        src.write_text("---\ntype: source\nstatus: ingested\n---\n\n# Source\n", encoding="utf-8")
        target = root / "03 Permanent Notes" / "Defining neuron error as gradient w.r.t. weighted input makes backpropagation algebraically simple.md"
        target.parent.mkdir(parents=True)
        target.write_text('---\ntype: permanent\nsource_trail:\n  - "[[Source - Example]]"\n---\n\n# Target\n', encoding="utf-8")
        source = root / "04 Concept Notes" / "Neuron error delta.md"
        source.parent.mkdir(parents=True)
        source.write_text(
            '---\ntype: concept\nsource_trail:\n  - "[[Source - Example]]"\n---\n\n'
            "See [[Defining neuron error as gradient w.r.t. weighted input makes backpropagation algebraically simple]].\n",
            encoding="utf-8",
        )
        issues = audit(root)
        assert issues["unresolved-links"] == []


def test_audit_path_qualified_links_are_exact():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        concept = root / "04 Concept Notes" / "Automatic differentiation.md"
        concept.parent.mkdir(parents=True)
        concept.write_text('---\ntype: concept\norigin_trail:\n  - "[[00 Fleeting Notes/Automatic differentiation|Automatic differentiation]]"\n---\n\n# Automatic differentiation\n', encoding="utf-8")
        source = root / "04 Concept Notes" / "Forward-mode automatic differentiation.md"
        source.write_text('---\ntype: concept\nconnects:\n  - "[[Automatic differentiation]]"\n---\n\nBroken [[test/04 Concept Notes/Automatic differentiation]].\n', encoding="utf-8")
        issues = audit(root)
        assert issues["unresolved-links"], issues


def test_normalize_project_prefixed_path_keeps_vault_relative_folder():
    text = "See [[test/04 Concept Notes/Automatic differentiation.md]]."
    new, changes = normalize_text(text)
    assert "[[04 Concept Notes/Automatic differentiation]]" in new
    assert changes == [("test/04 Concept Notes/Automatic differentiation.md", "04 Concept Notes/Automatic differentiation")]


def test_normalize_ambiguous_duplicate_link_prefers_durable_path():
    locations = {
        "Automatic differentiation": [
            Path("00 Fleeting Notes/Automatic differentiation.md"),
            Path("04 Concept Notes/Automatic differentiation.md"),
        ]
    }
    text = "See [[Automatic differentiation]]."
    new, changes = normalize_text(text, locations)
    assert "[[04 Concept Notes/Automatic differentiation]]" in new
    assert changes == [("Automatic differentiation", "04 Concept Notes/Automatic differentiation")]


def test_candidate_review_validate():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        p = root / "review.md"
        p.write_text("""---
type: candidate_review
status: proposed
mode: ingest
input:
  - "00 Inbox/example.md"
created: 2026-07-13
applied: false
schema_version: 1
---

# Candidate Review - Example

## Source

Input:
- `00 Inbox/example.md`

## Proposed notes

### Source notes
- [x] `01 Sources/Source - Example.md` — source wrapper.

### Literature notes
- [x] `02 Literature Notes/Literature - Example.md` — source compression.

### Concept notes
- [x] `04 Concept Notes/Example concept.md` — reusable concept.

### Permanent notes
- [x] `03 Permanent Notes/Example claim.md` — durable claim.

### Bridge notes
- [ ] `05 Bridge Notes/Example bridge.md` — weak bridge rejected.

### Contradiction/tension notes
- [ ] `06 Contradiction Notes/Example tension.md` — no durable tension.

### Index notes
- [x] `07 Index Notes/Index - Example.md` — map.

## Deliberately not created

- [ ] `Author` — metadata, not concept.

## Reviewer instructions

Edit checkboxes before writing.

## Reviewer notes

None.
""", encoding="utf-8")
        code, findings = validate_review(p)
        assert code == 0, findings


def test_normalize_links_preserves_frontmatter_paths():
    text = """---
origin_trail:
  - "[[00 Fleeting Notes/Automatic differentiation|Automatic differentiation]]"
---

Body [[04 Concept Notes/Backpropagation.md]].
"""
    new, changes = normalize_text(text)
    assert '[[00 Fleeting Notes/Automatic differentiation|Automatic differentiation]]' in new
    assert '[[04 Concept Notes/Backpropagation]]' in new
    assert len(changes) == 1


def test_fix_frontmatter_path_qualifies_origin_trail():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        fleeting = root / "00 Fleeting Notes" / "Automatic differentiation.md"
        concept = root / "04 Concept Notes" / "Automatic differentiation.md"
        fleeting.parent.mkdir(parents=True)
        concept.parent.mkdir(parents=True)
        fleeting.write_text("# Automatic differentiation\n", encoding="utf-8")
        text = """---
type: concept
origin_trail:
  - "[[Automatic differentiation]]"
---

# Automatic differentiation
"""
        new, changed, error = fix_text(text, fleeting_titles={"Automatic differentiation": "00 Fleeting Notes/Automatic differentiation"})
        assert error is None
        assert changed
        assert '"[[00 Fleeting Notes/Automatic differentiation|Automatic differentiation]]"' in new


def test_audit_duplicate_note_titles():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        fleeting = root / "00 Fleeting Notes" / "Automatic differentiation.md"
        concept = root / "04 Concept Notes" / "Automatic differentiation.md"
        fleeting.parent.mkdir(parents=True)
        concept.parent.mkdir(parents=True)
        fleeting.write_text("# Automatic differentiation\n", encoding="utf-8")
        concept.write_text('---\ntype: concept\norigin_trail:\n  - "[[Automatic differentiation]]"\n---\n\n# Automatic differentiation\n', encoding="utf-8")
        issues = audit(root)
        assert issues["duplicate-note-titles"]
        assert issues["frontmatter-issues"]


def test_candidate_review_normalize():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        p = root / "review.md"
        p.write_text("""---
type: candidate_review
status: applied
mode: ingest
input:
  - 00 Inbox/example.md
created: 2026-07-13
applied: True
schema_version: 1
modified: 2026-07-13 13:53:59+01:00
---

# Candidate Review - Example
""", encoding="utf-8")
        run_normalize(Normalize(review_file=p))
        text = p.read_text(encoding="utf-8")
        assert "applied: true" in text
        assert 'created: "2026-07-13"' in text
        assert 'modified: "2026-07-13T13:53:59+01:00"' in text
        assert '- "00 Inbox/example.md"' in text


def main() -> int:
    test_normalize_links()
    test_normalize_ignores_code_fences()
    test_normalize_links_preserves_frontmatter_paths()
    test_audit_math_fence()
    test_fix_frontmatter_nested_lists()
    test_fix_frontmatter_path_qualifies_origin_trail()
    test_audit_frontmatter_issues()
    test_audit_wrt_title_not_truncated()
    test_audit_duplicate_note_titles()
    test_audit_path_qualified_links_are_exact()
    test_normalize_project_prefixed_path_keeps_vault_relative_folder()
    test_normalize_ambiguous_duplicate_link_prefers_durable_path()
    test_candidate_review_validate()
    test_candidate_review_normalize()
    print("Smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
