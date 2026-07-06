#!/usr/bin/env python3
"""Normalize obvious Obsidian wikilink formatting issues.

This script is intentionally mechanical. It does not create notes.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def normalize_target(target: str) -> str:
    target = target.replace(r"\|", "|")
    # Strip markdown suffix before alias/heading handling.
    if "|" in target:
        left, alias = target.split("|", 1)
        left = _clean_path(left)
        return f"{left}|{alias}"
    return _clean_path(target)


def _clean_path(target: str) -> str:
    target = target.strip()
    if target.endswith(".md"):
        target = target[:-3]
    # Remove common project-prefixed paths before known vault folders.
    folders = [
        "00 Inbox/", "00 Fleeting Notes/", "01 Sources/", "02 Literature Notes/",
        "03 Permanent Notes/", "04 Concept Notes/", "05 Bridge Notes/",
        "06 Contradiction Notes/", "07 Index Notes/", "08 Wiki Articles/", "09 Media/", "Logs/Passports/", "Logs/Decision Logs/", "Logs/Review Queue/",
    ]
    for folder in folders:
        idx = target.find(folder)
        if idx >= 0:
            target = target[idx + len(folder):]
            if target.endswith(".md"):
                target = target[:-3]
            break
    return target


def normalize_text(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Normalize wikilinks outside fenced code blocks.

    Documentation often contains examples of bad links. Do not rewrite code-fenced
    examples because those examples are intentionally literal.
    """
    changes: list[tuple[str, str]] = []

    def repl(match: re.Match[str]) -> str:
        old = match.group(1)
        new = normalize_target(old)
        if old != new:
            changes.append((old, new))
        return f"[[{new}]]"

    out: list[str] = []
    in_fence = False
    fence_marker = ""
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            out.append(line)
            continue
        if in_fence:
            out.append(line)
        else:
            out.append(WIKILINK_RE.sub(repl, line))
    return "".join(out), changes


def iter_markdown(root: Path):
    skip = {".venv", ".git"}
    for path in root.rglob("*.md"):
        if any(part in skip for part in path.parts):
            continue
        yield path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.root)
    total = 0
    for path in iter_markdown(root):
        text = path.read_text(encoding="utf-8")
        new_text, changes = normalize_text(text)
        if changes:
            total += len(changes)
            print(f"{path}:")
            for old, new in changes:
                print(f"  [[{old}]] -> [[{new}]]")
            if args.apply:
                path.write_text(new_text, encoding="utf-8")
    if total == 0:
        print("No link normalization changes found.")
    elif not args.apply:
        print(f"Found {total} link normalization change(s). Re-run with --apply to modify files.")
    else:
        print(f"Applied {total} link normalization change(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
