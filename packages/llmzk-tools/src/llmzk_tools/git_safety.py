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

from git import GitCommandError, Repo
import tyro

from llmzk_tools.git_util import (
    GitContext,
    git_context,
    instance_to_repo_path,
    porcelain,
)

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


def require_context(path: Path) -> GitContext:
    context = git_context(path)
    if context is None:
        raise SystemExit(
            "Not inside a Git repository. Initialize Git first or run from the vault root."
        )
    return context


def repo_root(path: Path) -> tuple[Repo, Path]:
    """Compatibility helper returning the repository and repository root."""
    context = require_context(path)
    return context.repo, context.repo_root


def _scoped_lines(context: GitContext) -> list[str]:
    return porcelain(context.repo, context.pathspec)


def run_status(args: Status) -> int:
    context = require_context(args.path)
    try:
        branch = context.repo.active_branch.name
    except TypeError:
        branch = "(detached)"

    lines = _scoped_lines(context)
    print(f"Repository: {context.repo_root}")
    if context.instance_root != context.repo_root:
        print(f"llmzk instance: {context.instance_root}")
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
    context = require_context(args.path)
    lines = _scoped_lines(context)
    if not lines:
        print("Preflight: clean working tree. Safe to start a broad llmzk run.")
        return 0

    print("Preflight: working tree is dirty.")
    print(
        "Review or commit/revert existing changes before a broad llmzk run, "
        "or explicitly allow mixing changes."
    )
    print()
    for line in lines[: args.limit]:
        print(line)
    if len(lines) > args.limit:
        print(f"... {len(lines) - args.limit} more")
    return 1


def _diff_pathspecs(context: GitContext, files: list[str]) -> list[str]:
    if not files:
        return [] if context.pathspec == "." else [context.pathspec]

    pathspecs: list[str] = []
    for raw in files:
        try:
            _local_rel, _resolved, repo_rel = instance_to_repo_path(context, raw)
        except ValueError as exc:
            raise SystemExit(
                f"Refusing diff path outside llmzk instance: {raw} ({exc})"
            ) from exc
        pathspecs.append(repo_rel)
    return pathspecs


def _diff(repo: Repo, options: list[str], pathspecs: list[str]) -> str:
    args = [*options]
    if pathspecs:
        args.extend(["--", *pathspecs])
    return repo.git.diff(*args).rstrip()


def run_diff(args: Diff) -> int:
    context = require_context(args.path)
    pathspecs = _diff_pathspecs(context, args.files)

    if args.stat:
        print(_diff(context.repo, ["--stat"], pathspecs))
        staged = _diff(context.repo, ["--cached", "--stat"], pathspecs)
        if staged:
            print("\nStaged changes:")
            print(staged)
        return 0

    if args.name_only:
        print(_diff(context.repo, ["--name-only"], pathspecs))
        return 0

    print(_diff(context.repo, [], pathspecs))
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
        for nested in value.values():
            paths.extend(flatten_paths(nested))
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
        for path in flatten_paths(input_data):
            print(f"- {path}")
        print()
    if output_paths:
        print("Created/updated:")
        for path in output_paths[:30]:
            print(f"- {path}")
        if len(output_paths) > 30:
            print(f"- ... {len(output_paths) - 30} more")
        print()
    print("Passport:")
    print(f"- {passport_path}")
    return 0


def run_revert_run(args: RevertRun) -> int:
    context = require_context(args.path)
    passport_path = args.passport.expanduser().resolve()
    data = load_passport(passport_path)
    outputs = data.get("outputs") or {}
    paths = sorted(set(flatten_paths(outputs)))
    if not paths:
        print("No output paths found in passport. Nothing to revert automatically.")
        return 1

    print("Files associated with this run:")
    for path in paths:
        print(f"- {path}")
    print()

    # Dry-run is the default. `dry_run` is retained for compatibility with existing commands.
    _ = args.dry_run
    if not args.apply:
        print("Dry run only. No files changed.")
        print("To apply, rerun with --apply after explicit user approval.")
        return 0

    for raw in paths:
        try:
            local_rel, target, repo_rel = instance_to_repo_path(context, raw)
        except ValueError:
            print(f"Refusing to touch path outside vault root: {raw}")
            continue

        try:
            context.repo.git.ls_files("--error-unmatch", "--", repo_rel)
            context.repo.git.checkout("--", repo_rel)
            print(f"Restored tracked file: {local_rel}")
        except GitCommandError:
            if target.exists():
                if target.is_dir():
                    raise SystemExit(
                        f"Refusing to delete generated directory automatically: {local_rel}"
                    )
                target.unlink()
                print(f"Deleted untracked generated file: {local_rel}")
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
