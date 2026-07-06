#!/usr/bin/env python3
"""Git safety helpers for llmzk.

These helpers are intentionally small wrappers around Git. They do not replace
normal Git review; they make the llmzk safety workflow easier to invoke from
OpenCode commands.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


def run_git(args: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def repo_root(path: Path) -> Path:
    try:
        out = run_git(["rev-parse", "--show-toplevel"], path).stdout.strip()
        return Path(out)
    except subprocess.CalledProcessError:
        raise SystemExit("Not inside a Git repository. Initialize Git first or run from the vault root.")


def porcelain(root: Path) -> list[str]:
    out = run_git(["status", "--porcelain=v1"], root).stdout
    return [line for line in out.splitlines() if line.strip()]


def cmd_status(args: argparse.Namespace) -> int:
    root = repo_root(Path(args.path).resolve())
    branch = run_git(["branch", "--show-current"], root, check=False).stdout.strip() or "(detached)"
    lines = porcelain(root)
    print(f"Repository: {root}")
    print(f"Branch: {branch}")
    if not lines:
        print("Working tree: clean")
        return 0
    print(f"Working tree: dirty ({len(lines)} changed entries)")
    print()
    for line in lines[: args.limit]:
        print(line)
    if len(lines) > args.limit:
        print(f"... {len(lines) - args.limit} more")
    return 1 if args.fail_if_dirty else 0


def cmd_preflight(args: argparse.Namespace) -> int:
    root = repo_root(Path(args.path).resolve())
    lines = porcelain(root)
    if not lines:
        print("Preflight: clean working tree. Safe to start a broad llmzk run.")
        return 0
    print("Preflight: working tree is dirty.")
    print("Review or commit/revert existing changes before a broad llmzk run, or explicitly allow mixing changes.")
    print()
    for line in lines[: args.limit]:
        print(line)
    if len(lines) > args.limit:
        print(f"... {len(lines) - args.limit} more")
    return 1


def cmd_diff(args: argparse.Namespace) -> int:
    root = repo_root(Path(args.path).resolve())
    if args.stat:
        print(run_git(["diff", "--stat"], root, check=False).stdout.rstrip())
        staged = run_git(["diff", "--cached", "--stat"], root, check=False).stdout.rstrip()
        if staged:
            print("\nStaged changes:")
            print(staged)
        return 0
    if args.name_only:
        print(run_git(["diff", "--name-only"], root, check=False).stdout.rstrip())
        return 0
    print(run_git(["diff", "--", *args.files], root, check=False).stdout.rstrip())
    return 0


def load_passport(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Passport not found: {path}")
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(text) or {}
        if isinstance(data, dict):
            return data
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    return {"raw": text}


def flatten_paths(value: Any) -> list[str]:
    paths: list[str] = []
    if isinstance(value, str):
        if value.endswith(".md") or "/" in value:
            paths.append(value)
    elif isinstance(value, list):
        for item in value:
            paths.extend(flatten_paths(item))
    elif isinstance(value, dict):
        for v in value.values():
            paths.extend(flatten_paths(v))
    return paths


def cmd_commit_message(args: argparse.Namespace) -> int:
    passport_path = Path(args.passport).resolve()
    data = load_passport(passport_path)
    workflow_id = data.get("workflow_id") or data.get("id") or passport_path.stem
    workflow_type = data.get("workflow_type") or data.get("command") or "llmzk run"
    input_data = data.get("input") or data.get("inputs") or {}
    outputs = data.get("outputs") or {}
    output_paths = flatten_paths(outputs)

    title = f"llmzk: {workflow_type} {workflow_id}".strip()
    print(title)
    print()
    if input_data:
        print("Input:")
        for p in flatten_paths(input_data):
            print(f"- {p}")
        print()
    if output_paths:
        print("Created/updated:")
        for p in output_paths[:30]:
            print(f"- {p}")
        if len(output_paths) > 30:
            print(f"- ... {len(output_paths) - 30} more")
        print()
    print("Passport:")
    print(f"- {passport_path}")
    return 0


def cmd_revert_run(args: argparse.Namespace) -> int:
    root = repo_root(Path(args.path).resolve())
    passport_path = Path(args.passport).resolve()
    data = load_passport(passport_path)
    outputs = data.get("outputs") or {}
    paths = sorted(set(flatten_paths(outputs)))
    if not paths:
        print("No output paths found in passport. Nothing to revert automatically.")
        return 1

    print("Files associated with this run:")
    for p in paths:
        print(f"- {p}")
    print()
    if args.dry_run:
        print("Dry run only. No files changed.")
        print("To apply, rerun with --apply after explicit user approval.")
        return 0
    if not args.apply:
        print("Refusing to modify files without --apply.")
        return 1

    for p in paths:
        rel = Path(p)
        tracked = run_git(["ls-files", "--error-unmatch", str(rel)], root, check=False)
        if tracked.returncode == 0:
            run_git(["checkout", "--", str(rel)], root, check=False)
            print(f"Restored tracked file: {rel}")
        else:
            target = root / rel
            if target.exists():
                target.unlink()
                print(f"Deleted untracked generated file: {rel}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Git safety helpers for llmzk")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("status", help="Show Git status summary")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("--limit", type=int, default=80)
    p.add_argument("--fail-if-dirty", action="store_true")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("preflight", help="Check whether broad writes are safe")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_preflight)

    p = sub.add_parser("diff", help="Show Git diff")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("--stat", action="store_true")
    p.add_argument("--name-only", action="store_true")
    p.add_argument("files", nargs="*")
    p.set_defaults(func=cmd_diff)

    p = sub.add_parser("commit-message", help="Draft a commit message from a passport")
    p.add_argument("passport")
    p.set_defaults(func=cmd_commit_message)

    p = sub.add_parser("revert-run", help="Revert files associated with a passport")
    p.add_argument("passport")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("--dry-run", action="store_true", default=True)
    p.add_argument("--apply", action="store_true")
    p.set_defaults(func=cmd_revert_run)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
