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
