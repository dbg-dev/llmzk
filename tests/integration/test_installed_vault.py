from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
UV_AVAILABLE = shutil.which("uv") is not None


def run(
    args: list[str | Path],
    *,
    cwd: Path,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "llmzk tests",
            "GIT_AUTHOR_EMAIL": "llmzk-tests@example.com",
            "GIT_COMMITTER_NAME": "llmzk tests",
            "GIT_COMMITTER_EMAIL": "llmzk-tests@example.com",
            "UV_OFFLINE": "1",
            "UV_LINK_MODE": "copy",
        }
    )
    completed = subprocess.run(
        [str(arg) for arg in args],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise AssertionError(f"command failed: {args}\n{detail}")
    return completed


def copy_source(tmp_path: Path) -> Path:
    source = tmp_path / "source"

    def ignore(directory: str, names: list[str]) -> set[str]:
        ignored = {name for name in names if name in {".git", ".venv", "__pycache__", ".pytest_cache"}}
        path = Path(directory)
        if path.name == ".opencode" and "llmzk-tools" in names:
            ignored.add("llmzk-tools")
        return ignored

    shutil.copytree(ROOT, source, symlinks=True, ignore=ignore)
    return source


def git_commit(repo: Path, message: str) -> None:
    run(["git", "add", "-A"], cwd=repo)
    run(["git", "commit", "-m", message], cwd=repo)


@pytest.mark.skipif(not UV_AVAILABLE, reason="uv is required for installed-wrapper tests")
def test_copy_install_doctor_and_update_preserve_durable_notes(tmp_path: Path) -> None:
    source = copy_source(tmp_path)
    vault = tmp_path / "vault"

    run(
        [
            source / "scripts/init-vault.sh",
            vault,
            "--mode",
            "copy",
            "--git",
            "--commit",
            "--no-doctor",
        ],
        cwd=source,
    )

    wrapper = vault / ".opencode/bin/llmzk"
    doctor = run([wrapper, "doctor", vault, "--quiet-ok"], cwd=vault)
    assert "Doctor passed" in doctor.stdout

    sentinel = vault / "04 Concept Notes/keep.md"
    sentinel.write_text("durable knowledge\n", encoding="utf-8")
    git_commit(vault, "add durable note")

    agents = source / "scaffold/AGENTS.md"
    agents.write_text(agents.read_text(encoding="utf-8") + "\n<!-- v5.8 integration -->\n")

    dry_run = run([source / "scripts/update-vault.sh", vault, "--no-doctor"], cwd=source)
    assert "AGENTS.md" in dry_run.stdout

    run(
        [source / "scripts/update-vault.sh", vault, "--apply", "--no-doctor"],
        cwd=source,
    )
    assert "v5.8 integration" in (vault / "AGENTS.md").read_text(encoding="utf-8")
    assert sentinel.read_text(encoding="utf-8") == "durable knowledge\n"


@pytest.mark.skipif(not UV_AVAILABLE, reason="uv is required for installed-wrapper tests")
def test_nested_instance_git_commands_ignore_parent_changes(tmp_path: Path) -> None:
    source = copy_source(tmp_path)
    outer = tmp_path / "Obsidian"
    instance = outer / "AI"
    outer.mkdir()
    run(["git", "init"], cwd=outer)
    (outer / "outside.md").write_text("outside original\n", encoding="utf-8")
    git_commit(outer, "init outer vault")

    run(
        [
            source / "scripts/init-vault.sh",
            instance,
            "--mode",
            "copy",
            "--no-git",
            "--no-doctor",
            "--vault-prefix",
            "AI",
        ],
        cwd=source,
    )
    git_commit(outer, "install llmzk instance")

    wrapper = instance / ".opencode/bin/llmzk"
    (outer / "outside.md").write_text("outside changed\n", encoding="utf-8")

    preflight = run([wrapper, "git", "preflight", instance], cwd=instance)
    assert "clean working tree" in preflight.stdout

    doctor = run(
        [wrapper, "doctor", instance, "--fail-if-dirty", "--quiet-ok"],
        cwd=instance,
    )
    assert "Doctor passed" in doctor.stdout

    (instance / "AGENTS.md").write_text("instance changed\n", encoding="utf-8")
    diff = run([wrapper, "git", "diff", instance], cwd=instance)
    assert "instance changed" in diff.stdout
    assert "outside changed" not in diff.stdout

    dirty = run([wrapper, "git", "preflight", instance], cwd=instance, check=False)
    assert dirty.returncode == 1
    assert "working tree is dirty" in dirty.stdout
