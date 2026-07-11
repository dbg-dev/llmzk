#!/usr/bin/env python3
"""Create empty passport and decision log files for an llmzk workflow run."""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from typing import Literal

import tyro


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "run"


def run(kind: Literal["ingest", "promote", "synthesize", "review"], name: str, root: Path = Path(".")) -> int:
    """Create empty passport and decision log files for an llmzk workflow run."""
    today = dt.date.today().isoformat()
    workflow_id = f"{today}-{kind}-{slugify(name)}"

    passport = root / "Logs" / "Passports" / f"{workflow_id}.md"
    decision = root / "Logs" / "Decision Logs" / f"{workflow_id}.md"
    passport.parent.mkdir(parents=True, exist_ok=True)
    decision.parent.mkdir(parents=True, exist_ok=True)

    if not passport.exists():
        passport.write_text(f"""---
type: passport
workflow_id: {workflow_id}
workflow_type: {kind}
status: started
schema_version: 1
---

# Passport - {workflow_id}

## Input

- {name}

## Outputs

- TBD
""", encoding="utf-8")
    if not decision.exists():
        decision.write_text(f"""# Decision Log - {workflow_id}

## Input

- {name}

## Candidate inventory

### Concept notes to create or update

- TBD

### Permanent notes to create or update

- TBD

### Bridge notes to create or update

- TBD

### Contradiction/tension notes to create or update

- TBD

### Index notes to create or update

- TBD

### Notes deliberately not created

- TBD
""", encoding="utf-8")

    print(passport)
    print(decision)
    return 0


def main() -> int:
    return tyro.cli(run)


if __name__ == "__main__":
    raise SystemExit(main())
