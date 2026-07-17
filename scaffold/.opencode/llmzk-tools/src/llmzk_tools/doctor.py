from __future__ import annotations

import json as json_lib
from pathlib import Path
from typing import Iterable

from git import GitCommandError
import tyro

from llmzk_tools import __version__
from llmzk_tools.config import load_config
from llmzk_tools.finding import Finding, add
from llmzk_tools.git_util import find_repo, porcelain
from llmzk_tools.manifest import (
    LOG_FOLDERS,
    REQUIRED_COMMANDS,
    REQUIRED_DOCS,
    REQUIRED_OPEN_CODE_DIRS,
    REQUIRED_SKILLS,
    REQUIRED_TEMPLATES,
    REQUIRED_TOOLS,
    ROOT_FILES,
    VAULT_FOLDERS,
)

DOCTOR_ROOT_FILES = [*ROOT_FILES, ".llmzk.yaml"]


def check_exists(findings: list[Finding], root: Path, rel_paths: Iterable[str], *, kind: str) -> None:
    for rel in rel_paths:
        path = root / rel
        if path.exists() or path.is_symlink():
            add(findings, "ok", f"{kind} exists: {rel}")
        else:
            add(findings, "fail", f"Missing {kind}: {rel}")


def check_git(findings: list[Finding], root: Path, *, fail_if_dirty: bool) -> None:
    repo = find_repo(root)
    if repo is None or repo.working_tree_dir is None:
        add(findings, "fail", "Vault is not inside a Git repository")
        return

    git_root = Path(repo.working_tree_dir).resolve()
    if git_root != root:
        add(findings, "warn", f"Git root is {git_root}, not the supplied vault root {root}")
    else:
        add(findings, "ok", "Git repository detected at vault root")

    dirty = porcelain(repo)
    if not dirty:
        add(findings, "ok", "Git working tree is clean")
    else:
        level = "fail" if fail_if_dirty else "warn"
        add(findings, level, f"Git working tree is dirty ({len(dirty)} changed entries)")


def check_opencode_config(findings: list[Finding], root: Path) -> None:
    path = root / "opencode.json"
    if not path.exists():
        return
    try:
        data = json_lib.loads(path.read_text(encoding="utf-8"))
    except json_lib.JSONDecodeError as exc:
        add(findings, "fail", f"opencode.json is not valid JSON: {exc}")
        return
    instructions = data.get("instructions", [])
    if not isinstance(instructions, list):
        add(findings, "fail", "opencode.json instructions must be a list")
        return
    for rel in instructions:
        if not isinstance(rel, str):
            add(findings, "fail", f"Invalid instruction entry in opencode.json: {rel!r}")
            continue
        if (root / rel).exists() or (root / rel).is_symlink():
            add(findings, "ok", f"OpenCode instruction path exists: {rel}")
        else:
            add(findings, "fail", f"OpenCode instruction path missing: {rel}")


def check_gitignore(findings: list[Finding], root: Path) -> None:
    path = root / ".gitignore"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    required_fragments = [".venv/", "__MACOSX/", ".DS_Store"]
    for frag in required_fragments:
        if frag in text:
            add(findings, "ok", f".gitignore contains: {frag}")
        else:
            add(findings, "warn", f".gitignore missing expected fragment: {frag}")


def check_git_visibility(findings: list[Finding], root: Path) -> None:
    # Git safety depends on generated durable notes and run logs being visible to Git.
    # If these are ignored, git diff/status cannot be the review boundary.
    repo = find_repo(root)
    if repo is None:
        add(findings, "warn", "Skipping Git visibility checks because vault is not a Git repository")
        return
    probes = [
        "01 Sources/__llmzk_doctor_probe__.md",
        "02 Literature Notes/__llmzk_doctor_probe__.md",
        "03 Permanent Notes/__llmzk_doctor_probe__.md",
        "04 Concept Notes/__llmzk_doctor_probe__.md",
        "05 Bridge Notes/__llmzk_doctor_probe__.md",
        "06 Contradiction Notes/__llmzk_doctor_probe__.md",
        "07 Index Notes/__llmzk_doctor_probe__.md",
        "08 Wiki Articles/__llmzk_doctor_probe__.md",
        "Logs/Passports/__llmzk_doctor_probe__.yaml",
        "Logs/Decision Logs/__llmzk_doctor_probe__.md",
        "Logs/Candidate Reviews/__llmzk_doctor_probe__.md",
    ]
    for rel in probes:
        try:
            repo.git.check_ignore("-q", rel)
            add(findings, "fail", f"Git safety issue: generated output would be ignored: {rel}")
        except GitCommandError as exc:
            if exc.status == 1:
                add(findings, "ok", f"Generated output is Git-visible: {rel}")
            else:
                add(findings, "warn", f"Could not check Git visibility for {rel}: {exc}")


