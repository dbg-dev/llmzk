from __future__ import annotations

import filecmp
import fnmatch
import json as json_lib
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import tyro

from llmzk_tools import __version__
from llmzk_tools.config import load_config, write_config
from llmzk_tools.git_util import git_dirty
from llmzk_tools.manifest import ROOT_FILES, SYSTEM_DIRS, scaffold_managed_paths

IGNORED_PARTS = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "node_modules", "__MACOSX"}
IGNORED_NAMES = {".DS_Store"}

_SCAFFOLD_MANAGED = scaffold_managed_paths()


@dataclass(frozen=True)
class Change:
    level: str
    action: str
    path: str
    message: str


def add(changes: list[Change], level: str, action: str, path: str, message: str) -> None:
    changes.append(Change(level=level, action=action, path=path, message=message))


def is_scaffold_managed(file_rel: str) -> bool:
    """Check if a relative path matches scaffold-owned naming conventions."""
    return any(fnmatch.fnmatch(file_rel, pat) for pat in _SCAFFOLD_MANAGED)


def ignored(path: Path) -> bool:
    return any(part in IGNORED_PARTS for part in path.parts) or path.name in IGNORED_NAMES


def source_scaffold(source: Path) -> Path:
    root = source.expanduser().resolve()
    scaffold = root / "scaffold"
    if not scaffold.exists():
        raise FileNotFoundError(f"Source repo does not contain scaffold/: {root}")
    return scaffold


def iter_files(base: Path) -> Iterable[Path]:
    if base.is_file():
        if not ignored(base):
            yield base
        return
    for path in base.rglob("*"):
        if ignored(path):
            continue
        if path.is_file() or path.is_symlink():
            yield path


def file_changed(src: Path, dst: Path) -> bool:
    if not dst.exists() and not dst.is_symlink():
        return True
    if src.is_symlink() or dst.is_symlink():
        return not (dst.is_symlink() and dst.resolve() == src.resolve())
    if src.is_file() and dst.is_file():
        try:
            return not filecmp.cmp(src, dst, shallow=False)
        except OSError:
            return True
    return True


def plan_copy(vault: Path, scaffold: Path) -> list[Change]:
    changes: list[Change] = []
    for rel in ROOT_FILES:
        src = scaffold / rel
        dst = vault / rel
        if not src.exists():
            add(changes, "fail", "missing-source", rel, "Source scaffold file is missing")
        elif file_changed(src, dst):
            action = "create" if not dst.exists() else "update"
            add(changes, "change", action, rel, "System file differs from scaffold")
        else:
            add(changes, "ok", "unchanged", rel, "System file matches scaffold")
    for rel in SYSTEM_DIRS:
        src_dir = scaffold / rel
        dst_dir = vault / rel
        if not src_dir.exists():
            add(changes, "fail", "missing-source", rel, "Source scaffold directory is missing")
            continue
        if dst_dir.is_symlink():
            add(changes, "change", "replace-symlink", rel, "Will replace symlink with copied directory")
            continue
        scaffold_files = set()
        for src in iter_files(src_dir):
            file_rel = src.relative_to(scaffold).as_posix()
            scaffold_files.add(file_rel)
            dst = vault / file_rel
            if file_changed(src, dst):
                action = "create" if not dst.exists() else "update"
                add(changes, "change", action, file_rel, "System file differs from scaffold")
            else:
                add(changes, "ok", "unchanged", file_rel, "System file matches scaffold")
        if dst_dir.exists():
            for dst in iter_files(dst_dir):
                file_rel = dst.relative_to(vault).as_posix()
                if file_rel not in scaffold_files and is_scaffold_managed(file_rel):
                    add(changes, "change", "delete", file_rel, "Stale scaffold file not in upstream")
    return changes


def plan_symlink(vault: Path, scaffold: Path) -> list[Change]:
    changes: list[Change] = []
    for rel in ROOT_FILES:
        src = scaffold / rel
        dst = vault / rel
        if not src.exists():
            add(changes, "fail", "missing-source", rel, "Source scaffold file is missing")
        elif file_changed(src, dst):
            action = "create" if not dst.exists() else "update"
            add(changes, "change", action, rel, "Root system file differs from scaffold")
        else:
            add(changes, "ok", "unchanged", rel, "Root system file matches scaffold")
    for rel in SYSTEM_DIRS:
        src = scaffold / rel
        dst = vault / rel
        if not src.exists():
            add(changes, "fail", "missing-source", rel, "Source scaffold directory is missing")
        elif not dst.is_symlink() or dst.resolve() != src.resolve():
            add(changes, "change", "symlink", rel, f"Should symlink to {src}")
        else:
            add(changes, "ok", "unchanged", rel, "Symlink points to scaffold")
    return changes


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        if dst.is_dir() and not dst.is_symlink():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    shutil.copy2(src, dst)


