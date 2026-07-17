"""Shared Git utility helpers.

Git commands operate on an llmzk instance, which may be the repository root or
may live inside a larger Git-managed Obsidian vault. ``GitContext`` keeps those
two roots distinct so status, diff, dirty checks, and path operations stay
inside the supplied llmzk instance.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from git import InvalidGitRepositoryError, NoSuchPathError, Repo


@dataclass(frozen=True)
class GitContext:
    """Repository and llmzk-instance paths for scoped Git operations."""

    repo: Repo
    repo_root: Path
    instance_root: Path
    instance_prefix: Path

    @property
    def pathspec(self) -> str:
        """Git pathspec that scopes commands to this llmzk instance."""
        if self.instance_prefix == Path("."):
            return "."
        return self.instance_prefix.as_posix()


def find_repo(root: Path) -> Repo | None:
    """Find a Git repository at or above root, returning ``None`` if absent."""
    try:
        return Repo(root, search_parent_directories=True)
    except (InvalidGitRepositoryError, NoSuchPathError):
        return None


def git_context(root: Path) -> GitContext | None:
    """Resolve repository and instance roots for an llmzk path."""
    instance_root = root.expanduser().resolve()
    repo = find_repo(instance_root)
    if repo is None or repo.working_tree_dir is None:
        return None

    repo_root = Path(repo.working_tree_dir).resolve()
    try:
        instance_prefix = instance_root.relative_to(repo_root)
    except ValueError:
        return None

    if not instance_prefix.parts:
        instance_prefix = Path(".")

    return GitContext(
        repo=repo,
        repo_root=repo_root,
        instance_root=instance_root,
        instance_prefix=instance_prefix,
    )


def porcelain(repo: Repo, pathspec: str | Path | None = None) -> list[str]:
    """Return non-empty porcelain status lines, optionally scoped by pathspec."""
    args = ["--porcelain=v1"]
    if pathspec is not None and str(pathspec) not in {"", "."}:
        args.extend(["--", Path(pathspec).as_posix()])
    output = repo.git.status(*args)
    return [line for line in output.splitlines() if line.strip()]


def instance_to_repo_path(context: GitContext, raw: str | Path) -> tuple[Path, Path, str]:
    """Resolve an instance-relative path into local, absolute, and Git forms."""
    rel = Path(raw)
    if rel.is_absolute():
        raise ValueError(f"absolute paths are not allowed: {raw}")

    resolved = (context.instance_root / rel).resolve()
    try:
        local_rel = resolved.relative_to(context.instance_root)
    except ValueError as exc:
        raise ValueError(f"path escapes llmzk instance: {raw}") from exc

    repo_rel = resolved.relative_to(context.repo_root).as_posix()
    return local_rel, resolved, repo_rel


def git_dirty(root: Path) -> tuple[bool, int]:
    """Check whether the supplied llmzk instance has Git-visible changes."""
    context = git_context(root)
    if context is None:
        return False, 0
    lines = porcelain(context.repo, context.pathspec)
    return bool(lines), len(lines)
