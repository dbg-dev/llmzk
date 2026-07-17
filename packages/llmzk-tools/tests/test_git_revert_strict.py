from __future__ import annotations

from pathlib import Path

import pytest
from git import Repo

from llmzk_tools.git_safety import (
    PassportOutputError,
    RevertRun,
    parse_output_paths,
    run_revert_run,
)


def write(path: Path, text: str = "x\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def make_repo(path: Path) -> Repo:
    path.mkdir(parents=True, exist_ok=True)
    repo = Repo.init(path)
    with repo.config_writer() as writer:
        writer.set_value("user", "name", "Test")
        writer.set_value("user", "email", "test@example.com")
    return repo


def commit_all(repo: Repo) -> None:
    repo.git.add(A=True)
    repo.index.commit("init")


def test_parse_output_paths_accepts_supported_forms() -> None:
    assert parse_output_paths("01 Sources/A.md") == ["01 Sources/A.md"]
    assert parse_output_paths(["01 Sources/A.md", "04 Concept Notes/B.md"]) == [
        "01 Sources/A.md",
        "04 Concept Notes/B.md",
    ]
    assert parse_output_paths(
        {"sources": ["01 Sources/A.md"], "concept_notes": "04 Concept Notes/B.md"}
    ) == ["01 Sources/A.md", "04 Concept Notes/B.md"]


def test_parse_output_paths_rejects_nested_or_non_string_values() -> None:
    with pytest.raises(PassportOutputError):
        parse_output_paths({"concept_notes": {"path": "04 Concept Notes/B.md"}})
    with pytest.raises(PassportOutputError):
        parse_output_paths(["01 Sources/A.md", 3])


def test_revert_run_rejects_invalid_schema_before_changes(tmp_path: Path) -> None:
    root = tmp_path / "vault"
    repo = make_repo(root)
    write(root / "tracked.md", "old\n")
    commit_all(repo)
    write(root / "tracked.md", "new\n")
    passport = write(root / "passport.yaml", "outputs:\n  created:\n    path: tracked.md\n")

    assert run_revert_run(RevertRun(passport=passport, path=root, apply=True)) == 1
    assert (root / "tracked.md").read_text(encoding="utf-8") == "new\n"


def test_revert_run_returns_nonzero_for_partial_refusal(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = tmp_path / "vault"
    repo = make_repo(root)
    write(root / "tracked.md", "old\n")
    commit_all(repo)
    write(root / "tracked.md", "new\n")
    passport = write(
        root / "passport.yaml",
        "outputs:\n - tracked.md\n - ../../outside.md\n",
    )

    assert run_revert_run(RevertRun(passport=passport, path=root, apply=True)) == 1
    assert (root / "tracked.md").read_text(encoding="utf-8") == "old\n"
    output = capsys.readouterr().out
    assert "refused=1" in output
    assert "restored=1" in output


def test_revert_run_refuses_tracked_directory_path(tmp_path: Path) -> None:
    root = tmp_path / "vault"
    repo = make_repo(root)
    write(root / "04 Concept Notes/sub/A.md", "old\n")
    commit_all(repo)
    write(root / "04 Concept Notes/sub/A.md", "new\n")
    passport = write(root / "passport.yaml", "outputs:\n - 04 Concept Notes/sub\n")

    assert run_revert_run(RevertRun(passport=passport, path=root, apply=True)) == 1
    assert (root / "04 Concept Notes/sub/A.md").read_text(encoding="utf-8") == "new\n"
