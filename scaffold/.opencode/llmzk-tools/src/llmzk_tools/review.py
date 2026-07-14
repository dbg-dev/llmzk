#!/usr/bin/env python3
"""Candidate review helpers for llmzk.

The LLM produces and applies the candidate review; this deterministic helper only
checks that the review artifact is structurally usable and can mark it applied or
rejected after the workflow completes.
"""
from __future__ import annotations

import datetime as dt
import json as json_lib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Literal, Union

import tyro
import yaml

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
CHECKBOX_RE = re.compile(r"^\s*- \[(?P<mark>[ xX])\]\s+(?P<text>.+?)\s*$")
HEADING_RE = re.compile(r"^(?P<hashes>#{2,6})\s+(?P<title>.+?)\s*$")

REQUIRED_SECTIONS = [
    "Source",
    "Proposed notes",
    "Deliberately not created",
    "Reviewer instructions",
    "Reviewer notes",
]

NOTE_TYPE_HEADINGS = [
    "Source notes",
    "Literature notes",
    "Concept notes",
    "Permanent notes",
    "Bridge notes",
    "Contradiction/tension notes",
    "Index notes",
]

VALID_STATUSES = {"proposed", "edited", "applied", "rejected", "superseded"}
VALID_MODES = {"ingest", "promote"}


@dataclass
class Finding:
    level: Literal["ok", "warn", "fail"]
    message: str


@dataclass
class Validate:
    """Validate a candidate review file."""

    review_file: Path
    json: bool = False


@dataclass
class Mark:
    """Mark a candidate review file as applied, rejected, or superseded."""

    review_file: Path
    status: Literal["applied", "rejected", "superseded"] = "applied"


@dataclass
class Normalize:
    """Normalize candidate review frontmatter without changing review body."""

    review_file: Path


Command = Union[
    Annotated[Validate, tyro.conf.subcommand(name="validate")],
    Annotated[Mark, tyro.conf.subcommand(name="mark")],
    Annotated[Normalize, tyro.conf.subcommand(name="normalize")],
]


def split_frontmatter(text: str) -> tuple[dict, str, str | None]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text, None
    raw = match.group(1)
    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError:
        return {}, text[match.end():], raw
    return data if isinstance(data, dict) else {}, text[match.end():], raw


def normalize_frontmatter_value(value):
    if isinstance(value, dt.datetime):
        return value.isoformat(timespec="seconds")
    if isinstance(value, dt.date):
        return value.isoformat()
    if isinstance(value, list):
        return [normalize_frontmatter_value(item) for item in value]
    if isinstance(value, dict):
        return {key: normalize_frontmatter_value(item) for key, item in value.items()}
    return value


def normalize_frontmatter_data(data: dict) -> dict:
    normalized = {key: normalize_frontmatter_value(value) for key, value in data.items()}
    if normalized.get("type") == "candidate_review":
        # Keep booleans as booleans; custom dumper below renders lowercase YAML.
        if isinstance(normalized.get("applied"), str):
            lowered = normalized["applied"].strip().lower()
            if lowered in {"true", "false"}:
                normalized["applied"] = lowered == "true"
    return normalized


def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def quote_yaml_string(value: str) -> str:
    return '"' + value.replace('"', '\"') + '"'


def is_date_like(value: str) -> bool:
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}(?:T|$)", value))


