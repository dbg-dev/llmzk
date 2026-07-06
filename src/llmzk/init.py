from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

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


def default_repo_root() -> Path:
    # Source-tree usage: <repo>/src/llmzk/init.py
    return Path(__file__).resolve().parents[2]


def copy_or_symlink_dir(src: Path, dst: Path, *, mode: str, force: bool) -> None:
    if dst.exists() or dst.is_symlink():
        if not force:
            raise SystemExit(f"Refusing to overwrite existing path: {dst}")
        if dst.is_symlink() or dst.is_file():
            dst.unlink()
        else:
            shutil.rmtree(dst)
    if mode == "copy":
        shutil.copytree(src, dst)
    elif mode == "symlink":
        rel = os.path.relpath(src, start=dst.parent)
        dst.symlink_to(rel, target_is_directory=True)
    else:  # pragma: no cover
        raise ValueError(mode)


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


def run(cmd: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def is_git_repo(path: Path) -> bool:
    result = run(["git", "rev-parse", "--is-inside-work-tree"], path, check=False)
    return result.returncode == 0 and result.stdout.strip() == "true"


def init_git(vault: Path) -> None:
    if is_git_repo(vault):
        print("Git: existing repository detected")
        return
    result = run(["git", "init"], vault, check=False)
    if result.returncode != 0:
        raise SystemExit(f"git init failed:\n{result.stderr}")
    print("Git: initialized repository")


def initial_commit(vault: Path) -> None:
    run(
        [
            "git",
            "add",
            "AGENTS.md",
            "opencode.json",
            ".gitignore",
            ".opencode",
            "Templates",
            *VAULT_FOLDERS,
            "Logs",
        ],
        vault,
        check=False,
    )
    result = run(["git", "commit", "-m", "llmzk: initialize vault scaffold"], vault, check=False)
    if result.returncode != 0:
        print(
            "Git: initial commit failed. This is often because user.name/user.email is not configured.",
            file=sys.stderr,
        )
        print(result.stderr, file=sys.stderr)
    else:
        print("Git: created initial commit")


def cmd_init(args: argparse.Namespace) -> int:
    repo_root = Path(args.source).resolve() if args.source else default_repo_root()
    scaffold = repo_root / "scaffold"
    if not scaffold.exists():
        raise SystemExit(f"Could not find scaffold directory: {scaffold}")

    vault = Path(args.vault).expanduser().resolve()
    if vault.exists() and any(vault.iterdir()) and not args.force:
        raise SystemExit(
            f"Vault path is not empty: {vault}\nUse --force to install into an existing folder."
        )
    vault.mkdir(parents=True, exist_ok=True)

    print(f"llmzk source: {repo_root}")
    print(f"Vault: {vault}")
    print(f"Install mode: {args.mode}")

    # Root files are copied, not symlinked, because they are project-local entry points.
    for name in ROOT_FILES:
        copy_file(scaffold / name, vault / name, force=args.force)

    # System directories can be copied or symlinked.
    for name in SYSTEM_DIRS:
        copy_or_symlink_dir(scaffold / name, vault / name, mode=args.mode, force=args.force)

    for name in VAULT_FOLDERS:
        ensure_gitkeep(vault / name)
    for name in LOG_FOLDERS:
        ensure_gitkeep(vault / name)

    if args.git:
        init_git(vault)
        if args.commit:
            initial_commit(vault)

    print("\nCreated llmzk vault scaffold.")
    print("Next:")
    print(f"  cd {vault}")
    print("  opencode")
    print("  /llmzk-git-status")
    print("  /llmzk-ingest 00 Inbox/<source>.md")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Initialize an llmzk OpenCode/Obsidian vault")
    parser.add_argument("vault", help="Path to the vault folder to create or install into")
    parser.add_argument(
        "--mode",
        choices=["copy", "symlink"],
        default="copy",
        help="Install .opencode and Templates by copying or symlinking",
    )
    parser.add_argument("--source", help="Path to the llmzk source repo; defaults to this source checkout")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow installing into an existing folder and overwrite installed system paths",
    )
    parser.add_argument(
        "--git",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Initialize a Git repository in the vault",
    )
    parser.add_argument("--commit", action="store_true", help="Create an initial scaffold commit")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return cmd_init(args)


if __name__ == "__main__":
    raise SystemExit(main())
