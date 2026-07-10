from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Literal

from git import GitCommandError, InvalidGitRepositoryError, NoSuchPathError, Repo
import tyro

from llmzk.doctor import run_doctor

VAULT_FOLDERS = [
    "00 Inbox",
    "00 Fleeting Notes",
    "01 Sources",
    "02 Literature Notes",
    "03 Permanent Notes",
    "04 Concept Notes",
    "05 Bridge Notes",
    "06 Contradiction Notes",
    "07 Index Notes",
    "08 Wiki Articles",
    "09 Media",
]

LOG_FOLDERS = [
    "Logs/Passports",
    "Logs/Decision Logs",
    "Logs/Review Queue",
]

ROOT_FILES = ["AGENTS.md", "opencode.json", ".gitignore"]
SYSTEM_DIRS = [".opencode", "Templates"]
INITIAL_COMMIT_PATHS = [
    "AGENTS.md",
    "opencode.json",
    ".gitignore",
    ".opencode",
    "Templates",
    *VAULT_FOLDERS,
    "Logs",
]


def default_repo_root() -> Path:
    """Return the source checkout root for editable/source-tree usage."""
    return Path(__file__).resolve().parents[2]


def copy_or_symlink_dir(src: Path, dst: Path, *, mode: Literal["copy", "symlink"], force: bool) -> None:
    if dst.exists() or dst.is_symlink():
        if not force:
            raise SystemExit(f"Refusing to overwrite existing path: {dst}")
        if dst.is_symlink() or dst.is_file():
            dst.unlink()
        else:
            shutil.rmtree(dst)
    if mode == "copy":
        shutil.copytree(src, dst)
    else:
        rel = os.path.relpath(src, start=dst.parent)
        dst.symlink_to(rel, target_is_directory=True)


def copy_file(src: Path, dst: Path, *, force: bool) -> None:
    if dst.exists() or dst.is_symlink():
        if not force:
            raise SystemExit(f"Refusing to overwrite existing file: {dst}")
        dst.unlink()
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def ensure_gitkeep(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    gitkeep = path / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.write_text("", encoding="utf-8")


def repo_at(path: Path) -> Repo | None:
    try:
        return Repo(path, search_parent_directories=False)
    except (InvalidGitRepositoryError, NoSuchPathError):
        return None


def init_git_repo(vault: Path) -> Repo:
    repo = repo_at(vault)
    if repo is not None:
        print("Git: existing repository detected")
        return repo
    repo = Repo.init(vault)
    print("Git: initialized repository")
    return repo


def initial_commit(vault: Path) -> None:
    repo = repo_at(vault) or init_git_repo(vault)
    try:
        repo.git.add(*INITIAL_COMMIT_PATHS)
        if not repo.is_dirty(untracked_files=True):
            print("Git: no scaffold changes to commit")
            return
        repo.index.commit("llmzk: initialize vault scaffold")
        print("Git: created initial commit")
    except GitCommandError as exc:
        print(
            "Git: initial commit failed. This is often because user.name/user.email is not configured.",
            file=sys.stderr,
        )
        print(str(exc), file=sys.stderr)


def init(
    vault: Path,
    mode: Literal["copy", "symlink"] = "copy",
    source: Path | None = None,
    force: bool = False,
    git: bool = True,
    commit: bool = False,
    doctor: bool = True,
) -> int:
    """Initialize an llmzk OpenCode/Obsidian vault.

    Args:
        vault: Path to the vault folder to create or install into.
        mode: Install `.opencode` and `Templates` by copying or symlinking.
        source: Path to the llmzk source repo. Defaults to this source checkout.
        force: Allow installing into an existing folder and overwrite installed system paths.
        git: Initialize a Git repository in the vault.
        commit: Create an initial scaffold commit.
        doctor: Run `llmzk doctor` after installing the scaffold.
    """
    repo_root = source.expanduser().resolve() if source else default_repo_root()
    scaffold = repo_root / "scaffold"
    if not scaffold.exists():
        raise SystemExit(f"Could not find scaffold directory: {scaffold}")

    vault = vault.expanduser().resolve()
    if vault.exists() and any(vault.iterdir()) and not force:
        raise SystemExit(
            f"Vault path is not empty: {vault}\nUse --force to install into an existing folder."
        )
    vault.mkdir(parents=True, exist_ok=True)

    print(f"llmzk source: {repo_root}")
    print(f"Vault: {vault}")
    print(f"Install mode: {mode}")

    # Root files are copied, not symlinked, because they are project-local entry points.
    for name in ROOT_FILES:
        copy_file(scaffold / name, vault / name, force=force)

    # System directories can be copied or symlinked.
    for name in SYSTEM_DIRS:
        copy_or_symlink_dir(scaffold / name, vault / name, mode=mode, force=force)

    for name in VAULT_FOLDERS:
        ensure_gitkeep(vault / name)
    for name in LOG_FOLDERS:
        ensure_gitkeep(vault / name)

    if git:
        init_git_repo(vault)
        if commit:
            initial_commit(vault)

    if doctor:
        print("\nRunning llmzk doctor...")
        code, findings = run_doctor(vault, fail_if_dirty=False, quiet_ok=True)
        for finding in findings:
            print(f"[{finding.level.upper()}] {finding.message}")
        if code != 0:
            print("Doctor reported issues. Review the messages above before using the vault.", file=sys.stderr)

    print("\nCreated llmzk vault scaffold.")
    print("Next:")
    print(f"  cd {vault}")
    if git and not commit:
        print('  git add . && git commit -m "llmzk: initialize vault scaffold"')
    print("  opencode")
    print("  /llmzk-doctor")
    print("  /llmzk-git-status")
    print("  /llmzk-ingest 00 Inbox/<source>.md")
    return 0


def main() -> int:
    return tyro.cli(init)


if __name__ == "__main__":
    raise SystemExit(main())