def format_scalar(value) -> str:
    value = normalize_frontmatter_value(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return ""
    if isinstance(value, str):
        if is_date_like(value) or ":" in value or "#" in value or "[" in value or "]" in value or "/" in value:
            return quote_yaml_string(value)
        return value
    return str(value)


def dump_yaml_value(lines: list[str], key: str, value, indent: int = 0) -> None:
    pad = " " * indent
    value = normalize_frontmatter_value(value)
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
                lines.append(f"{pad}  - {format_scalar(item)}")
    else:
        lines.append(f"{pad}{key}: {format_scalar(value)}")


def dump_frontmatter(data: dict, body: str) -> str:
    normalized = normalize_frontmatter_data(data)
    lines: list[str] = []
    for key, value in normalized.items():
        dump_yaml_value(lines, str(key), value)
    raw = "\n".join(lines)
    return f"---\n{raw}\n---\n{body if body.startswith(chr(10)) else chr(10) + body}"


def headings(body: str) -> list[str]:
    found: list[str] = []
    for line in body.splitlines():
        match = HEADING_RE.match(line)
        if match:
            found.append(match.group("title").strip())
    return found


def checkbox_items(body: str) -> list[tuple[bool, str]]:
    items: list[tuple[bool, str]] = []
    for line in body.splitlines():
        match = CHECKBOX_RE.match(line)
        if not match:
            continue
        mark = match.group("mark").lower()
        items.append((mark == "x", match.group("text").strip()))
    return items


def add(findings: list[Finding], level: Literal["ok", "warn", "fail"], message: str) -> None:
    findings.append(Finding(level, message))


def validate_review(path: Path) -> tuple[int, list[Finding]]:
    findings: list[Finding] = []
    if not path.exists():
        return 1, [Finding("fail", f"Candidate review not found: {path}")]
    text = path.read_text(encoding="utf-8")
    data, body, raw_frontmatter = split_frontmatter(text)

    if raw_frontmatter is None:
        add(findings, "fail", "Missing YAML frontmatter")
    else:
        add(findings, "ok", "YAML frontmatter found")

    if data.get("type") == "candidate_review":
        add(findings, "ok", "type is candidate_review")
    else:
        add(findings, "fail", "frontmatter type must be candidate_review")

    status = data.get("status")
    if status in VALID_STATUSES:
        add(findings, "ok", f"status is {status}")
    else:
        add(findings, "fail", f"status must be one of {sorted(VALID_STATUSES)}")

    mode = data.get("mode")
    if mode in VALID_MODES:
        add(findings, "ok", f"mode is {mode}")
    else:
        add(findings, "fail", f"mode must be one of {sorted(VALID_MODES)}")

    inputs = data.get("input") or data.get("inputs")
    if isinstance(inputs, list) and inputs:
        add(findings, "ok", f"input list present ({len(inputs)} item{'s' if len(inputs) != 1 else ''})")
    else:
        add(findings, "fail", "frontmatter input must be a non-empty list")

    h = headings(body)
    for section in REQUIRED_SECTIONS:
        if section in h:
            add(findings, "ok", f"section exists: {section}")
        else:
            add(findings, "fail", f"missing section: {section}")
    for section in NOTE_TYPE_HEADINGS:
        if section in h:
            add(findings, "ok", f"proposed-note subsection exists: {section}")
        else:
            add(findings, "warn", f"missing proposed-note subsection: {section}")

    items = checkbox_items(body)
    approved = [text for checked, text in items if checked]
    rejected = [text for checked, text in items if not checked]
    if items:
        add(findings, "ok", f"checkbox candidates parse ({len(approved)} approved, {len(rejected)} unchecked)")
    else:
        add(findings, "fail", "no parseable checkbox candidates found")
    if not approved:
        add(findings, "warn", "no approved candidates; write-approved would have nothing to create")

    failures = [f for f in findings if f.level == "fail"]
    return (1 if failures else 0), findings


def run_validate(args: Validate) -> int:
    exit_code, findings = validate_review(args.review_file.expanduser())
    if args.json:
        print(json_lib.dumps([f.__dict__ for f in findings], indent=2))
        return exit_code
    print(f"llmzk candidate review validate: {args.review_file}")
    print()
    for finding in findings:
        label = {"ok": "OK", "warn": "WARN", "fail": "FAIL"}[finding.level]
        print(f"[{label}] {finding.message}")
    print()
    print("Review result: " + ("passed" if exit_code == 0 else "failed"))
    return exit_code


def run_mark(args: Mark) -> int:
    path = args.review_file.expanduser()
    if not path.exists():
        raise SystemExit(f"Candidate review not found: {path}")
    text = path.read_text(encoding="utf-8")
    data, body, raw_frontmatter = split_frontmatter(text)
    if raw_frontmatter is None:
        raise SystemExit("Cannot mark review: missing YAML frontmatter")
    if data.get("type") != "candidate_review":
        raise SystemExit("Cannot mark review: frontmatter type must be candidate_review")
    data["status"] = args.status
    timestamp = now_iso()
    data["modified"] = timestamp
    if args.status == "applied":
        data["applied"] = True
        data["applied_at"] = timestamp
    elif args.status == "rejected":
        data["applied"] = False
        data["rejected_at"] = timestamp
    elif args.status == "superseded":
        data["applied"] = False
        data["superseded_at"] = timestamp
    path.write_text(dump_frontmatter(data, body), encoding="utf-8")
    print(f"Marked {path} as {args.status}")
    return 0



def run_normalize(args: Normalize) -> int:
    path = args.review_file.expanduser()
    if not path.exists():
        raise SystemExit(f"Candidate review not found: {path}")
    text = path.read_text(encoding="utf-8")
    data, body, raw_frontmatter = split_frontmatter(text)
    if raw_frontmatter is None:
        raise SystemExit("Cannot normalize review: missing YAML frontmatter")
    if data.get("type") != "candidate_review":
        raise SystemExit("Cannot normalize review: frontmatter type must be candidate_review")
    new_text = dump_frontmatter(data, body)
    path.write_text(new_text, encoding="utf-8")
    print(f"Normalized candidate review frontmatter: {path}")
    return 0

def main() -> int:
    command = tyro.cli(Command)
    if isinstance(command, Validate):
        return run_validate(command)
    if isinstance(command, Mark):
        return run_mark(command)
    if isinstance(command, Normalize):
        return run_normalize(command)
    raise AssertionError(f"Unhandled command: {command!r}")


if __name__ == "__main__":
    raise SystemExit(main())
