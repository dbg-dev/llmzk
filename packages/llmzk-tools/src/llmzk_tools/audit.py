#!/usr/bin/env python3
"""Lightweight audit for llmzk vaults."""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path, PurePosixPath
from typing import Any

import tyro
import yaml

from llmzk_tools.config import DURABLE_ROOTS, LlmzkConfig, load_config, local_markdown_path
from llmzk_tools.frontmatter import split_frontmatter_raw as split_frontmatter
from llmzk_tools.paths import (
    LINK_LIST_FIELDS,
    RAW_INBOX_ROOT,
    iter_md,
    build_title_locations as title_locations,
)
from llmzk_tools.wikilink import (
    WIKILINK_RE,
    strip_wikilink_target,
    target_stem,
    is_local_heading_target,
    is_exact_path_target,
)

CODE_FENCE_RE = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)
MATH_HINTS = [r"\frac", r"\partial", r"\delta", r"\nabla", r"\odot", r"\sum", r"\begin{aligned}"]
DURABLE_FOLDERS = ["03 Permanent Notes", "04 Concept Notes", "05 Bridge Notes", "06 Contradiction Notes"]
# Path-qualified links are resolved by llmzk_tools.config so they can
# optionally include the instance vault-relative prefix.


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def exact_target_path(raw: str, config: LlmzkConfig) -> PurePosixPath | None:
    """Return an llmzk-root-relative Markdown path for a path-qualified wikilink.

    Path-qualified links may be written either relative to the llmzk instance
    root (``04 Concept Notes/X``) or relative to the outer Obsidian vault when
    ``vault_relative_prefix`` is configured (``AI/04 Concept Notes/X``).
    Unknown prefixes still fail instead of silently resolving by basename.
    """
    target = strip_wikilink_target(raw)
    if not target or "/" not in target:
        return None
    local_target = config.to_local_target(target)
    return local_markdown_path(local_target)


def wikilink_resolves(root: Path, raw: str, locations: dict[str, list[Path]], config: LlmzkConfig) -> bool:
    if is_local_heading_target(raw):
        return True
    exact = exact_target_path(raw, config)
    if exact is not None:
        return (root / Path(*exact.parts)).is_file()
    if is_exact_path_target(raw):
        return False
    title = target_stem(raw)
    return bool(title and title in locations)


def has_nested_singleton_list(value: Any) -> bool:
    if isinstance(value, list):
        if any(isinstance(item, list) for item in value):
            return True
        return any(has_nested_singleton_list(item) for item in value)
    return False


def _duplicate_fleeting_and_durable(title: str, locations: dict[str, list[Path]]) -> bool:
    locs = locations.get(title, [])
    has_fleeting = any(str(loc).startswith("00 Fleeting Notes/") for loc in locs)
    has_durable = any(loc.parts and loc.parts[0] in DURABLE_ROOTS for loc in locs)
    return has_fleeting and has_durable


def audit_frontmatter(path: Path, text: str, rel: Path, locations: dict[str, list[Path]], config: LlmzkConfig) -> list[str]:
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
            issues.append(f"{rel}: `{field}` has nested list formatting; run llmzk fix-frontmatter")
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
                    if field == "origin_trail" and item.startswith("[[") and item.endswith("]]" ):
                        target = config.to_local_target(strip_wikilink_target(item[2:-2]))
                        title = target_stem(target)
                        if _duplicate_fleeting_and_durable(title, locations) and "/" not in target:
                            issues.append(
                                f"{rel}: `origin_trail` should path-qualify fleeting source for duplicate title: {item!r}"
                            )
    return issues


def duplicate_title_issues(locations: dict[str, list[Path]]) -> list[str]:
    issues: list[str] = []
    for title, locs in sorted(locations.items()):
        if len(locs) <= 1:
            continue
        has_fleeting = any(str(loc).startswith("00 Fleeting Notes/") for loc in locs)
        has_durable = any(loc.parts and loc.parts[0] in DURABLE_ROOTS for loc in locs)
        if not (has_fleeting and has_durable):
            continue
        rendered = "; ".join(str(loc) for loc in sorted(locs))
        issues.append(f"{title}: duplicate title across fleeting and durable notes -> {rendered}")
    return issues


def ambiguous_link_issue(rel: Path, raw: str, locations: dict[str, list[Path]]) -> str | None:
    """Warn when a durable note links by basename to a duplicate fleeting/durable title."""
    target = strip_wikilink_target(raw)
    if "/" in target:
        return None
    title = target_stem(raw)
    if not _duplicate_fleeting_and_durable(title, locations):
        return None
    return f"{rel}: [[{raw}]] should be path-qualified because title also exists in 00 Fleeting Notes"


def audit(root: Path) -> dict[str, list[str]]:
    config = load_config(root)
    locations = title_locations(root)
    issues: dict[str, list[str]] = {
        "bad-link-formatting": [],
        "unresolved-links": [],
        "ambiguous-links": [],
        "raw-inbox-unresolved-links": [],
        "math-formatting": [],
        "frontmatter-issues": [],
        "missing-source-trail": [],
        "empty-index-notes": [],
        "duplicate-note-titles": duplicate_title_issues(locations),
    }

    for path in iter_md(root, include_inbox=False):
        text = read(path)
        rel = path.relative_to(root)
        issues["frontmatter-issues"].extend(audit_frontmatter(path, text, rel, locations, config))
        for m in WIKILINK_RE.finditer(text):
            raw = m.group(1)
            if r"\|" in raw or raw.endswith(".md") or raw.startswith("/"):
                issues["bad-link-formatting"].append(f"{rel}: [[{raw}]]")
            if not wikilink_resolves(root, raw, locations, config):
                issues["unresolved-links"].append(f"{rel}: [[{raw}]]")
            if rel.parts and rel.parts[0] in DURABLE_ROOTS:
                issue = ambiguous_link_issue(rel, raw, locations)
                if issue:
                    issues["ambiguous-links"].append(issue)
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
            if not wikilink_resolves(root, raw, locations, config):
                issues["raw-inbox-unresolved-links"].append(f"{rel}: [[{raw}]]")

    return issues


def write_review_queue(root: Path, issues: dict[str, list[str]]) -> None:
    rq = root / "Logs" / "Review Queue"
    rq.mkdir(parents=True, exist_ok=True)

    # Review Queue is machine-generated audit output. Clear previous markdown
    # reports before writing the current set so stale false positives do not
    # survive after the graph has been fixed.
    for old_report in rq.glob("*.md"):
        old_report.unlink()

    generated_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    for name, items in issues.items():
        p = rq / f"{name}.md"
        if items:
            body = "\n".join(f"- {item}" for item in items)
        else:
            body = "- None"
        title = name.replace("-", " ").title()
        p.write_text(
            "---\n"
            "type: audit_report\n"
            f"generated_at: {generated_at!r}\n"
            f"issue_type: {name!r}\n"
            f"issue_count: {len(items)}\n"
            "---\n\n"
            f"# {title}\n\n{body}\n",
            encoding="utf-8",
        )


def run(root: tyro.conf.Positional[Path] = Path(".")) -> int:
    """Audit an llmzk vault and write review-queue files."""
    issues = audit(root)
    write_review_queue(root, issues)
    total = sum(len(v) for v in issues.values())
    print(f"Audit complete. Issues: {total}")
    for k, v in issues.items():
        print(f"  {k}: {len(v)}")
    return 0


def main() -> int:
    return tyro.cli(run)


if __name__ == "__main__":
    raise SystemExit(main())
