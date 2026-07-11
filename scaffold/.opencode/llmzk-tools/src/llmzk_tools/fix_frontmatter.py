#!/usr/bin/env python3
"""Fix common llmzk frontmatter problems.

This script is intentionally conservative. It fixes:
- nested YAML lists such as `- - - Source` in link-list fields;
- bare note names in link-list fields by converting them to quoted wikilinks;
- escaped Obsidian pipe aliases in frontmatter wikilinks.

It does not rewrite the body of the note.
"""
from __future__ import annotations

import tyro
import re
from pathlib import Path
from typing import Any

import yaml

LINK_LIST_FIELDS = {
    "source_trail",
    "origin_trail",
    "connects",
    "derived_from",
    "updates",
    "related",
}

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def split_frontmatter(text: str) -> tuple[str | None, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, text
    return match.group(1), text[match.end():]


def flatten_singletons(value: Any) -> Any:
    """Flatten accidental nested singleton lists from malformed YAML bullets."""
    while isinstance(value, list) and len(value) == 1 and isinstance(value[0], list):
        value = value[0]
    if isinstance(value, list):
        return [flatten_singletons(v) for v in value]
    return value


def clean_wikilink_text(value: str) -> str:
    value = value.strip()
    value = value.replace(r"\|", "|")
    if value.startswith("[[") and value.endswith("]]"):
        inner = value[2:-2]
    else:
        inner = value
    # Remove .md suffix from target side, preserving aliases/headings.
    if "|" in inner:
        target, alias = inner.split("|", 1)
        inner = f"{clean_target(target)}|{alias.strip()}"
    else:
        inner = clean_target(inner)
    return f"[[{inner}]]"


def clean_target(target: str) -> str:
    target = target.strip()
    if "#" in target:
        note, heading = target.split("#", 1)
        note = clean_target(note)
        return f"{note}#{heading.strip()}"
    if target.endswith(".md"):
        target = target[:-3]
    # Strip project-prefixed vault paths from common folders.
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
    return target.strip()


def normalize_link_list(value: Any) -> list[str]:
    value = flatten_singletons(value)
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        value = [value]

    out: list[str] = []
    for item in value:
        item = flatten_singletons(item)
        if isinstance(item, list):
            # If there is still a nested list, add each scalar item.
            for sub in item:
                if sub not in (None, ""):
                    out.append(clean_wikilink_text(str(sub)))
        elif item not in (None, ""):
            out.append(clean_wikilink_text(str(item)))
    # Preserve order, remove duplicates.
    seen: set[str] = set()
    deduped: list[str] = []
    for item in out:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped


def quote_yaml_string(s: str) -> str:
    escaped = s.replace('"', '\\"')
    return f'"{escaped}"'


def format_scalar(value: Any) -> str:
    if isinstance(value, str):
        value = value.replace(r"\|", "|")
        if "[[" in value or ":" in value or "#" in value or "|" in value:
            return quote_yaml_string(value)
        return value
    if value is None:
        return ""
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


def dump_frontmatter(data: dict[str, Any]) -> str:
    lines: list[str] = []
    for key, value in data.items():
        if key in LINK_LIST_FIELDS:
            items = normalize_link_list(value)
            lines.append(f"{key}:")
            if items:
                for item in items:
                    lines.append(f"  - {quote_yaml_string(item)}")
            else:
                lines.append("  []")
        else:
            dump_yaml_value(lines, str(key), value)
    return "\n".join(lines)


def fix_text(text: str) -> tuple[str, bool, str | None]:
    fm, body = split_frontmatter(text)
    if fm is None:
        return text, False, None
    try:
        data = yaml.safe_load(fm) or {}
    except yaml.YAMLError as exc:
        return text, False, f"YAML parse error: {exc}"
    if not isinstance(data, dict):
        return text, False, "Frontmatter is not a mapping"
    # Normalize link-list fields explicitly.
    for key in list(data):
        if key in LINK_LIST_FIELDS:
            data[key] = normalize_link_list(data.get(key))
    new_fm = dump_frontmatter(data)
    new_text = f"---\n{new_fm}\n---\n{body}"
    return new_text, new_text != text, None


def iter_markdown(root: Path):
    skip = {".venv", ".git", "__pycache__"}
    for path in root.rglob("*.md"):
        if any(part in skip for part in path.parts):
            continue
        yield path


def run(root: Path, apply: bool = False) -> int:
    """Normalize llmzk frontmatter link-list formatting."""
    changed = 0
    errors = 0
    for path in iter_markdown(root):
        text = path.read_text(encoding="utf-8")
        new_text, did_change, error = fix_text(text)
        if error:
            errors += 1
            print(f"{path}: {error}")
            continue
        if did_change:
            changed += 1
            print(f"{path}: frontmatter would be normalized" if not apply else f"{path}: normalized")
            if apply:
                path.write_text(new_text, encoding="utf-8")
    if changed == 0 and errors == 0:
        print("No frontmatter normalization changes found.")
    elif not apply:
        print(f"Found {changed} frontmatter file(s) to normalize. Re-run with --apply to modify files.")
    else:
        print(f"Normalized {changed} frontmatter file(s).")
    if errors:
        print(f"Encountered {errors} frontmatter parse error(s).")
        return 1
    return 0


def main() -> int:
    return tyro.cli(run)


if __name__ == "__main__":
    raise SystemExit(main())