def copy_tree_overlay(src_dir: Path, dst_dir: Path, *, system_prefix: str = "") -> None:
    if dst_dir.is_symlink() or dst_dir.is_file():
        dst_dir.unlink()
    dst_dir.mkdir(parents=True, exist_ok=True)
    scaffold_files = set()
    for src in iter_files(src_dir):
        rel = src.relative_to(src_dir)
        scaffold_files.add(rel.as_posix())
        dst = dst_dir / rel
        copy_file(src, dst)
    if dst_dir.exists():
        for dst in iter_files(dst_dir):
            rel = dst.relative_to(dst_dir).as_posix()
            full_rel = f"{system_prefix}{rel}" if system_prefix else rel
            if rel not in scaffold_files and is_scaffold_managed(full_rel):
                dst.unlink()


def apply_update(vault: Path, scaffold: Path, *, mode: str, source: Path) -> None:
    for rel in ROOT_FILES:
        copy_file(scaffold / rel, vault / rel)
    if mode == "copy":
        for rel in SYSTEM_DIRS:
            copy_tree_overlay(scaffold / rel, vault / rel, system_prefix=f"{rel}/")
    else:
        for rel in SYSTEM_DIRS:
            dst = vault / rel
            if dst.exists() or dst.is_symlink():
                if dst.is_dir() and not dst.is_symlink():
                    shutil.rmtree(dst)
                else:
                    dst.unlink()
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.symlink_to(scaffold / rel, target_is_directory=True)

    cfg = load_config(vault)
    write_config(
        vault,
        instance_name=cfg.instance_name,
        vault_relative_prefix=cfg.vault_relative_prefix,
        link_style=cfg.link_style,
        installed_version=__version__,
        install_mode=mode,
        source_path=str(source.expanduser().resolve()),
    )


def update(
    vault: tyro.conf.Positional[Path] = Path("."),
    *,
    source: Path | None = None,
    mode: str = "auto",
    apply: bool = False,
    allow_dirty: bool = False,
    json: bool = False,
) -> int:
    """Report or update the installed llmzk system layer from an upstream scaffold.

    Only system paths are touched: AGENTS.md, opencode.json, .gitignore,
    .opencode/, Templates/, and .llmzk.yaml metadata. Durable note folders and
    Logs are never copied, deleted, or rewritten by this tool.
    """
    root = vault.expanduser().resolve()
    if not root.exists():
        print(f"Vault path does not exist: {root}")
        return 1
    cfg = load_config(root)
    if source is None:
        if cfg.source_path:
            source = Path(cfg.source_path)
        else:
            print("Missing --source and .llmzk.yaml has no source_path")
            return 1
    source_root = source.expanduser().resolve()
    try:
        scaffold = source_scaffold(source_root)
    except FileNotFoundError as exc:
        print(str(exc))
        return 1
    if mode == "auto":
        mode = cfg.install_mode if cfg.install_mode in {"copy", "symlink"} else "copy"
    if mode not in {"copy", "symlink"}:
        print("--mode must be copy, symlink, or auto")
        return 1

    changes = plan_symlink(root, scaffold) if mode == "symlink" else plan_copy(root, scaffold)
    dirty, dirty_count = git_dirty(root)
    if apply and dirty and not allow_dirty:
        add(changes, "fail", "blocked", ".", f"Git tree is dirty ({dirty_count} changed entries); rerun with --allow-dirty if intentional")

    failures = [c for c in changes if c.level == "fail"]
    if json:
        print(json_lib.dumps([c.__dict__ for c in changes], indent=2))
    else:
        print(f"llmzk update: {root}")
        print(f"source: {source_root}")
        print(f"mode: {mode}")
        print(f"action: {'apply' if apply else 'dry-run'}")
        print("scope: system layer only; durable notes and Logs are not touched")
        print()
        for c in changes:
            if c.level == "ok":
                continue
            label = {"change": "CHANGE", "fail": "FAIL", "ok": "OK"}[c.level]
            print(f"[{label}] {c.action}: {c.path} — {c.message}")
        if not [c for c in changes if c.level != "ok"]:
            print("No system-layer drift detected.")

    if failures:
        return 1
    if apply:
        apply_update(root, scaffold, mode=mode, source=source_root)
        if not json:
            print()
            print("Update applied. Run: .opencode/bin/llmzk doctor .")
    return 0


def main() -> int:
    return tyro.cli(update)


if __name__ == "__main__":
    raise SystemExit(main())