def check_no_nested_git(findings: list[Finding], root: Path) -> None:
    for rel_root in [".opencode", "Templates"]:
        base = root / rel_root
        if not base.exists():
            continue
        for path in base.rglob(".git"):
            add(findings, "fail", f"Nested Git repository detected: {path.relative_to(root)}")


def check_gitkeep(findings: list[Finding], root: Path) -> None:
    for rel in [*VAULT_FOLDERS, *LOG_FOLDERS]:
        folder = root / rel
        if not folder.exists():
            add(findings, "fail", f"Missing vault/log folder: {rel}")
            continue
        gitkeep = folder / ".gitkeep"
        if gitkeep.exists():
            add(findings, "ok", f"Folder placeholder exists: {rel}/.gitkeep")
        else:
            add(findings, "warn", f"Missing folder placeholder: {rel}/.gitkeep")


def check_tool_project(findings: list[Finding], root: Path) -> None:
    pyproject = root / ".opencode" / "llmzk-tools" / "pyproject.toml"
    wrapper = root / ".opencode" / "bin" / "llmzk"
    if wrapper.exists() or wrapper.is_symlink():
        add(findings, "ok", "llmzk wrapper exists: .opencode/bin/llmzk")
    else:
        add(findings, "fail", "Missing llmzk wrapper: .opencode/bin/llmzk")
    if not pyproject.exists():
        add(findings, "fail", "Missing llmzk-tools pyproject.toml")
        return
    text = pyproject.read_text(encoding="utf-8")
    required = [
        "llmzk-audit",
        "llmzk-benchmark",
        "llmzk-doctor",
        "llmzk-fix-frontmatter",
        "llmzk-git-safety",
        "llmzk-new-run",
        "llmzk-normalize-links",
        "llmzk-review",
        "llmzk-update",
    ]
    for name in required:
        if name in text:
            add(findings, "ok", f"llmzk-tools script registered: {name}")
        else:
            add(findings, "fail", f"llmzk-tools script missing from pyproject.toml: {name}")
    for dep in ["tyro", "gitpython", "pyyaml"]:
        if dep in text.lower():
            add(findings, "ok", f"llmzk-tools dependency declared: {dep}")
        else:
            add(findings, "fail", f"llmzk-tools dependency missing: {dep}")



def check_llmzk_config(findings: list[Finding], root: Path) -> None:
    path = root / ".llmzk.yaml"
    if not path.exists():
        add(findings, "fail", "Missing llmzk instance config: .llmzk.yaml")
        return
    text = path.read_text(encoding="utf-8")
    required_keys = ["schema_version:", "instance_name:", "vault_relative_prefix:", "link_style:"]
    metadata_keys = ["installed_version:", "install_mode:", "source_path:"]
    for key in required_keys:
        if key in text:
            add(findings, "ok", f"llmzk config contains: {key[:-1]}")
        else:
            add(findings, "fail", f"llmzk config missing key: {key[:-1]}")
    for key in metadata_keys:
        if key in text:
            add(findings, "ok", f"llmzk config contains: {key[:-1]}")
        else:
            add(findings, "warn", f"llmzk config missing update metadata: {key[:-1]}")
    if "link_style: vault_relative" in text and ("vault_relative_prefix: \"\"" in text or "vault_relative_prefix: ''" in text):
        add(findings, "warn", "link_style is vault_relative but vault_relative_prefix is empty")
    cfg = load_config(root)
    if not cfg.installed_version:
        add(findings, "warn", "llmzk config has no installed_version; run llmzk update after upgrading")
    elif cfg.installed_version != __version__:
        add(findings, "warn", f"Version mismatch: .llmzk.yaml says {cfg.installed_version}, tools say {__version__}")
    else:
        add(findings, "ok", f"llmzk version metadata matches tools: {__version__}")
    if cfg.install_mode not in {"copy", "symlink"}:
        add(findings, "warn", f"Unknown install_mode in .llmzk.yaml: {cfg.install_mode}")
    else:
        add(findings, "ok", f"Install mode recorded: {cfg.install_mode}")
    if cfg.install_mode == "symlink":
        for rel in [".opencode", "Templates"]:
            path = root / rel
            if path.is_symlink():
                add(findings, "ok", f"Symlink install path is a symlink: {rel}")
            else:
                add(findings, "warn", f"install_mode is symlink but path is not a symlink: {rel}")
    if cfg.source_path:
        source = Path(cfg.source_path).expanduser()
        if source.exists():
            add(findings, "ok", f"Recorded source_path exists: {cfg.source_path}")
        else:
            add(findings, "warn", f"Recorded source_path does not exist: {cfg.source_path}")
    else:
        add(findings, "warn", "No source_path recorded; update needs --source")

