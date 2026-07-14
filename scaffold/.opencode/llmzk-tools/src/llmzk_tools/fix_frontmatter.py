#!/usr/bin/env python3
"""Fix common llmzk frontmatter problems.

This script is intentionally conservative. It fixes:
- nested YAML lists such as `- - - Source` in link-list fields;
- bare note names in link-list fields by converting them to quoted wikilinks;
- escaped Obsidian pipe aliases in frontmatter wikilinks;
- ambiguous `origin_trail` references to fleeting notes when a durable note has the same title.

It does not rewrite the body of the note.
"""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from typing import Any

import tyro
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
CONTENT_FOLDERS = [
    "00 Inbox/", "00 Fleeting Notes/", "01 Sources/", "02 Literature Notes/",
    "03 Permanent Notes/", "04 Concept Notes/", "05 Bridge Notes/",
    "06 Contradiction Notes/", "07 Index Notes/", "08 Wiki Articles/", "09 Media/",
    "Logs/Passports/", "Logs/Decision Logs/", "Logs/Review Queue/", "Logs/Candidate Reviews/",
]


def split_frontmatter(text: str) -> tuple[str | None, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, text
    return match.group(1), text[match.end():]


def markdown_note_title(path: Path) -> str:
    name = path.name
    return name[:-3] if name.endswith(".md") else name


def build_fleeting_titles(root: Path) -> dict[str, str]:
    folder = root / "00 Fleeting Notes"
    if not folder.exists():
        return {}
    out: dict[str, str] = {}
    for path in folder.glob("*.md"):
        title = markdown_note_title(path)
        out[title] = f"00 Fleeting Notes/{title}"
    return out


def flatten_singletons(value: Any) -> Any:
    """Flatten accidental nested singleton lists from malformed YAML bullets."""
    while isinstance(value, list) and len(value) == 1 and isinstance(value[0], list):
        value = value[0]
    if isinstance(value, list):
        return [flatten_singletons(v) for v in value]
    return value


def split_link_inner(inner: str) -> tuple[str, str | None]:
    inner = inner.strip().replace(r"\|", "|")
    if "|" in inner:
        target, alias = inner.split("|", 1)
        return target.strip(), alias.strip()
    return inner.strip(), None


def clean_wikilink_text(value: str, *, field: str | None = None, fleeting_titles: dict[str, str] | None = None) -> str:
    value = value.strip().replace(r"\|", "|")
    if value.startswith("[[") and value.endswith("]]" ):
        inner = value[2:-2]
    else:
        inner = value
    target, alias = split_link_inner(inner)
    cleaned_target = clean_target(target, preserve_fleeting_path=(field == "origin_trail"))

    if field == "origin_trail" and fleeting_titles:
        title = cleaned_target.rsplit("/", 1)[-1]
        if title in fleeting_titles:
            # If a promoted durable note has the same title as the fleeting source,
            # keep the source path explicit and alias it back to the readable title.
            cleaned_target = fleeting_titles[title]
            alias = alias or title

    if alias:
        return f"[[{cleaned_target}|{alias}]]"
    return f"[[{cleaned_target}]]"


def clean_target(target: str, *, preserve_fleeting_path: bool = False) -> str:
    target = target.strip()
    if "#" in target:
        note, heading = target.split("#", 1)
        note = clean_target(note, preserve_fleeting_path=preserve_fleeting_path)
        return f"{note}#{heading.strip()}"
    if target.endswith(".md"):
        target = target[:-3]

    # Preserve explicit fleeting paths in origin_trail so provenance links do not
    # become ambiguous when a durable note has the same basename.
    if preserve_fleeting_path:
        idx = target.find("00 Fleeting Notes/")
        if idx >= 0:
            kept = target[idx:]
            return kept[:-3] if kept.endswith(".md") else kept

    # Strip project-prefixed vault paths from common folders for ordinary links.
    for folder in CONTENT_FOLDERS:
        idx = target.find(folder)
        if idx >= 0:
            target = target[idx + len(folder):]
            if target.endswith(".md"):
                target = target[:-3]
            break
    return target.strip()


def normalize_link_list(value: Any, *, field: str | None = None, fleeting_titles: dict[str, str] | None = None) -> list[str]:
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
                    out.append(clean_wikilink_text(str(sub), field=field, fleeting_titles=fleeting_titles))
        elif item not in (None, ""):
            out.append(clean_wikilink_text(str(item), field=field, fleeting_titles=fleeting_titles))
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


def is_date_like(value: str) -> bool:
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}(?:T|$|\s)", value))


def format_scalar(value: Any) -> str:
    if isinstance(value, dt.datetime):
        value = value.isoformat(timespec="seconds")
    elif isinstance(value, dt.date):
        value = value.isoformat()
    if isinstance(value, str):
        value = value.replace(r"\|", "|")
        if "[[" in value or ":" in value or "#" in value or "|" in value or "/" in value or is_date_like(value):
            return quote_yaml_string(value)
        return value
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
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


def dump_frontmatter(data: dict[str, Any], *, fleeting_titles: dict[str, str] | None = None) -> str:
    lines: list[str] = []
    for key, value in data.items():
        if key in LINK_LIST_FIELDS:
            items = normalize_link_list(value, field=key, fleeting_titles=fleeting_titles)
            lines.append(f"{key}:")
            if items:
                for item in items:
                    lines.append(f"  - {quote_yaml_string(item)}")
            else:
                lines.append("  []")
        else:
            dump_yaml_value(lines, str(key), value)
    return "\n".join(lines)


def fix_text(text: str, *, fleeting_titles: dict[str, str] | None = None) -> tuple[str, bool, str | None]:
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
            data[key] = normalize_link_list(data.get(key), field=key, fleeting_titles=fleeting_titles)
    new_fm = dump_frontmatter(data, fleeting_titles=fleeting_titles)
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
    root = root.expanduser().resolve()
    fleeting_titles = build_fleeting_titles(root)
    changed = 0
    errors = 0
    for path in iter_markdown(root):
        text = path.read_text(encoding="utf-8")
        new_text, did_change, error = fix_text(text, fleeting_titles=fleeting_titles)
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
