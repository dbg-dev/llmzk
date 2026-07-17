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

from pathlib import Path
from typing import Any

import tyro
import yaml

from llmzk_tools.config import LlmzkConfig, load_config
from llmzk_tools.frontmatter import (
    split_frontmatter_raw as split_frontmatter,
    quote_yaml_string,
    dump_yaml_value,
)
from llmzk_tools.paths import (
    LINK_LIST_FIELDS,
    iter_markdown,
    markdown_note_title,
    build_title_locations,
    preferred_durable_path,
)
from llmzk_tools.wikilink import split_link_inner


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


def clean_wikilink_text(value: str, *, field: str | None = None, fleeting_titles: dict[str, str] | None = None, title_locations: dict[str, list[Path]] | None = None, config: LlmzkConfig | None = None) -> str:
    value = value.strip().replace(r"\|", "|")
    if value.startswith("[[") and value.endswith("]]" ):
        inner = value[2:-2]
    else:
        inner = value
    target, alias = split_link_inner(inner)
    cleaned_target = clean_target(target, preserve_fleeting_path=(field == "origin_trail"), config=config)

    title = cleaned_target.rsplit("/", 1)[-1]
    if field == "origin_trail" and fleeting_titles:
        if title in fleeting_titles:
            # If a promoted durable note has the same title as the fleeting source,
            # keep the source path explicit and alias it back to the readable title.
            cleaned_target = fleeting_titles[title]
            alias = alias or title
    elif "/" not in cleaned_target:
        durable_path = preferred_durable_path(title, title_locations)
        if durable_path:
            cleaned_target = durable_path
            alias = alias or title

    if config:
        cleaned_target = config.render_target(cleaned_target)
    if alias:
        return f"[[{cleaned_target}|{alias}]]"
    return f"[[{cleaned_target}]]"


def clean_target(target: str, *, preserve_fleeting_path: bool = False, config: LlmzkConfig | None = None) -> str:
    target = target.strip()
    if "#" in target:
        note, heading = target.split("#", 1)
        note = clean_target(note, preserve_fleeting_path=preserve_fleeting_path, config=config)
        return f"{note}#{heading.strip()}"
    if target.endswith(".md"):
        target = target[:-3]

    if config:
        target = config.to_local_target(target)

    # Preserve explicit fleeting paths in origin_trail so provenance links do not
    # become ambiguous when a durable note has the same basename.
    if preserve_fleeting_path and target.startswith("00 Fleeting Notes/"):
        return target[:-3] if target.endswith(".md") else target

    # Do not blindly strip arbitrary project prefixes here. Unknown prefixes
    # should remain visible so audit can flag them. Configured vault-relative
    # prefixes are stripped above by config.to_local_target().
    return target.strip().strip("/")


def normalize_link_list(value: Any, *, field: str | None = None, fleeting_titles: dict[str, str] | None = None, title_locations: dict[str, list[Path]] | None = None, config: LlmzkConfig | None = None) -> list[str]:
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
                    out.append(clean_wikilink_text(str(sub), field=field, fleeting_titles=fleeting_titles, title_locations=title_locations, config=config))
        elif item not in (None, ""):
            out.append(clean_wikilink_text(str(item), field=field, fleeting_titles=fleeting_titles, title_locations=title_locations, config=config))
    # Preserve order, remove duplicates.
    seen: set[str] = set()
    deduped: list[str] = []
    for item in out:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped


def dump_frontmatter(data: dict[str, Any], *, fleeting_titles: dict[str, str] | None = None, title_locations: dict[str, list[Path]] | None = None, config: LlmzkConfig | None = None) -> str:
    lines: list[str] = []
    for key, value in data.items():
        if key in LINK_LIST_FIELDS:
            items = normalize_link_list(value, field=key, fleeting_titles=fleeting_titles, title_locations=title_locations, config=config)
            lines.append(f"{key}:")
            if items:
                for item in items:
                    lines.append(f"  - {quote_yaml_string(item)}")
            else:
                lines.append("  []")
        else:
            dump_yaml_value(lines, str(key), value)
    return "\n".join(lines)


def fix_text(text: str, *, fleeting_titles: dict[str, str] | None = None, title_locations: dict[str, list[Path]] | None = None, config: LlmzkConfig | None = None) -> tuple[str, bool, str | None]:
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
            data[key] = normalize_link_list(data.get(key), field=key, fleeting_titles=fleeting_titles, title_locations=title_locations, config=config)
    new_fm = dump_frontmatter(data, fleeting_titles=fleeting_titles, title_locations=title_locations, config=config)
    new_text = f"---\n{new_fm}\n---\n{body}"
    return new_text, new_text != text, None


def run(root: tyro.conf.Positional[Path] = Path("."), apply: bool = False) -> int:
    """Normalize llmzk frontmatter link-list formatting."""
    root = root.expanduser().resolve()
    fleeting_titles = build_fleeting_titles(root)
    title_locations = build_title_locations(root)
    config = load_config(root)
    changed = 0
    errors = 0
    for path in iter_markdown(root):
        text = path.read_text(encoding="utf-8")
        new_text, did_change, error = fix_text(text, fleeting_titles=fleeting_titles, title_locations=title_locations, config=config)
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
