"""Shared Git utility helpers.

Consolidates the duplicated find_repo, porcelain, and git_dirty helpers
from doctor.py, update.py, and git_safety.py.
"""
from __future__ import annotations

from pathlib import Path

from git import InvalidGitRepositoryError, NoSuchPathError, Repo


def find_repo(root: Path) -> Repo | None:
    """Find a Git repository at or above root, returning None if not in one."""
    try:
        return Repo(root, search_parent_directories=True)
    except (InvalidGitRepositoryError, NoSuchPathError):
        return None


def porcelain(repo: Repo) -> list[str]:
    """Return non-empty porcelain status lines."""
    out = repo.git.status("--porcelain=v1")
    return [line for line in out.splitlines() if line.strip()]


def git_dirty(root: Path) -> tuple[bool, int]:
    """Check if the Git working tree at root is dirty. Returns (is_dirty, count)."""
    repo = find_repo(root)
    if repo is None:
        return False, 0
    lines = porcelain(repo)
    return bool(lines), len(lines)
