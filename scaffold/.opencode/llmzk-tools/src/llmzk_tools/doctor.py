from __future__ import annotations

import json as json_lib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from git import GitCommandError, InvalidGitRepositoryError, NoSuchPathError, Repo
import tyro

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
    "Logs/Candidate Reviews",
    "Logs/Review Queue",
]

ROOT_FILES = ["AGENTS.md", "opencode.json", ".gitignore"]
REQUIRED_OPEN_CODE_DIRS = [
    ".opencode/commands",
    ".opencode/agents",
    ".opencode/skills",
    ".opencode/docs",
    ".opencode/llmzk-tools",
    ".opencode/llmzk-tools/src/llmzk_tools",
    ".opencode/bin",
]
REQUIRED_COMMANDS = [
    "llmzk-audit.md",
    "llmzk-doctor.md",
    "llmzk-fix-frontmatter.md",
    "llmzk-git-commit-message.md",
    "llmzk-git-diff.md",
    "llmzk-git-preflight.md",
    "llmzk-git-revert-run.md",
    "llmzk-git-status.md",
    "llmzk-ingest.md",
    "llmzk-write-approved.md",
    "llmzk-review-validate.md",
    "llmzk-promote-candidates.md",
    "llmzk-ingest-candidates.md",
    "llmzk-normalize-links.md",
    "llmzk-promote.md",
    "llmzk-review.md",
    "llmzk-synthesize.md",
]
REQUIRED_SKILLS = [
    "llmzk-audit/SKILL.md",
    "llmzk-git-safety/SKILL.md",
    "llmzk-ingest/SKILL.md",
    "llmzk-promote/SKILL.md",
    "llmzk-synthesize/SKILL.md",
]
REQUIRED_DOCS = [
    "SOUL.md",
    "STRUCTURE.md",
    "STYLE.md",
    "SCHEMA.md",
    "LINT_RULES.md",
    "GIT_POLICY.md",
    "OBSIDIAN_SKILLS.md",
]
REQUIRED_TOOLS = [
    "audit.py",
    "doctor.py",
    "fix_frontmatter.py",
    "git_safety.py",
    "new_run.py",
    "normalize_links.py",
    "review.py",
    "smoke_test.py",
]
REQUIRED_TEMPLATES = [
    "source-note.md",
    "literature-note.md",
    "permanent-note.md",
    "concept-note.md",
    "bridge-note.md",
    "contradiction-note.md",
    "index-note.md",
    "passport.md",
    "decision-log.md",
    "candidate-review.md",
]


@dataclass(frozen=True)
class Finding:
    level: str
    message: str


def add(findings: list[Finding], level: str, message: str) -> None:
    findings.append(Finding(level=level, message=message))


def check_exists(findings: list[Finding], root: Path, rel_paths: Iterable[str], *, kind: str) -> None:
    for rel in rel_paths:
        path = root / rel
        if path.exists() or path.is_symlink():
            add(findings, "ok", f"{kind} exists: {rel}")
        else:
            add(findings, "fail", f"Missing {kind}: {rel}")


def find_repo(root: Path) -> Repo | None:
    try:
        return Repo(root, search_parent_directories=True)
    except (InvalidGitRepositoryError, NoSuchPathError):
        return None


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

    dirty = [line for line in repo.git.status("--porcelain=v1").splitlines() if line.strip()]
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
        "llmzk-doctor",
        "llmzk-fix-frontmatter",
        "llmzk-git-safety",
        "llmzk-new-run",
        "llmzk-normalize-links",
        "llmzk-review",
        "llmzk-smoke-test",
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


def run_doctor(vault: Path, *, fail_if_dirty: bool = False, quiet_ok: bool = False) -> tuple[int, list[Finding]]:
    root = vault.expanduser().resolve()
    findings: list[Finding] = []
    if not root.exists():
        add(findings, "fail", f"Vault path does not exist: {root}")
        return 1, findings

    check_exists(findings, root, ROOT_FILES, kind="root file")
    check_exists(findings, root, REQUIRED_OPEN_CODE_DIRS, kind="OpenCode directory")
    check_exists(findings, root / ".opencode/commands", REQUIRED_COMMANDS, kind="OpenCode command")
    check_exists(findings, root / ".opencode/skills", REQUIRED_SKILLS, kind="OpenCode skill")
    check_exists(findings, root / ".opencode/docs", REQUIRED_DOCS, kind="llmzk doc")
    check_exists(findings, root / ".opencode/llmzk-tools/src/llmzk_tools", REQUIRED_TOOLS, kind="llmzk tool module")
    check_tool_project(findings, root)
    check_exists(findings, root / "Templates", REQUIRED_TEMPLATES, kind="template")
    check_gitkeep(findings, root)
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
    vault: Path,
    /,
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
