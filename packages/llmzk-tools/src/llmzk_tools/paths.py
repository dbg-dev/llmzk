"""Shared vault path helpers: markdown iteration, title indexing, and link-list fields.

Consolidates the 3x duplicated iter_md/iter_markdown, markdown_note_title,
build_title_locations, and preferred_durable_path implementations.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Iterable

from llmzk_tools.config import CONTENT_ROOTS, DURABLE_ROOTS

LINK_LIST_FIELDS = {
    "source_trail",
    "origin_trail",
    "connects",
    "derived_from",
    "updates",
    "related",
}

SKIP_DIRS = {".venv", ".git", "__pycache__", "__MACOSX"}

RAW_INBOX_ROOT = "00 Inbox"


def iter_markdown(root: Path) -> Iterable[Path]:
    """Yield all .md files under root, skipping ignored directories."""
    for path in root.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def iter_md(root: Path, *, include_inbox: bool = False) -> Iterable[Path]:
    """Yield .md files in vault content roots, skipping README and ignored dirs.

    Raw inbox is excluded by default so it does not pollute unresolved-link
    queues. Set include_inbox=True to include 00 Inbox/.
    """
    content_roots = set(CONTENT_ROOTS)
    if include_inbox:
        content_roots.add(RAW_INBOX_ROOT)
    for p in iter_markdown(root):
        try:
            rel = p.relative_to(root)
        except ValueError:
            continue
        if not rel.parts or rel.parts[0] not in content_roots:
            continue
        if p.name.lower() == "readme.md":
            continue
        yield p


def markdown_note_title(path: Path) -> str:
    """Return an Obsidian note title from a Markdown file path.

    Avoid ``Path.stem`` here because note titles can legitimately contain
    periods such as ``w.r.t.``. We only want to remove the final Markdown
    suffix, not reinterpret parts of the title as file extensions.
    """
    name = path.name
    return name[:-3] if name.endswith(".md") else name


def build_title_locations(root: Path) -> dict[str, list[Path]]:
    """Build a title-to-paths index from vault content roots."""
    locations: dict[str, list[Path]] = defaultdict(list)
    for path in iter_md(root, include_inbox=False):
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        locations[markdown_note_title(path)].append(rel)
    return dict(locations)


def is_fleeting(rel: Path) -> bool:
    return str(rel).startswith("00 Fleeting Notes/")


def is_durable(rel: Path) -> bool:
    return bool(rel.parts and rel.parts[0] in DURABLE_ROOTS)


def preferred_durable_path(
    title: str, locations: dict[str, list[Path]] | None
) -> str | None:
    """When a title exists in both fleeting and durable notes, return the durable path.

    Prefers 04 Concept Notes/ when present, otherwise the first durable path.
    Returns None if there is no fleeting/durable ambiguity.
    """
    if not locations:
        return None
    locs = locations.get(title, [])
    has_fleeting = any(is_fleeting(loc) for loc in locs)
    durable = [loc for loc in locs if is_durable(loc)]
    if not has_fleeting or not durable:
        return None
    durable = sorted(
        durable, key=lambda loc: (0 if str(loc).startswith("04 Concept Notes/") else 1, str(loc))
    )
    rel = durable[0]
    text = str(rel)
    return text[:-3] if text.endswith(".md") else text
