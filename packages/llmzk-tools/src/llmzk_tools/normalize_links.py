#!/usr/bin/env python3
"""Normalize obvious Obsidian wikilink formatting issues.

This script is intentionally mechanical. It does not create notes.
"""
from __future__ import annotations

from pathlib import Path
import re

import tyro

from llmzk_tools.config import LlmzkConfig, load_config
from llmzk_tools.paths import (
    iter_markdown,
    build_title_locations,
    preferred_durable_path,
)
from llmzk_tools.wikilink import WIKILINK_RE


def normalize_target(target: str, locations: dict[str, list[Path]] | None = None, config: LlmzkConfig | None = None) -> str:
    target = target.replace(r"\|", "|")
    if "|" in target:
        left, alias = target.split("|", 1)
        left = _clean_path(left, config=config)
        if "/" not in left:
            left = preferred_durable_path(left, locations) or left
        if config:
            left = config.render_target(left)
        return f"{left}|{alias}"
    cleaned = _clean_path(target, config=config)
    if "/" not in cleaned:
        cleaned = preferred_durable_path(cleaned, locations) or cleaned
    if config:
        cleaned = config.render_target(cleaned)
    return cleaned


def _clean_path(target: str, config: LlmzkConfig | None = None) -> str:
    target = target.strip().strip("/")
    if target.endswith(".md"):
        target = target[:-3]
    if config:
        target = config.to_local_target(target)
    return target.strip().strip("/")


def split_frontmatter(text: str) -> tuple[str, str]:
    """Split YAML frontmatter from body, preserving the frontmatter text.

    Wikilinks in frontmatter are handled by `llmzk fix-frontmatter`. The body
    link normalizer deliberately leaves frontmatter untouched so provenance links
    such as `[[00 Fleeting Notes/Example|Example]]` are not stripped back to an
    ambiguous basename.
    """
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---", 4)
    if end < 0:
        return "", text
    close_end = end + len("\n---")
    if close_end < len(text) and text[close_end:close_end + 1] == "\n":
        close_end += 1
    return text[:close_end], text[close_end:]


def normalize_text(text: str, locations: dict[str, list[Path]] | None = None, config: LlmzkConfig | None = None) -> tuple[str, list[tuple[str, str]]]:
    """Normalize wikilinks outside frontmatter and fenced code blocks.

    Documentation often contains examples of bad links. Do not rewrite code-fenced
    examples because those examples are intentionally literal. Do not rewrite
    YAML frontmatter because llmzk-specific provenance fields need field-aware
    handling.
    """
    frontmatter, body = split_frontmatter(text)
    changes: list[tuple[str, str]] = []

    def repl(match: re.Match[str]) -> str:
        old = match.group(1)
        new = normalize_target(old, locations, config)
        if old != new:
            changes.append((old, new))
        return f"[[{new}]]"

    out: list[str] = []
    in_fence = False
    fence_marker = ""
    for line in body.splitlines(keepends=True):
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
    return frontmatter + "".join(out), changes


def run(root: tyro.conf.Positional[Path] = Path("."), apply: bool = False, dry_run: bool = False) -> int:
    """Normalize escaped-pipe and project-prefixed wikilinks outside fenced code blocks."""
    # `dry_run` is retained for command compatibility; dry-run is the default unless `apply` is set.
    _ = dry_run
    total = 0
    locations = build_title_locations(root)
    config = load_config(root)
    for path in iter_markdown(root):
        text = path.read_text(encoding="utf-8")
        new_text, changes = normalize_text(text, locations, config)
        if changes:
            total += len(changes)
            print(f"{path}:")
            for old, new in changes:
                print(f"  [[{old}]] -> [[{new}]]")
            if apply:
                path.write_text(new_text, encoding="utf-8")
    if total == 0:
        print("No link normalization changes found.")
    elif not apply:
        print(f"Found {total} link normalization change(s). Re-run with --apply to modify files.")
    else:
        print(f"Applied {total} link normalization change(s).")
    return 0


def main() -> int:
    return tyro.cli(run)


if __name__ == "__main__":
    raise SystemExit(main())
