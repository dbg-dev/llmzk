from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run_build(*args: str) -> subprocess.CompletedProcess[str]:
    root = repo_root()
    return subprocess.run(
        [sys.executable, str(root / "scripts" / "build-scaffold.py"), *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def test_source_first_layout() -> None:
    root = repo_root()
    assert (root / "packages" / "llmzk-tools" / "pyproject.toml").is_file()
    assert (root / "scripts" / "build-scaffold.py").is_file()


def test_build_and_drift_check(tmp_path: Path) -> None:
    target = tmp_path / "scaffold" / ".opencode" / "llmzk-tools"

    built = run_build("--target", str(target))
    assert built.returncode == 0, built.stderr or built.stdout
    assert (target / "pyproject.toml").is_file()
    assert (target / ".llmzk-generated").is_file()

    clean = run_build("--target", str(target), "--check")
    assert clean.returncode == 0, clean.stderr or clean.stdout

    (target / "pyproject.toml").write_text("drift\n", encoding="utf-8")
    drift = run_build("--target", str(target), "--check")
    assert drift.returncode == 1
    assert "changed: pyproject.toml" in drift.stdout
