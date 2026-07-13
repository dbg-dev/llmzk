#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path

from llmzk_tools.normalize_links import normalize_text
from llmzk_tools.audit import audit
from llmzk_tools.fix_frontmatter import fix_text
from llmzk_tools.review import validate_review


def test_normalize_links():
    text = "[[Jacobian-Vector Product (JVP)\\|JVP]] and [[04 Concept Notes/Backpropagation.md]]"
    new, changes = normalize_text(text)
    assert "[[Jacobian-Vector Product (JVP)|JVP]]" in new
    assert "[[Backpropagation]]" in new
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


def main() -> int:
    test_normalize_links()
    test_normalize_ignores_code_fences()
    test_audit_math_fence()
    test_fix_frontmatter_nested_lists()
    test_audit_frontmatter_issues()
    test_candidate_review_validate()
    print("Smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
