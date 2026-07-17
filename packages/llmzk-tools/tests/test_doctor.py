from __future__ import annotations

import json as json_lib
import shutil
from pathlib import Path

import pytest
from git import Repo

from llmzk_tools import __version__
from llmzk_tools.config import write_config
from llmzk_tools import doctor as doctor_mod


def write(path: Path, text: str = "x\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def make_vault(tmp_path: Path, *, init_git: bool = True) -> Path:
    vault = tmp_path / "vault"
    vault.mkdir()
    for rel in doctor_mod.DOCTOR_ROOT_FILES:
        if rel == ".gitignore":
            write(vault / rel, ".venv/\n__MACOSX/\n.DS_Store\n")
        elif rel == "opencode.json":
            write(vault / rel, json_lib.dumps({"instructions": ["AGENTS.md"]}))
        elif rel == ".llmzk.yaml":
            write_config(
                vault,
                instance_name="root",
                vault_relative_prefix="",
                link_style="local",
                installed_version=__version__,
                install_mode="copy",
                source_path="",
            )
        else:
            write(vault / rel)
    for rel in doctor_mod.VAULT_FOLDERS:
        write(vault / rel / ".gitkeep")
    for rel in doctor_mod.LOG_FOLDERS:
        write(vault / rel / ".gitkeep")
    for rel in doctor_mod.REQUIRED_OPEN_CODE_DIRS:
        (vault / rel).mkdir(parents=True, exist_ok=True)
    for rel in doctor_mod.REQUIRED_COMMANDS:
        write(vault / ".opencode" / "commands" / rel)
    for rel in doctor_mod.REQUIRED_SKILLS:
        write(vault / ".opencode" / "skills" / rel)
    for rel in doctor_mod.REQUIRED_DOCS:
        write(vault / ".opencode" / "docs" / rel)
    for rel in doctor_mod.REQUIRED_TOOLS:
        write(vault / ".opencode" / "llmzk-tools" / "src" / "llmzk_tools" / rel)
    for rel in doctor_mod.REQUIRED_TEMPLATES:
        write(vault / "Templates" / rel)
    write(vault / ".opencode" / "bin" / "llmzk", "#!/usr/bin/env bash\n")
    pyproject = vault / ".opencode" / "llmzk-tools" / "pyproject.toml"
    write(
        pyproject,
        "[project.scripts]\n"
        "llmzk-audit = 'x'\n"
        "llmzk-benchmark = 'x'\n"
        "llmzk-doctor = 'x'\n"
        "llmzk-fix-frontmatter = 'x'\n"
        "llmzk-git-safety = 'x'\n"
        "llmzk-new-run = 'x'\n"
        "llmzk-normalize-links = 'x'\n"
        "llmzk-review = 'x'\n"
        "llmzk-update = 'x'\n"
        "[project]\ndependencies = ['tyro', 'gitpython', 'pyyaml']\n",
    )
    if init_git:
        repo = Repo.init(vault)
        with repo.config_writer() as cw:
            cw.set_value("user", "name", "Test")
            cw.set_value("user", "email", "test@example.com")
        repo.git.add(A=True)
        repo.index.commit("init")
    return vault


def finding_messages(findings: list[doctor_mod.Finding], level: str | None = None) -> list[str]:
    return [f.message for f in findings if level is None or f.level == level]


# check_exists


def test_check_exists_reports_ok_and_fail(tmp_path: Path) -> None:
    findings: list[doctor_mod.Finding] = []
    write(tmp_path / "present.md")
    doctor_mod.check_exists(findings, tmp_path, ["present.md", "missing.md"], kind="test")
    ok = finding_messages(findings, "ok")
    fail = finding_messages(findings, "fail")
    assert any("present.md" in m for m in ok)
    assert any("missing.md" in m for m in fail)


def test_check_exists_treats_symlink_as_present(tmp_path: Path) -> None:
    findings: list[doctor_mod.Finding] = []
    target = write(tmp_path / "target.md")
    (tmp_path / "link.md").symlink_to(target)
    doctor_mod.check_exists(findings, tmp_path, ["link.md"], kind="test")
    assert finding_messages(findings, "fail") == []


# find_repo


def test_find_repo_returns_none_for_non_git(tmp_path: Path) -> None:
    assert doctor_mod.find_repo(tmp_path) is None


def test_find_repo_returns_repo_for_git_dir(tmp_path: Path) -> None:
    Repo.init(tmp_path)
    assert doctor_mod.find_repo(tmp_path) is not None


# check_git


def test_check_git_clean(tmp_path: Path) -> None:
    Repo.init(tmp_path)
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_git(findings, tmp_path, fail_if_dirty=False)
    assert any("clean" in m for m in finding_messages(findings, "ok"))


def test_check_git_dirty_warns_by_default(tmp_path: Path) -> None:
    repo = Repo.init(tmp_path)
    with repo.config_writer() as cw:
        cw.set_value("user", "name", "Test")
        cw.set_value("user", "email", "test@example.com")
    write(tmp_path / "a.md")
    repo.git.add(A=True)
    repo.index.commit("init")
    write(tmp_path / "b.md", "dirty\n")
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_git(findings, tmp_path, fail_if_dirty=False)
    assert any("dirty" in m for m in finding_messages(findings, "warn"))


def test_check_git_dirty_fails_when_fail_if_dirty(tmp_path: Path) -> None:
    repo = Repo.init(tmp_path)
    with repo.config_writer() as cw:
        cw.set_value("user", "name", "Test")
        cw.set_value("user", "email", "test@example.com")
    write(tmp_path / "a.md")
    repo.git.add(A=True)
    repo.index.commit("init")
    write(tmp_path / "b.md", "dirty\n")
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_git(findings, tmp_path, fail_if_dirty=True)
    assert any("dirty" in m for m in finding_messages(findings, "fail"))


def test_check_git_no_repo_fails(tmp_path: Path) -> None:
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_git(findings, tmp_path, fail_if_dirty=False)
    assert any("not inside a Git repository" in m for m in finding_messages(findings, "fail"))


def test_check_git_scopes_instance_inside_parent_repo(tmp_path: Path) -> None:
    parent = tmp_path / "parent"
    parent.mkdir()
    Repo.init(parent)
    sub = parent / "sub"
    sub.mkdir()
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_git(findings, sub, fail_if_dirty=False)
    assert finding_messages(findings, "warn") == []
    assert any("scoped to llmzk instance" in m for m in finding_messages(findings, "ok"))

def test_check_opencode_config_missing_file_no_findings(tmp_path: Path) -> None:
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_opencode_config(findings, tmp_path)
    assert findings == []


def test_check_opencode_config_valid_instructions(tmp_path: Path) -> None:
    write(tmp_path / "AGENTS.md")
    write(tmp_path / "opencode.json", json_lib.dumps({"instructions": ["AGENTS.md"]}))
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_opencode_config(findings, tmp_path)
    assert any("AGENTS.md" in m for m in finding_messages(findings, "ok"))


def test_check_opencode_config_invalid_json(tmp_path: Path) -> None:
    write(tmp_path / "opencode.json", "{not json")
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_opencode_config(findings, tmp_path)
    assert any("not valid JSON" in m for m in finding_messages(findings, "fail"))


def test_check_opencode_config_instructions_not_list(tmp_path: Path) -> None:
    write(tmp_path / "opencode.json", json_lib.dumps({"instructions": "AGENTS.md"}))
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_opencode_config(findings, tmp_path)
    assert any("must be a list" in m for m in finding_messages(findings, "fail"))


def test_check_opencode_config_missing_instruction_path(tmp_path: Path) -> None:
    write(tmp_path / "opencode.json", json_lib.dumps({"instructions": ["missing.md"]}))
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_opencode_config(findings, tmp_path)
    assert any("instruction path missing" in m for m in finding_messages(findings, "fail"))


def test_check_opencode_config_non_string_instruction(tmp_path: Path) -> None:
    write(tmp_path / "opencode.json", json_lib.dumps({"instructions": [123]}))
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_opencode_config(findings, tmp_path)
    assert any("Invalid instruction entry" in m for m in finding_messages(findings, "fail"))


# check_gitignore


def test_check_gitignore_missing_file_no_findings(tmp_path: Path) -> None:
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_gitignore(findings, tmp_path)
    assert findings == []


def test_check_gitignore_has_all_fragments(tmp_path: Path) -> None:
    write(tmp_path / ".gitignore", ".venv/\n__MACOSX/\n.DS_Store\n")
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_gitignore(findings, tmp_path)
    assert finding_messages(findings, "warn") == []


def test_check_gitignore_missing_fragment_warns(tmp_path: Path) -> None:
    write(tmp_path / ".gitignore", ".venv/\n")
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_gitignore(findings, tmp_path)
    warns = finding_messages(findings, "warn")
    assert any("__MACOSX/" in m for m in warns)
    assert any(".DS_Store" in m for m in warns)


# check_git_visibility


def test_check_git_visibility_all_visible_in_clean_vault(tmp_path: Path) -> None:
    vault = make_vault(tmp_path)
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_git_visibility(findings, vault)
    assert finding_messages(findings, "fail") == []
    assert finding_messages(findings, "ok")


def test_check_git_visibility_reports_ignored_durable(tmp_path: Path) -> None:
    vault = make_vault(tmp_path)
    write(vault / ".gitignore", ".venv/\n__MACOSX/\n.DS_Store\n01 Sources/\n")
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_git_visibility(findings, vault)
    fails = finding_messages(findings, "fail")
    assert any("01 Sources" in m for m in fails)


def test_check_git_visibility_warns_when_no_git(tmp_path: Path) -> None:
    vault = make_vault(tmp_path, init_git=False)
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_git_visibility(findings, vault)
    assert any("Skipping Git visibility" in m for m in finding_messages(findings, "warn"))


# check_no_nested_git


def test_check_no_nested_git_clean(tmp_path: Path) -> None:
    vault = make_vault(tmp_path)
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_no_nested_git(findings, vault)
    assert finding_messages(findings, "fail") == []


def test_check_no_nested_git_detects_nested_repo(tmp_path: Path) -> None:
    vault = make_vault(tmp_path)
    Repo.init(vault / ".opencode" / "nested")
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_no_nested_git(findings, vault)
    fails = finding_messages(findings, "fail")
    assert any("Nested Git repository" in m for m in fails)


def test_check_no_nested_git_skips_missing_dirs(tmp_path: Path) -> None:
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_no_nested_git(findings, tmp_path)
    assert findings == []


# check_gitkeep


def test_check_gitkeep_all_present(tmp_path: Path) -> None:
    vault = make_vault(tmp_path)
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_gitkeep(findings, vault)
    assert finding_messages(findings, "fail") == []
    assert finding_messages(findings, "warn") == []


def test_check_gitkeep_missing_folder_fails(tmp_path: Path) -> None:
    vault = make_vault(tmp_path)
    shutil.rmtree(vault / "01 Sources")
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_gitkeep(findings, vault)
    assert any("Missing vault/log folder" in m for m in finding_messages(findings, "fail"))


def test_check_gitkeep_missing_placeholder_warns(tmp_path: Path) -> None:
    vault = make_vault(tmp_path)
    (vault / "01 Sources" / ".gitkeep").unlink()
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_gitkeep(findings, vault)
    assert any("Missing folder placeholder" in m for m in finding_messages(findings, "warn"))


# check_tool_project


def test_check_tool_project_complete(tmp_path: Path) -> None:
    vault = make_vault(tmp_path)
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_tool_project(findings, vault)
    assert finding_messages(findings, "fail") == []


def test_check_tool_project_missing_wrapper(tmp_path: Path) -> None:
    vault = make_vault(tmp_path)
    (vault / ".opencode" / "bin" / "llmzk").unlink()
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_tool_project(findings, vault)
    assert any("Missing llmzk wrapper" in m for m in finding_messages(findings, "fail"))


def test_check_tool_project_missing_pyproject(tmp_path: Path) -> None:
    vault = make_vault(tmp_path)
    (vault / ".opencode" / "llmzk-tools" / "pyproject.toml").unlink()
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_tool_project(findings, vault)
    assert any("Missing llmzk-tools pyproject.toml" in m for m in finding_messages(findings, "fail"))


def test_check_tool_project_missing_script_registration(tmp_path: Path) -> None:
    vault = make_vault(tmp_path)
    pyproject = vault / ".opencode" / "llmzk-tools" / "pyproject.toml"
    pyproject.write_text("[project.scripts]\nllmzk-audit = 'x'\n", encoding="utf-8")
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_tool_project(findings, vault)
    fails = finding_messages(findings, "fail")
    assert any("llmzk-doctor" in m for m in fails)


def test_check_tool_project_missing_dependency(tmp_path: Path) -> None:
    vault = make_vault(tmp_path)
    pyproject = vault / ".opencode" / "llmzk-tools" / "pyproject.toml"
    pyproject.write_text(
        "[project.scripts]\n"
        "llmzk-audit = 'x'\nllmzk-benchmark = 'x'\nllmzk-doctor = 'x'\n"
        "llmzk-fix-frontmatter = 'x'\nllmzk-git-safety = 'x'\nllmzk-new-run = 'x'\n"
        "llmzk-normalize-links = 'x'\nllmzk-review = 'x'\nllmzk-update = 'x'\n"
        "[project]\ndependencies = ['tyro', 'gitpython']\n",
        encoding="utf-8",
    )
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_tool_project(findings, vault)
    fails = finding_messages(findings, "fail")
    assert any("pyyaml" in m for m in fails)


# check_llmzk_config


def test_check_llmzk_config_missing_file_fails(tmp_path: Path) -> None:
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_llmzk_config(findings, tmp_path)
    assert any("Missing llmzk instance config" in m for m in finding_messages(findings, "fail"))


def test_check_llmzk_config_warns_on_empty_prefix_with_vault_relative(tmp_path: Path) -> None:
    write(tmp_path / ".llmzk.yaml", "schema_version: 1\ninstance_name: x\nlink_style: vault_relative\nvault_relative_prefix: \"\"\n")
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_llmzk_config(findings, tmp_path)
    assert any("vault_relative_prefix is empty" in m for m in finding_messages(findings, "warn"))


def test_check_llmzk_config_fails_on_unknown_install_mode(tmp_path: Path) -> None:
    write_config(tmp_path, instance_name="x", install_mode="copy")
    (tmp_path / ".llmzk.yaml").write_text(
        "schema_version: 1\ninstance_name: x\nvault_relative_prefix: ''\nlink_style: local\n"
        "installed_version: ''\ninstall_mode: weird\nsource_path: ''\n",
        encoding="utf-8",
    )
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_llmzk_config(findings, tmp_path)
    assert any("install_mode must be one of" in m for m in finding_messages(findings, "fail"))


def test_check_llmzk_config_source_path_does_not_exist(tmp_path: Path) -> None:
    write_config(tmp_path, instance_name="x", source_path="/nonexistent/path/xyz")
    findings: list[doctor_mod.Finding] = []
    doctor_mod.check_llmzk_config(findings, tmp_path)
    assert any("source_path does not exist" in m for m in finding_messages(findings, "warn"))


# run_doctor


def test_run_doctor_healthy_vault_passes(tmp_path: Path) -> None:
    vault = make_vault(tmp_path)
    code, findings = doctor_mod.run_doctor(vault)
    assert code == 0, finding_messages(findings, "fail")


def test_run_doctor_missing_path_fails(tmp_path: Path) -> None:
    code, findings = doctor_mod.run_doctor(tmp_path / "nope")
    assert code == 1
    assert any("Vault path does not exist" in m for m in finding_messages(findings, "fail"))


def test_run_doctor_missing_root_file_fails(tmp_path: Path) -> None:
    vault = make_vault(tmp_path)
    (vault / "AGENTS.md").unlink()
    code, findings = doctor_mod.run_doctor(vault)
    assert code == 1
    assert any("Missing root file: AGENTS.md" in m for m in finding_messages(findings, "fail"))


def test_run_doctor_missing_command_fails(tmp_path: Path) -> None:
    vault = make_vault(tmp_path)
    (vault / ".opencode" / "commands" / "llmzk-audit.md").unlink()
    code, findings = doctor_mod.run_doctor(vault)
    assert code == 1
    assert any("Missing OpenCode command: llmzk-audit.md" in m for m in finding_messages(findings, "fail"))


def test_run_doctor_quiet_ok_compacts_findings(tmp_path: Path) -> None:
    vault = make_vault(tmp_path)
    code, findings = doctor_mod.run_doctor(vault, quiet_ok=True)
    assert code == 0
    assert findings == [doctor_mod.Finding("ok", "Doctor passed")]


def test_run_doctor_warn_does_not_fail_by_default(tmp_path: Path) -> None:
    vault = make_vault(tmp_path)
    (vault / "01 Sources" / ".gitkeep").unlink()
    code, _ = doctor_mod.run_doctor(vault)
    assert code == 0


def test_run_doctor_non_git_warning_does_not_fail_when_fail_if_dirty(tmp_path: Path) -> None:
    vault = make_vault(tmp_path)
    (vault / "01 Sources" / ".gitkeep").unlink()
    repo = Repo(vault)
    repo.git.add(A=True)
    repo.index.commit("remove folder placeholder")

    code, _ = doctor_mod.run_doctor(vault, fail_if_dirty=True)

    assert code == 0

def test_doctor_json_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    vault = make_vault(tmp_path)
    code = doctor_mod.doctor(vault, json=True)
    assert code == 0
    out = capsys.readouterr().out
    data = json_lib.loads(out)
    assert isinstance(data, list)
    assert all("level" in d and "message" in d for d in data)


def test_doctor_text_output_passes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    vault = make_vault(tmp_path)
    code = doctor_mod.doctor(vault)
    assert code == 0
    out = capsys.readouterr().out
    assert "Doctor result: passed" in out


def test_doctor_text_output_fails(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    vault = make_vault(tmp_path)
    (vault / "AGENTS.md").unlink()
    code = doctor_mod.doctor(vault)
    assert code == 1
    out = capsys.readouterr().out
    assert "Doctor result: failed" in out


def test_doctor_quiet_ok(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    vault = make_vault(tmp_path)
    code = doctor_mod.doctor(vault, quiet_ok=True)
    assert code == 0
    out = capsys.readouterr().out
    assert "Doctor passed" in out
    assert "root file exists" not in out
