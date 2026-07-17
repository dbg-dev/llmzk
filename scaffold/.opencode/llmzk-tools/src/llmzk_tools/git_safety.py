#!/usr/bin/env python3
"""Git safety helpers for llmzk.

These helpers intentionally wrap a small subset of Git via GitPython. They do
not replace normal Git review; they make the llmzk safety workflow easier to
invoke from OpenCode commands.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Any, Union

from git import GitCommandError, InvalidGitRepositoryError, NoSuchPathError, Repo
import tyro

from llmzk_tools.git_util import porcelain

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


@dataclass
class Status:
    """Show Git status summary."""

    path: tyro.conf.Positional[Path] = Path(".")
    limit: int = 80
    fail_if_dirty: bool = False


@dataclass
class Preflight:
    """Check whether broad writes are safe."""

    path: tyro.conf.Positional[Path] = Path(".")
    limit: int = 50


@dataclass
class Diff:
    """Show Git diff."""

    path: tyro.conf.Positional[Path] = Path(".")
    stat: bool = False
    name_only: bool = False
    files: list[str] = field(default_factory=list)


@dataclass
class CommitMessage:
    """Draft a commit message from a passport."""

    passport: tyro.conf.Positional[Path]


@dataclass
class RevertRun:
    """Revert files associated with a passport."""

    passport: tyro.conf.Positional[Path]
    path: tyro.conf.Positional[Path] = Path(".")
    dry_run: bool = False
    apply: bool = False


Command = Union[
    Annotated[Status, tyro.conf.subcommand(name="status")],
    Annotated[Preflight, tyro.conf.subcommand(name="preflight")],
    Annotated[Diff, tyro.conf.subcommand(name="diff")],
    Annotated[CommitMessage, tyro.conf.subcommand(name="commit-message")],
    Annotated[RevertRun, tyro.conf.subcommand(name="revert-run")],
]


def repo_root(path: Path) -> tuple[Repo, Path]:
    try:
        repo = Repo(path.expanduser().resolve(), search_parent_directories=True)
    except (InvalidGitRepositoryError, NoSuchPathError):
        raise SystemExit("Not inside a Git repository. Initialize Git first or run from the vault root.")
    if repo.working_tree_dir is None:
        raise SystemExit("Git repository has no working tree. Run from a normal vault checkout.")
    return repo, Path(repo.working_tree_dir).resolve()


def run_status(args: Status) -> int:
    repo, root = repo_root(args.path)
    try:
        branch = repo.active_branch.name
    except TypeError:
        branch = "(detached)"
    lines = porcelain(repo)
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


def run_preflight(args: Preflight) -> int:
    repo, _ = repo_root(args.path)
    lines = porcelain(repo)
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


def run_diff(args: Diff) -> int:
    repo, _ = repo_root(args.path)
    if args.stat:
        print(repo.git.diff("--stat").rstrip())
        staged = repo.git.diff("--cached", "--stat").rstrip()
        if staged:
            print("\nStaged changes:")
            print(staged)
        return 0
    if args.name_only:
        print(repo.git.diff("--name-only").rstrip())
        return 0
    if args.files:
        print(repo.git.diff("--", *args.files).rstrip())
    else:
        print(repo.git.diff().rstrip())
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
        if value.endswith(".md") or value.endswith(".yaml") or "/" in value:
            paths.append(value)
    elif isinstance(value, list):
        for item in value:
            paths.extend(flatten_paths(item))
    elif isinstance(value, dict):
        for v in value.values():
            paths.extend(flatten_paths(v))
    return paths


def run_commit_message(args: CommitMessage) -> int:
    passport_path = args.passport.expanduser().resolve()
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


def run_revert_run(args: RevertRun) -> int:
    repo, root = repo_root(args.path)
    passport_path = args.passport.expanduser().resolve()
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
    # Dry-run is the default. `dry_run` is retained for compatibility with existing commands.
    _ = args.dry_run
    if not args.apply:
        print("Dry run only. No files changed.")
        print("To apply, rerun with --apply after explicit user approval.")
        return 0

    for p in paths:
        rel = Path(p)
        resolved = (root / rel).resolve()
        try:
            resolved.relative_to(root)
        except ValueError:
            print(f"Refusing to touch path outside vault root: {rel} -> {resolved}")
            continue
        try:
            repo.git.ls_files("--error-unmatch", str(rel))
            repo.git.checkout("--", str(rel))
            print(f"Restored tracked file: {rel}")
        except GitCommandError:
            target = root / rel
            if target.exists():
                if target.is_dir():
                    raise SystemExit(f"Refusing to delete generated directory automatically: {rel}")
                target.unlink()
                print(f"Deleted untracked generated file: {rel}")
    return 0


def main() -> int:
    command = tyro.cli(Command)
    if isinstance(command, Status):
        return run_status(command)
    if isinstance(command, Preflight):
        return run_preflight(command)
    if isinstance(command, Diff):
        return run_diff(command)
    if isinstance(command, CommitMessage):
        return run_commit_message(command)
    if isinstance(command, RevertRun):
        return run_revert_run(command)
    raise AssertionError(f"Unhandled command: {command!r}")


if __name__ == "__main__":
    raise SystemExit(main())
