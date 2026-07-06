#!/usr/bin/env python3
"""Create empty passport and decision log files for an llmzk workflow run."""
from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "run"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=["ingest", "promote", "synthesize", "review"])
    parser.add_argument("name")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root)
    today = dt.date.today().isoformat()
    workflow_id = f"{today}-{args.kind}-{slugify(args.name)}"

    passport = root / "Logs" / "Passports" / f"{workflow_id}.md"
    decision = root / "Logs" / "Decision Logs" / f"{workflow_id}.md"
    passport.parent.mkdir(parents=True, exist_ok=True)
    decision.parent.mkdir(parents=True, exist_ok=True)

    if not passport.exists():
        passport.write_text(f"""---\ntype: passport\nworkflow_id: {workflow_id}\nworkflow_type: {args.kind}\nstatus: started\nschema_version: 1\n---\n\n# Passport - {workflow_id}\n\n## Input\n\n- {args.name}\n\n## Outputs\n\n- TBD\n""", encoding="utf-8")
    if not decision.exists():
        decision.write_text(f"""# Decision Log - {workflow_id}\n\n## Input\n\n- {args.name}\n\n## Candidate inventory\n\n### Concept notes to create or update\n\n- TBD\n\n### Permanent notes to create or update\n\n- TBD\n\n### Bridge notes to create or update\n\n- TBD\n\n### Contradiction/tension notes to create or update\n\n- TBD\n\n### Index notes to create or update\n\n- TBD\n\n### Notes deliberately not created\n\n- TBD\n""", encoding="utf-8")

    print(passport)
    print(decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
