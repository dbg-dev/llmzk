from pathlib import Path

from git import Repo

from llmzk_tools.git_safety import (
    Diff,
    Preflight,
    RevertRun,
    Status,
    run_diff,
    run_preflight,
    run_revert_run,
    run_status,
)
from llmzk_tools.git_util import (
    git_context,
    git_dirty,
    instance_to_repo_path,
    porcelain,
)


def write(path: Path, text: str = "x\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def make_parent_repo(tmp_path: Path) -> tuple[Repo, Path, Path]:
    parent = tmp_path / "vault"
    instance = parent / "AI"
    instance.mkdir(parents=True)
    repo = Repo.init(parent)
    with repo.config_writer() as writer:
        writer.set_value("user", "name", "Test")
        writer.set_value("user", "email", "test@example.com")
    write(parent / "outside.md", "outside original\n")
    write(instance / "inside.md", "inside original\n")
    repo.git.add(A=True)
    repo.index.commit("init")
    return repo, parent, instance


def test_context_scopes_nested_instance(tmp_path: Path) -> None:
    _repo, parent, instance = make_parent_repo(tmp_path)
    context = git_context(instance)
    assert context is not None
    assert context.repo_root == parent.resolve()
    assert context.instance_root == instance.resolve()
    assert context.pathspec == "AI"


def test_porcelain_and_dirty_ignore_parent_changes(tmp_path: Path) -> None:
    repo, parent, instance = make_parent_repo(tmp_path)
    write(parent / "outside.md", "outside changed\n")
    context = git_context(instance)
    assert context is not None
    assert porcelain(repo, context.pathspec) == []
    assert git_dirty(instance) == (False, 0)


def test_status_and_preflight_ignore_parent_changes(tmp_path: Path) -> None:
    _repo, parent, instance = make_parent_repo(tmp_path)
    write(parent / "outside.md", "outside changed\n")
    assert run_status(Status(path=instance, fail_if_dirty=True)) == 0
    assert run_preflight(Preflight(path=instance)) == 0


def test_diff_is_scoped_to_instance(tmp_path: Path, capsys) -> None:
    _repo, parent, instance = make_parent_repo(tmp_path)
    write(parent / "outside.md", "outside changed\n")
    write(instance / "inside.md", "inside changed\n")
    assert run_diff(Diff(path=instance)) == 0
    output = capsys.readouterr().out
    assert "inside changed" in output
    assert "outside changed" not in output


def test_diff_file_paths_are_instance_relative(tmp_path: Path, capsys) -> None:
    _repo, parent, instance = make_parent_repo(tmp_path)
    write(parent / "outside.md", "outside changed\n")
    write(instance / "inside.md", "inside changed\n")
    assert run_diff(Diff(path=instance, files=["inside.md"])) == 0
    output = capsys.readouterr().out
    assert "inside changed" in output
    assert "outside changed" not in output


def test_revert_run_targets_instance_not_repo_root(tmp_path: Path) -> None:
    repo, parent, instance = make_parent_repo(tmp_path)
    write(parent / "04 Concept Notes" / "Foo.md", "root original\n")
    write(instance / "04 Concept Notes" / "Foo.md", "instance original\n")
    repo.git.add(A=True)
    repo.index.commit("notes")

    write(parent / "04 Concept Notes" / "Foo.md", "root changed\n")
    write(instance / "04 Concept Notes" / "Foo.md", "instance changed\n")
    passport = write(instance / "passport.yaml", "outputs:\n - 04 Concept Notes/Foo.md\n")

    assert run_revert_run(RevertRun(passport=passport, path=instance, apply=True)) == 0
    assert (instance / "04 Concept Notes" / "Foo.md").read_text() == "instance original\n"
    assert (parent / "04 Concept Notes" / "Foo.md").read_text() == "root changed\n"


def test_instance_path_cannot_escape_to_parent_repo(tmp_path: Path) -> None:
    _repo, parent, instance = make_parent_repo(tmp_path)
    context = git_context(instance)
    assert context is not None
    try:
        instance_to_repo_path(context, "../outside.md")
    except ValueError as exc:
        assert "escapes llmzk instance" in str(exc)
    else:
        raise AssertionError("path escape was accepted")
    assert (parent / "outside.md").exists()


def test_doctor_git_check_ignores_parent_changes(tmp_path: Path) -> None:
    from llmzk_tools import doctor as doctor_mod

    _repo, parent, instance = make_parent_repo(tmp_path)
    write(parent / "outside.md", "outside changed\n")
    findings: list[doctor_mod.Finding] = []

    doctor_mod.check_git(findings, instance, fail_if_dirty=True)

    assert not [finding for finding in findings if finding.level == "fail"]
    assert any("scoped to llmzk instance" in finding.message for finding in findings)


def test_doctor_git_visibility_uses_instance_prefix(tmp_path: Path) -> None:
    from llmzk_tools import doctor as doctor_mod

    repo, parent, instance = make_parent_repo(tmp_path)
    write(parent / ".gitignore", "AI/01 Sources/\n")
    repo.git.add(A=True)
    repo.index.commit("ignore instance source")
    findings: list[doctor_mod.Finding] = []

    doctor_mod.check_git_visibility(findings, instance)

    assert any(
        finding.level == "fail" and "01 Sources" in finding.message
        for finding in findings
    )
