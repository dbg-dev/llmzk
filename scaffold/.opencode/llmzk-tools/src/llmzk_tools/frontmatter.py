"""Shared frontmatter parsing and YAML dumping helpers.

These utilities are used by audit, fix_frontmatter, benchmark, and review
modules. They standardise the three different split_frontmatter return shapes
that previously existed into two canonical functions, and consolidate the YAML
scalar dumping helpers that had drifted between fix_frontmatter and review.
"""
from __future__ import annotations

import datetime as dt
import re
from typing import Any

import yaml

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)


def split_frontmatter_raw(text: str) -> tuple[str | None, str]:
    """Split frontmatter from body, returning raw frontmatter text.

    Returns (raw_fm_text, body) where raw_fm_text is None if there is no
    frontmatter.
    """
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, text
    return match.group(1), text[match.end():]


def parse_frontmatter(text: str) -> tuple[dict, str, str | None]:
    """Split and parse frontmatter, returning (data, body, raw_fm_text).

    On YAML parse errors, returns ({}, body_after_match, raw_fm_text).
    """
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text, None
    raw = match.group(1)
    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError:
        return {}, text[match.end():], raw
    return data if isinstance(data, dict) else {}, text[match.end():], raw


def quote_yaml_string(s: str) -> str:
    escaped = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def is_date_like(value: str) -> bool:
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}(?:T|$|\s)", value))


def _would_be_reinterpreted(value: str) -> bool:
    """Check if yaml.safe_load would parse this bare string as a non-string type.

    Guards against YAML 1.1 boolean keywords (yes/no/on/off/true/false),
    null keywords (null/Null/NULL/~), and numeric-looking strings (123, 0x1f,
    3.14) that would silently change type on round-trip.
    """
    try:
        parsed = yaml.safe_load(value)
    except yaml.YAMLError:
        return True
    return not isinstance(parsed, str) or parsed != value


def format_scalar(value: Any) -> str:
    if isinstance(value, dt.datetime):
        value = value.isoformat(timespec="seconds")
    elif isinstance(value, dt.date):
        value = value.isoformat()
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return ""
    if isinstance(value, str):
        value = value.replace(r"\|", "|")
        if is_date_like(value) or ":" in value or "#" in value or "[" in value or "]" in value or "/" in value or "|" in value or _would_be_reinterpreted(value):
            return quote_yaml_string(value)
        return value
    return str(value)


def dump_yaml_value(lines: list[str], key: str, value: Any, indent: int = 0) -> None:
    pad = " " * indent
    if isinstance(value, dict):
        lines.append(f"{pad}{key}:")
        for child_key, child_value in value.items():
            dump_yaml_value(lines, str(child_key), child_value, indent + 2)
    elif isinstance(value, list):
        if not value:
            lines.append(f"{pad}{key}: []")
        else:
            lines.append(f"{pad}{key}:")
            for item in value:
                if isinstance(item, dict):
                    lines.append(f"{pad}  -")
                    for child_key, child_value in item.items():
                        dump_yaml_value(lines, str(child_key), child_value, indent + 4)
                else:
                    lines.append(f"{pad}  - {format_scalar(item)}")
    elif value is None:
        lines.append(f"{pad}{key}:")
    else:
        lines.append(f"{pad}{key}: {format_scalar(value)}")
