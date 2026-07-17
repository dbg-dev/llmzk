from __future__ import annotations

from pathlib import Path

import pytest
from git import Repo

from llmzk_tools.git_safety import (
    CommitMessage,
    Diff,
    Preflight,
    RevertRun,
    Status,
    flatten_paths,
    load_passport,
    porcelain,
    repo_root,
    run_commit_message,
    run_diff,
    run_preflight,
    run_revert_run,
    run_status,
)


def make_repo(path: Path) -> Repo:
    path.mkdir(parents=True, exist_ok=True)
    repo = Repo.init(path)
    with repo.config_writer() as cw:
        cw.set_value("user", "name", "Test")
        cw.set_value("user", "email", "test@example.com")
    return repo


def write(path: Path, text: str = "x\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def commit_all(repo: Repo, message: str = "init") -> None:
    repo.git.add(A=True)
    repo.index.commit(message)


# repo_root


def test_repo_root_returns_repo_for_initialized_repo(tmp_path: Path) -> None:
    make_repo(tmp_path)
    repo, root = repo_root(tmp_path)
    assert root == tmp_path.resolve()
    assert repo.working_tree_dir is not None


def test_repo_root_exits_for_non_git_dir(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        repo_root(tmp_path)


# porcelain


def test_porcelain_empty_for_clean_repo(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write(tmp_path / "a.md", "a\n")
    commit_all(repo)
    assert porcelain(repo) == []


def test_porcelain_reports_dirty_files(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write(tmp_path / "a.md", "a\n")
    commit_all(repo)
    write(tmp_path / "b.md", "b\n")
    lines = porcelain(repo)
    assert any("b.md" in line for line in lines)


# run_status


def test_run_status_clean_returns_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = make_repo(tmp_path)
    write(tmp_path / "a.md", "a\n")
    commit_all(repo)
    code = run_status(Status(path=tmp_path))
    assert code == 0
    assert "clean" in capsys.readouterr().out


def test_run_status_dirty_returns_zero_without_fail_if_dirty(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = make_repo(tmp_path)
    write(tmp_path / "a.md", "a\n")
    commit_all(repo)
    write(tmp_path / "b.md", "b\n")
    code = run_status(Status(path=tmp_path))
    assert code == 0
    assert "dirty" in capsys.readouterr().out


def test_run_status_dirty_returns_one_with_fail_if_dirty(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write(tmp_path / "a.md", "a\n")
    commit_all(repo)
    write(tmp_path / "b.md", "b\n")
    code = run_status(Status(path=tmp_path, fail_if_dirty=True))
    assert code == 1


# run_preflight


def test_run_preflight_clean_returns_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = make_repo(tmp_path)
    write(tmp_path / "a.md", "a\n")
    commit_all(repo)
    code = run_preflight(Preflight(path=tmp_path))
    assert code == 0
    assert "clean" in capsys.readouterr().out


def test_run_preflight_dirty_returns_one(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write(tmp_path / "a.md", "a\n")
    commit_all(repo)
    write(tmp_path / "b.md", "b\n")
    code = run_preflight(Preflight(path=tmp_path))
    assert code == 1


# run_diff


def test_run_diff_stat(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = make_repo(tmp_path)
    write(tmp_path / "a.md", "a\n")
    commit_all(repo)
    write(tmp_path / "a.md", "changed\n")
    code = run_diff(Diff(path=tmp_path, stat=True))
    assert code == 0
    assert "a.md" in capsys.readouterr().out


def test_run_diff_name_only(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = make_repo(tmp_path)
    write(tmp_path / "a.md", "a\n")
    commit_all(repo)
    write(tmp_path / "a.md", "changed\n")
    code = run_diff(Diff(path=tmp_path, name_only=True))
    assert code == 0
    assert "a.md" in capsys.readouterr().out


def test_run_diff_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = make_repo(tmp_path)
    write(tmp_path / "a.md", "a\n")
    write(tmp_path / "b.md", "b\n")
    commit_all(repo)
    write(tmp_path / "a.md", "changed a\n")
    write(tmp_path / "b.md", "changed b\n")
    code = run_diff(Diff(path=tmp_path, files=["a.md"]))
    assert code == 0
    out = capsys.readouterr().out
    assert "changed a" in out
    assert "changed b" not in out


def test_run_diff_default(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = make_repo(tmp_path)
    write(tmp_path / "a.md", "a\n")
    commit_all(repo)
    write(tmp_path / "a.md", "changed\n")
    code = run_diff(Diff(path=tmp_path))
    assert code == 0
    assert "changed" in capsys.readouterr().out


# load_passport


def test_load_passport_yaml(tmp_path: Path) -> None:
    p = tmp_path / "passport.yaml"
    p.write_text("workflow_id: run1\nworkflow_type: ingest\n", encoding="utf-8")
    data = load_passport(p)
    assert data["workflow_id"] == "run1"
    assert data["workflow_type"] == "ingest"


def test_load_passport_json(tmp_path: Path) -> None:
    p = tmp_path / "passport.json"
    p.write_text('{"workflow_id": "run1"}', encoding="utf-8")
    data = load_passport(p)
    assert data["workflow_id"] == "run1"


def test_load_passport_missing_exits(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        load_passport(tmp_path / "nope.yaml")


def test_load_passport_raw_fallback(tmp_path: Path) -> None:
    p = tmp_path / "passport.txt"
    p.write_text("just text\n", encoding="utf-8")
    data = load_passport(p)
    assert data["raw"] == "just text\n"


# flatten_paths


def test_flatten_paths_string_md() -> None:
    assert flatten_paths("01 Sources/Foo.md") == ["01 Sources/Foo.md"]


def test_flatten_paths_string_yaml() -> None:
    assert flatten_paths("Logs/Passports/run.yaml") == ["Logs/Passports/run.yaml"]


def test_flatten_paths_string_with_slash() -> None:
    assert flatten_paths("04 Concept Notes/X") == ["04 Concept Notes/X"]


def test_flatten_paths_string_plain_skipped() -> None:
    assert flatten_paths("Backpropagation") == []


def test_flatten_paths_list() -> None:
    paths = flatten_paths(["01 Sources/Foo.md", "Backpropagation", "04 Concept Notes/Y.md"])
    assert paths == ["01 Sources/Foo.md", "04 Concept Notes/Y.md"]


def test_flatten_paths_dict() -> None:
    data = {"outputs": ["01 Sources/Foo.md"], "id": "run1"}
    assert flatten_paths(data) == ["01 Sources/Foo.md"]


def test_flatten_paths_nested() -> None:
    data = {"a": {"b": ["01 Sources/Foo.md", "Logs/Passports/run.yaml"]}}
    assert flatten_paths(data) == ["01 Sources/Foo.md", "Logs/Passports/run.yaml"]


# run_commit_message


def test_run_commit_message_from_yaml_passport(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    p = tmp_path / "passport.yaml"
    p.write_text(
        "workflow_id: run1\nworkflow_type: ingest\ninput: 00 Inbox/foo.md\n"
        "outputs:\n  - 01 Sources/Source - Foo.md\n",
        encoding="utf-8",
    )
    code = run_commit_message(CommitMessage(passport=p))
    assert code == 0
    out = capsys.readouterr().out
    assert "llmzk: ingest run1" in out
    assert "00 Inbox/foo.md" in out
    assert "01 Sources/Source - Foo.md" in out


def test_run_commit_message_uses_stem_when_no_id(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    p = tmp_path / "my-run.yaml"
    p.write_text("workflow_type: ingest\n", encoding="utf-8")
    code = run_commit_message(CommitMessage(passport=p))
    assert code == 0
    out = capsys.readouterr().out
    assert "my-run" in out


# run_revert_run


def test_run_revert_run_dry_run_default_no_changes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = make_repo(tmp_path)
    write(tmp_path / "01 Sources" / "Foo.md", "original\n")
    commit_all(repo)
    write(tmp_path / "01 Sources" / "Foo.md", "modified\n")
    p = tmp_path / "passport.yaml"
    p.write_text("outputs:\n  - 01 Sources/Foo.md\n", encoding="utf-8")
    code = run_revert_run(RevertRun(passport=p, path=tmp_path))
    assert code == 0
    assert (tmp_path / "01 Sources" / "Foo.md").read_text(encoding="utf-8") == "modified\n"
    out = capsys.readouterr().out
    assert "Dry run" in out


def test_run_revert_run_apply_restores_tracked_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = make_repo(tmp_path)
    write(tmp_path / "01 Sources" / "Foo.md", "original\n")
    commit_all(repo)
    write(tmp_path / "01 Sources" / "Foo.md", "modified\n")
    p = tmp_path / "passport.yaml"
    p.write_text("outputs:\n  - 01 Sources/Foo.md\n", encoding="utf-8")
    code = run_revert_run(RevertRun(passport=p, path=tmp_path, apply=True))
    assert code == 0
    assert (tmp_path / "01 Sources" / "Foo.md").read_text(encoding="utf-8") == "original\n"
    assert "Restored" in capsys.readouterr().out


def test_run_revert_run_apply_deletes_untracked_generated_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = make_repo(tmp_path)
    write(tmp_path / "a.md", "a\n")
    commit_all(repo)
    write(tmp_path / "04 Concept Notes" / "Generated.md", "generated\n")
    p = tmp_path / "passport.yaml"
    p.write_text("outputs:\n  - 04 Concept Notes/Generated.md\n", encoding="utf-8")
    code = run_revert_run(RevertRun(passport=p, path=tmp_path, apply=True))
    assert code == 0
    assert not (tmp_path / "04 Concept Notes" / "Generated.md").exists()
    assert "Deleted" in capsys.readouterr().out


def test_run_revert_run_no_outputs_returns_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    make_repo(tmp_path)
    p = tmp_path / "passport.yaml"
    p.write_text("workflow_id: run1\n", encoding="utf-8")
    code = run_revert_run(RevertRun(passport=p, path=tmp_path))
    assert code == 1
    assert "Nothing to revert" in capsys.readouterr().out


def test_run_revert_run_refuses_to_delete_directory(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write(tmp_path / "a.md", "a\n")
    commit_all(repo)
    write(tmp_path / "04 Concept Notes" / "sub" / "Gen.md", "x\n")
    p = tmp_path / "passport.yaml"
    p.write_text("outputs:\n  - 04 Concept Notes/sub\n", encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        run_revert_run(RevertRun(passport=p, path=tmp_path, apply=True))
    assert "Refusing to delete" in str(exc.value)
