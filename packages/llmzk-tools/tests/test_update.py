from __future__ import annotations

from pathlib import Path

import pytest

from llmzk_tools import __version__
from llmzk_tools.config import load_config, write_config
from llmzk_tools import update as update_mod


DURABLE_SENTINELS = {
    "03 Permanent Notes/keep.md": "permanent knowledge\n",
    "04 Concept Notes/keep.md": "concept knowledge\n",
    "Logs/Decision Logs/keep.md": "log knowledge\n",
}


def write(path: Path, text: str = "x\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def make_source_repo(tmp_path: Path) -> tuple[Path, Path]:
    source = tmp_path / "source"
    scaffold = source / "scaffold"
    write(scaffold / "AGENTS.md", "new agents\n")
    write(scaffold / "opencode.json", '{"instructions": ["AGENTS.md"]}\n')
    write(scaffold / ".gitignore", ".venv/\n__MACOSX/\n.DS_Store\n")
    write(scaffold / ".opencode/commands/llmzk-update.md", "new update command\n")
    write(scaffold / ".opencode/llmzk-tools/.llmzk-generated", "generated\n")
    write(
        scaffold / ".opencode/llmzk-tools/pyproject.toml",
        '[project]\nname = "llmzk-tools"\nversion = "0.0.0"\n',
    )
    write(scaffold / ".opencode/llmzk-tools/src/llmzk_tools/update.py", "# update tool\n")
    write(scaffold / "Templates/concept-note.md", "new template\n")
    return source, scaffold


def make_vault(tmp_path: Path, *, install_mode: str = "copy") -> Path:
    vault = tmp_path / "vault"
    write(vault / "AGENTS.md", "old agents\n")
    write(vault / "opencode.json", "{}\n")
    write(vault / ".gitignore", "old\n")
    write(vault / ".opencode/commands/old.md", "old command\n")
    write(vault / "Templates/concept-note.md", "old template\n")
    for rel, text in DURABLE_SENTINELS.items():
        write(vault / rel, text)
    write_config(
        vault,
        instance_name="AI",
        vault_relative_prefix="AI",
        link_style="vault_relative",
        installed_version="0.5.5",
        install_mode=install_mode,
        source_path="",
    )
    return vault


def assert_durable_sentinels_preserved(vault: Path) -> None:
    for rel, text in DURABLE_SENTINELS.items():
        assert (vault / rel).read_text(encoding="utf-8") == text


def test_source_scaffold_requires_scaffold_directory(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        update_mod.source_scaffold(tmp_path / "not-a-source-repo")


@pytest.mark.parametrize("missing_name", [".llmzk-generated", "pyproject.toml"])
def test_source_scaffold_requires_assembled_tools(
    tmp_path: Path,
    missing_name: str,
) -> None:
    source, scaffold = make_source_repo(tmp_path)
    (scaffold / ".opencode" / "llmzk-tools" / missing_name).unlink()

    with pytest.raises(FileNotFoundError, match="Source scaffold is not assembled"):
        update_mod.source_scaffold(source)


def test_update_rejects_unassembled_source_without_mutating_vault(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source, scaffold = make_source_repo(tmp_path)
    vault = make_vault(tmp_path)
    installed_tool = write(
        vault / ".opencode/llmzk-tools/pyproject.toml",
        "installed tooling\n",
    )
    (scaffold / ".opencode/llmzk-tools/.llmzk-generated").unlink()

    exit_code = update_mod.update(
        vault,
        source=source,
        apply=True,
        allow_dirty=True,
    )

    assert exit_code == 1
    assert installed_tool.read_text(encoding="utf-8") == "installed tooling\n"
    assert (vault / "AGENTS.md").read_text(encoding="utf-8") == "old agents\n"
    assert_durable_sentinels_preserved(vault)
    assert "Source scaffold is not assembled" in capsys.readouterr().out


def test_iter_files_ignores_directories_git_caches_and_macos_metadata(tmp_path: Path) -> None:
    base = tmp_path / "base"
    write(base / "ok.md", "ok\n")
    write(base / ".git/config", "git\n")
    write(base / ".venv/lib/site.py", "venv\n")
    write(base / "__pycache__/x.pyc", "cache\n")
    write(base / ".DS_Store", "metadata\n")

    rels = {p.relative_to(base).as_posix() for p in update_mod.iter_files(base)}

    assert rels == {"ok.md"}


def test_plan_copy_reports_only_system_layer_changes(tmp_path: Path) -> None:
    _source, scaffold = make_source_repo(tmp_path)
    vault = make_vault(tmp_path)

    changes = update_mod.plan_copy(vault, scaffold)
    changed_paths = {c.path for c in changes if c.level == "change"}

    assert "AGENTS.md" in changed_paths
    assert ".opencode/commands/llmzk-update.md" in changed_paths
    assert "Templates/concept-note.md" in changed_paths
    for rel in DURABLE_SENTINELS:
        assert rel not in changed_paths
        assert not any(path.startswith(rel.split("/")[0] + "/") for path in changed_paths)


def test_apply_update_copy_updates_system_layer_and_preserves_durable_notes(tmp_path: Path) -> None:
    source, scaffold = make_source_repo(tmp_path)
    vault = make_vault(tmp_path)

    update_mod.apply_update(vault, scaffold, mode="copy", source=source)

    assert (vault / "AGENTS.md").read_text(encoding="utf-8") == "new agents\n"
    assert (vault / ".opencode/commands/llmzk-update.md").read_text(encoding="utf-8") == "new update command\n"
    assert (vault / "Templates/concept-note.md").read_text(encoding="utf-8") == "new template\n"
    assert not (vault / ".opencode").is_symlink()
    assert not (vault / "Templates").is_symlink()
    assert_durable_sentinels_preserved(vault)

    cfg = load_config(vault)
    assert cfg.instance_name == "AI"
    assert cfg.vault_relative_prefix == "AI"
    assert cfg.link_style == "vault_relative"
    assert cfg.installed_version == __version__
    assert cfg.install_mode == "copy"
    assert Path(cfg.source_path) == source.resolve()


def test_apply_update_symlink_links_system_dirs_and_preserves_durable_notes(tmp_path: Path) -> None:
    source, scaffold = make_source_repo(tmp_path)
    vault = make_vault(tmp_path, install_mode="symlink")

    update_mod.apply_update(vault, scaffold, mode="symlink", source=source)

    assert (vault / "AGENTS.md").read_text(encoding="utf-8") == "new agents\n"
    assert (vault / ".opencode").is_symlink()
    assert (vault / ".opencode").resolve() == (scaffold / ".opencode").resolve()
    assert (vault / "Templates").is_symlink()
    assert (vault / "Templates").resolve() == (scaffold / "Templates").resolve()
    assert_durable_sentinels_preserved(vault)

    cfg = load_config(vault)
    assert cfg.install_mode == "symlink"
    assert cfg.installed_version == __version__


def test_update_dry_run_does_not_mutate_vault(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source, _scaffold = make_source_repo(tmp_path)
    vault = make_vault(tmp_path)

    exit_code = update_mod.update(vault, source=source, apply=False, json=True)

    assert exit_code == 0
    assert (vault / "AGENTS.md").read_text(encoding="utf-8") == "old agents\n"
    assert (vault / "Templates/concept-note.md").read_text(encoding="utf-8") == "old template\n"
    assert_durable_sentinels_preserved(vault)
    assert "AGENTS.md" in capsys.readouterr().out


def test_update_apply_blocks_dirty_git_without_allow_dirty(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source, _scaffold = make_source_repo(tmp_path)
    vault = make_vault(tmp_path)
    monkeypatch.setattr(update_mod, "git_dirty", lambda root: (True, 3))

    exit_code = update_mod.update(vault, source=source, apply=True, allow_dirty=False, json=True)

    assert exit_code == 1
    assert (vault / "AGENTS.md").read_text(encoding="utf-8") == "old agents\n"
    assert_durable_sentinels_preserved(vault)


def test_update_apply_allows_dirty_when_explicitly_allowed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source, _scaffold = make_source_repo(tmp_path)
    vault = make_vault(tmp_path)
    monkeypatch.setattr(update_mod, "git_dirty", lambda root: (True, 3))

    exit_code = update_mod.update(vault, source=source, apply=True, allow_dirty=True, json=True)

    assert exit_code == 0
    assert (vault / "AGENTS.md").read_text(encoding="utf-8") == "new agents\n"
    assert_durable_sentinels_preserved(vault)


def test_plan_symlink_reports_directory_symlink_actions(tmp_path: Path) -> None:
    _source, scaffold = make_source_repo(tmp_path)
    vault = make_vault(tmp_path, install_mode="symlink")

    changes = update_mod.plan_symlink(vault, scaffold)
    actions = {(c.path, c.action) for c in changes if c.level == "change"}

    assert (".opencode", "symlink") in actions
    assert ("Templates", "symlink") in actions


def test_plan_copy_detects_stale_scaffold_files_not_in_upstream(tmp_path: Path) -> None:
    _source, scaffold = make_source_repo(tmp_path)
    vault = make_vault(tmp_path)
    write(vault / ".opencode" / "commands" / "llmzk-old-removed.md", "stale\n")
    write(vault / ".opencode" / "docs" / "OLD-REMOVED.md", "stale doc\n")
    write(vault / ".opencode" / "agents" / "zk-old-agent.md", "stale agent\n")

    changes = update_mod.plan_copy(vault, scaffold)
    stale = [c for c in changes if c.action == "delete"]

    stale_paths = {c.path for c in stale}
    assert ".opencode/commands/llmzk-old-removed.md" in stale_paths
    assert ".opencode/agents/zk-old-agent.md" in stale_paths
    for c in stale:
        assert "Stale scaffold file not in upstream" in c.message


def test_plan_copy_does_not_flag_user_files_as_stale(tmp_path: Path) -> None:
    _source, scaffold = make_source_repo(tmp_path)
    vault = make_vault(tmp_path)
    write(vault / ".opencode" / "commands" / "my-custom-command.md", "custom\n")
    write(vault / ".opencode" / "commands" / "README.md", "user readme\n")

    changes = update_mod.plan_copy(vault, scaffold)
    stale = [c for c in changes if c.action == "delete"]

    assert stale == []


def test_plan_copy_does_not_flag_scaffold_files_as_stale(tmp_path: Path) -> None:
    _source, scaffold = make_source_repo(tmp_path)
    vault = make_vault(tmp_path)

    changes = update_mod.plan_copy(vault, scaffold)
    stale = [c for c in changes if c.action == "delete"]

    assert stale == []


def test_apply_update_copy_deletes_stale_scaffold_files(tmp_path: Path) -> None:
    source, scaffold = make_source_repo(tmp_path)
    vault = make_vault(tmp_path)
    stale_file = write(vault / ".opencode" / "commands" / "llmzk-old-removed.md", "stale\n")

    update_mod.apply_update(vault, scaffold, mode="copy", source=source)

    assert not stale_file.exists()


def test_apply_update_copy_preserves_durable_files(tmp_path: Path) -> None:
    source, scaffold = make_source_repo(tmp_path)
    vault = make_vault(tmp_path)

    update_mod.apply_update(vault, scaffold, mode="copy", source=source)

    assert_durable_sentinels_preserved(vault)


def test_apply_update_copy_preserves_user_files(tmp_path: Path) -> None:
    source, scaffold = make_source_repo(tmp_path)
    vault = make_vault(tmp_path)
    user_file = write(vault / ".opencode" / "commands" / "my-custom-command.md", "custom\n")
    user_doc = write(vault / ".opencode" / "docs" / "my-notes.md", "notes\n")

    update_mod.apply_update(vault, scaffold, mode="copy", source=source)

    assert user_file.exists()
    assert user_file.read_text(encoding="utf-8") == "custom\n"
    assert user_doc.exists()
    assert user_doc.read_text(encoding="utf-8") == "notes\n"


def test_is_scaffold_managed_matches_llmzk_commands():
    assert update_mod.is_scaffold_managed(".opencode/commands/llmzk-audit.md")
    assert update_mod.is_scaffold_managed(".opencode/commands/llmzk-write-approved.md")


def test_is_scaffold_managed_matches_zk_agents():
    assert update_mod.is_scaffold_managed(".opencode/agents/zk-auditor.md")
    assert update_mod.is_scaffold_managed(".opencode/agents/zk-curator.md")


def test_is_scaffold_managed_matches_docs():
    assert update_mod.is_scaffold_managed(".opencode/docs/SOUL.md")
    assert update_mod.is_scaffold_managed(".opencode/docs/BENCHMARKS.md")


def test_is_scaffold_managed_matches_templates():
    assert update_mod.is_scaffold_managed("Templates/concept-note.md")
    assert update_mod.is_scaffold_managed("Templates/passport.md")


def test_is_scaffold_managed_matches_llmzk_tools():
    assert update_mod.is_scaffold_managed(".opencode/llmzk-tools/src/llmzk_tools/audit.py")
    assert update_mod.is_scaffold_managed(".opencode/llmzk-tools/pyproject.toml")


def test_is_scaffold_managed_matches_bin():
    assert update_mod.is_scaffold_managed(".opencode/bin/llmzk")


def test_is_scaffold_managed_does_not_match_user_files():
    assert not update_mod.is_scaffold_managed(".opencode/commands/my-custom-command.md")
    assert not update_mod.is_scaffold_managed(".opencode/commands/README.md")
    assert not update_mod.is_scaffold_managed(".opencode/agents/my-agent.md")
