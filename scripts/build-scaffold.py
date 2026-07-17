#!/usr/bin/env python3
"""Build the installed-vault Python project into the scaffold.

`packages/llmzk-tools` is the only editable source. The generated copy under
`scaffold/.opencode/llmzk-tools` exists solely so existing install and update
paths can continue treating the scaffold as a complete vault distribution.
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import subprocess
import sys
from pathlib import Path

IGNORED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
}
IGNORED_FILES = {".DS_Store"}


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def tracked_target_files(root: Path, target: Path) -> list[str]:
    try:
        relative = target.relative_to(root)
    except ValueError:
        return []
    completed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--", relative.as_posix()],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return []
    return [line for line in completed.stdout.splitlines() if line]


def ignored(path: Path) -> bool:
    return path.name in IGNORED_FILES or any(part in IGNORED_DIRS for part in path.parts)


def copy_source(source: Path, target: Path) -> None:
    if not (source / "pyproject.toml").is_file():
        raise FileNotFoundError(f"llmzk-tools source package not found: {source}")

    if target.exists() or target.is_symlink():
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        else:
            target.unlink()

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns(*sorted(IGNORED_DIRS | IGNORED_FILES)),
        copy_function=shutil.copy2,
        symlinks=True,
    )
    (target / ".llmzk-generated").write_text(
        "Generated from packages/llmzk-tools by scripts/build-scaffold.py.\n",
        encoding="utf-8",
    )


def relative_files(root: Path) -> set[Path]:
    if not root.exists():
        return set()
    return {
        path.relative_to(root)
        for path in root.rglob("*")
        if (path.is_file() or path.is_symlink()) and not ignored(path.relative_to(root))
    }


def check(source: Path, target: Path) -> list[str]:
    problems: list[str] = []
    source_files = relative_files(source)
    target_files = relative_files(target) - {Path(".llmzk-generated")}

    for rel in sorted(source_files - target_files):
        problems.append(f"missing: {rel.as_posix()}")
    for rel in sorted(target_files - source_files):
        problems.append(f"extra: {rel.as_posix()}")

    for rel in sorted(source_files & target_files):
        src = source / rel
        dst = target / rel
        if src.is_symlink() or dst.is_symlink():
            if not (src.is_symlink() and dst.is_symlink() and src.readlink() == dst.readlink()):
                problems.append(f"changed: {rel.as_posix()}")
        elif not filecmp.cmp(src, dst, shallow=False):
            problems.append(f"changed: {rel.as_posix()}")

    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path)
    parser.add_argument("--target", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()

    root = repository_root()
    source = (args.source or root / "packages" / "llmzk-tools").resolve()
    target = (args.target or root / "scaffold" / ".opencode" / "llmzk-tools").resolve()

    if args.clean:
        if target.exists() or target.is_symlink():
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target)
            else:
                target.unlink()
        print(f"Removed generated scaffold tools: {target}")
        return 0

    if args.check:
        problems = check(source, target)
        if problems:
            print("Generated scaffold tools are out of date:")
            for problem in problems:
                print(f"  {problem}")
            return 1
        print("Generated scaffold tools match packages/llmzk-tools")
        return 0

    tracked = tracked_target_files(root, target)
    if tracked:
        print(
            "Refusing to rebuild scaffold/.opencode/llmzk-tools while its former files "
            "remain tracked. Stage the monorepo move first with `git add -A`, then rerun.",
            file=sys.stderr,
        )
        return 2

    copy_source(source, target)
    print(f"Built {target} from {source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