def run_doctor(vault: Path, *, fail_if_dirty: bool = False, quiet_ok: bool = False) -> tuple[int, list[Finding]]:
    root = vault.expanduser().resolve()
    findings: list[Finding] = []
    if not root.exists():
        add(findings, "fail", f"Vault path does not exist: {root}")
        return 1, findings

    check_exists(findings, root, DOCTOR_ROOT_FILES, kind="root file")
    check_exists(findings, root, REQUIRED_OPEN_CODE_DIRS, kind="OpenCode directory")
    check_exists(findings, root / ".opencode/commands", REQUIRED_COMMANDS, kind="OpenCode command")
    check_exists(findings, root / ".opencode/skills", REQUIRED_SKILLS, kind="OpenCode skill")
    check_exists(findings, root / ".opencode/docs", REQUIRED_DOCS, kind="llmzk doc")
    check_exists(findings, root / ".opencode/llmzk-tools/src/llmzk_tools", REQUIRED_TOOLS, kind="llmzk tool module")
    check_tool_project(findings, root)
    check_exists(findings, root / "Templates", REQUIRED_TEMPLATES, kind="template")
    check_gitkeep(findings, root)
    check_llmzk_config(findings, root)
    check_opencode_config(findings, root)
    check_gitignore(findings, root)
    check_git_visibility(findings, root)
    check_no_nested_git(findings, root)
    check_git(findings, root, fail_if_dirty=fail_if_dirty)

    failures = [f for f in findings if f.level == "fail"]
    warnings = [f for f in findings if f.level == "warn"]
    if failures:
        exit_code = 1
    elif warnings and fail_if_dirty:
        exit_code = 1
    else:
        exit_code = 0

    if quiet_ok and exit_code == 0:
        findings = [Finding("ok", "Doctor passed")]
    return exit_code, findings


def doctor(
    vault: tyro.conf.Positional[Path] = Path("."),
    fail_if_dirty: bool = False,
    quiet_ok: bool = False,
    json: bool = False,
) -> int:
    """Check an installed llmzk vault.

    Args:
        vault: Path to the installed vault.
        fail_if_dirty: Fail if the vault Git working tree has uncommitted changes.
        quiet_ok: Only print a compact success line on pass.
        json: Print findings as JSON.
    """
    exit_code, findings = run_doctor(vault, fail_if_dirty=fail_if_dirty, quiet_ok=quiet_ok)
    if json:
        print(json_lib.dumps([f.__dict__ for f in findings], indent=2))
        return exit_code

    print(f"llmzk doctor: {vault.expanduser().resolve()}")
    print()
    for finding in findings:
        label = {"ok": "OK", "warn": "WARN", "fail": "FAIL"}[finding.level]
        if quiet_ok and finding.level == "ok" and finding.message != "Doctor passed":
            continue
        print(f"[{label}] {finding.message}")

    print()
    if exit_code == 0:
        print("Doctor result: passed")
    else:
        print("Doctor result: failed")
    return exit_code


def main() -> int:
    return tyro.cli(doctor)


if __name__ == "__main__":
    raise SystemExit(main())
