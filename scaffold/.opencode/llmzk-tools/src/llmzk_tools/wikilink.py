"""Shared wikilink parsing and target cleaning helpers.

Consolidates the 3x duplicated WIKILINK_RE and the scattered target-cleaning
functions across audit, normalize_links, fix_frontmatter, and benchmark.
"""
from __future__ import annotations

import re

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def strip_wikilink_target(raw: str) -> str:
    """Core wikilink target cleaning: strip alias, heading, slashes, and .md suffix."""
    target = raw.replace(r"\|", "|")
    target = target.split("|", 1)[0]
    target = target.split("#", 1)[0]
    target = target.strip().strip("/")
    if target.endswith(".md"):
        target = target[:-3]
    return target.strip()


def target_stem(target: str) -> str:
    """Return the comparable note title from raw wikilink target text.

    Wikilinks are not filesystem paths. Do not call ``Path(target).stem`` on
    raw wikilink targets, because titles such as ``w.r.t. weighted input``
    would be truncated as if they had a suffix.
    """
    target = strip_wikilink_target(target)
    if "/" in target:
        target = target.rsplit("/", 1)[-1]
    return target.strip()


def split_link_inner(inner: str) -> tuple[str, str | None]:
    """Split a wikilink inner string into (target, alias|None)."""
    inner = inner.strip().replace(r"\|", "|")
    if "|" in inner:
        target, alias = inner.split("|", 1)
        return target.strip(), alias.strip()
    return inner.strip(), None


def is_local_heading_target(raw: str) -> bool:
    """Check if a wikilink target is a local heading reference like [[#Section]]."""
    inner = raw.replace(r"\|", "|").split("|", 1)[0].strip()
    return inner.startswith("#")


def is_exact_path_target(raw: str) -> bool:
    """Check if a wikilink target contains a path separator."""
    return "/" in strip_wikilink_target(raw)
