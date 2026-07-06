#!/usr/bin/env python3
"""Lightweight audit for llmzk vaults."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any, Iterable

import yaml

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
CODE_FENCE_RE = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
MATH_HINTS = [r"\frac", r"\partial", r"\delta", r"\nabla", r"\odot", r"\sum", r"\begin{aligned}"]
DURABLE_FOLDERS = ["03 Permanent Notes", "04 Concept Notes", "05 Bridge Notes", "06 Contradiction Notes"]
LINK_LIST_FIELDS = {"source_trail", "origin_trail", "connects", "derived_from", "updates", "related"}

CONTENT_ROOTS = {
    "00 Fleeting Notes", "01 Sources", "02 Literature Notes", "03 Permanent Notes",
    "04 Concept Notes", "05 Bridge Notes", "06 Contradiction Notes", "07 Index Notes",
    "08 Wiki Articles",
}
RAW_INBOX_ROOT = "00 Inbox"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def iter_md(root: Path, *, include_inbox: bool = False) -> Iterable[Path]:
    # Audit durable/user-facing vault content. Raw inbox is separated so it does not pollute
    # ordinary unresolved-link queues.
    content_roots = set(CONTENT_ROOTS)
    if include_inbox:
        content_roots.add(RAW_INBOX_ROOT)
    for p in root.rglob("*.md"):
        try:
            rel = p.relative_to(root)
        except ValueError:
            continue
        if not rel.parts or rel.parts[0] not in content_roots:
            continue
        if p.name.lower() == "readme.md":
            continue
        yield p


def note_stems(root: Path) -> set[str]:
    return {p.stem for p in iter_md(root, include_inbox=False)}


def target_stem(target: str) -> str:
    target = target.replace(r"\|", "|")
    target = target.split("|", 1)[0]
    target = target.split("#", 1)[0]
    if target.endswith(".md"):
        target = target[:-3]
    return Path(target).stem


def split_frontmatter(text: str) -> tuple[str | None, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, text
    return match.group(1), text[match.end():]


def has_nested_singleton_list(value: Any) -> bool:
    if isinstance(value, list):
        if any(isinstance(item, list) for item in value):
            return True
        return any(has_nested_singleton_list(item) for item in value)
    return False


def audit_frontmatter(path: Path, text: str, rel: Path) -> list[str]:
    fm, _ = split_frontmatter(text)
    if fm is None:
        return []
    issues: list[str] = []
    try:
        data = yaml.safe_load(fm) or {}
    except yaml.YAMLError as exc:
        return [f"{rel}: YAML parse error: {exc}"]
    if not isinstance(data, dict):
        return [f"{rel}: frontmatter is not a mapping"]
    for field in LINK_LIST_FIELDS:
        if field not in data:
            continue
        value = data[field]
        if has_nested_singleton_list(value):
            issues.append(f"{rel}: `{field}` has nested list formatting; run llmzk_fix_frontmatter.py")
        if value not in (None, ""):
            items = value if isinstance(value, list) else [value]
            for item in items:
                if isinstance(item, list):
                    issues.append(f"{rel}: `{field}` contains nested list item {item!r}")
                elif isinstance(item, str):
                    if item and not (item.startswith("[[") and item.endswith("]]")):
                        issues.append(f"{rel}: `{field}` item should be quoted wikilink: {item!r}")
                    if r"\|" in item:
                        issues.append(f"{rel}: `{field}` contains escaped pipe: {item!r}")
    return issues


def audit(root: Path) -> dict[str, list[str]]:
    stems = note_stems(root)
    issues: dict[str, list[str]] = {
        "bad-link-formatting": [],
        "unresolved-links": [],
        "raw-inbox-unresolved-links": [],
        "math-formatting": [],
        "frontmatter-issues": [],
        "missing-source-trail": [],
        "empty-index-notes": [],
    }

    for path in iter_md(root, include_inbox=False):
        text = read(path)
        rel = path.relative_to(root)
        issues["frontmatter-issues"].extend(audit_frontmatter(path, text, rel))
        for m in WIKILINK_RE.finditer(text):
            raw = m.group(1)
            if r"\|" in raw or raw.endswith(".md") or raw.startswith("/"):
                issues["bad-link-formatting"].append(f"{rel}: [[{raw}]]")
            stem = target_stem(raw)
            if stem and stem not in stems:
                issues["unresolved-links"].append(f"{rel}: [[{raw}]]")
        for lang, body in CODE_FENCE_RE.findall(text):
            lang = (lang or "").lower()
            if lang in {"", "text", "markdown", "latex"} and any(h in body for h in MATH_HINTS):
                issues["math-formatting"].append(f"{rel}: math-like content in ```{lang or 'plain'} fence")
        if any(folder in path.parts for folder in DURABLE_FOLDERS):
            if "source_trail:" not in text and "origin_trail:" not in text:
                issues["missing-source-trail"].append(str(rel))
        if "07 Index Notes" in path.parts:
            body = text.split("---")[-1].strip() if text.startswith("---") else text.strip()
            link_count = len(WIKILINK_RE.findall(body))
            if link_count == 0:
                issues["empty-index-notes"].append(str(rel))

    # Raw inbox unresolved links are reported separately and do not count as durable graph issues.
    for path in iter_md(root, include_inbox=True):
        if RAW_INBOX_ROOT not in path.parts:
            continue
        text = read(path)
        rel = path.relative_to(root)
        for m in WIKILINK_RE.finditer(text):
            raw = m.group(1)
            stem = target_stem(raw)
            if stem and stem not in stems:
                issues["raw-inbox-unresolved-links"].append(f"{rel}: [[{raw}]]")

    return issues


def write_review_queue(root: Path, issues: dict[str, list[str]]) -> None:
    rq = root / "Logs" / "Review Queue"
    rq.mkdir(parents=True, exist_ok=True)
    for name, items in issues.items():
        p = rq / f"{name}.md"
        if items:
            body = "\n".join(f"- {item}" for item in items)
        else:
            body = "- None"
        p.write_text(f"# {name.replace('-', ' ').title()}\n\n{body}\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root)
    issues = audit(root)
    write_review_queue(root, issues)
    total = sum(len(v) for v in issues.values())
    print(f"Audit complete. Issues: {total}")
    for k, v in issues.items():
        print(f"  {k}: {len(v)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
