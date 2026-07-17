from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from llmzk_tools import update as update_mod
from llmzk_tools.config import load_config, write_config
from llmzk_tools.update_transaction import SystemLayerTransaction, UpdateRollbackError


def write(path: Path, text: str = "x\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def make_source(tmp_path: Path) -> tuple[Path, Path]:
    source = tmp_path / "source"
    scaffold = source / "scaffold"
    write(scaffold / "AGENTS.md", "new agents\n")
    write(scaffold / "opencode.json", '{"instructions": ["AGENTS.md"]}\n')
    write(scaffold / ".gitignore", ".venv/\n")
    write(scaffold / ".opencode/commands/llmzk-update.md", "new command\n")
    write(scaffold / ".opencode/llmzk-tools/.llmzk-generated", "generated\n")
    write(
        scaffold / ".opencode/llmzk-tools/pyproject.toml",
        '[project]\nname = "llmzk-tools"\nversion = "0.0.0"\n',
    )
    write(scaffold / "Templates/concept-note.md", "new template\n")
    return source, scaffold


def make_vault(tmp_path: Path, *, mode: str = "copy") -> Path:
    vault = tmp_path / "vault"
    write(vault / "AGENTS.md", "old agents\n")
    write(vault / "opencode.json", "{}\n")
    write(vault / ".gitignore", "old\n")
    write(vault / ".opencode/commands/llmzk-update.md", "old command\n")
    write(vault / ".opencode/commands/llmzk-stale.md", "stale command\n")
    write(vault / ".opencode/commands/custom.md", "custom command\n")
    write(vault / "Templates/concept-note.md", "old template\n")
    write(vault / "04 Concept Notes/keep.md", "durable\n")
    write_config(
        vault,
        instance_name="AI",
        vault_relative_prefix="AI",
        link_style="vault_relative",
        installed_version="0.5.8.0",
        install_mode=mode,
        source_path="old-source",
    )
    return vault


def assert_original_vault(vault: Path) -> None:
    assert (vault / "AGENTS.md").read_text(encoding="utf-8") == "old agents\n"
    assert (vault / ".opencode/commands/llmzk-update.md").read_text(encoding="utf-8") == "old command\n"
    assert (vault / ".opencode/commands/llmzk-stale.md").read_text(encoding="utf-8") == "stale command\n"
    assert (vault / ".opencode/commands/custom.md").read_text(encoding="utf-8") == "custom command\n"
    assert (vault / "Templates/concept-note.md").read_text(encoding="utf-8") == "old template\n"
    assert (vault / "04 Concept Notes/keep.md").read_text(encoding="utf-8") == "durable\n"
    assert load_config(vault).installed_version == "0.5.8.0"
    assert not list(vault.glob(".llmzk-update-backup-*"))


def test_copy_update_rolls_back_after_mid_update_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source, scaffold = make_source(tmp_path)
    vault = make_vault(tmp_path)
    original = update_mod.copy_tree_overlay
    calls = 0

    def fail_on_second_tree(*args, **kwargs) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected copy failure")
        original(*args, **kwargs)

    monkeypatch.setattr(update_mod, "copy_tree_overlay", fail_on_second_tree)

    with pytest.raises(update_mod.UpdateApplyError, match="previous system layer restored"):
        update_mod.apply_update(vault, scaffold, mode="copy", source=source)

    assert_original_vault(vault)


def test_symlink_update_rolls_back_after_mid_update_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source, scaffold = make_source(tmp_path)
    vault = make_vault(tmp_path)
    original = update_mod.replace_with_symlink
    calls = 0

    def fail_on_second_link(source_path: Path, destination: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected symlink failure")
        original(source_path, destination)

    monkeypatch.setattr(update_mod, "replace_with_symlink", fail_on_second_link)

    with pytest.raises(update_mod.UpdateApplyError, match="previous system layer restored"):
        update_mod.apply_update(vault, scaffold, mode="symlink", source=source)

    assert not (vault / ".opencode").is_symlink()
    assert not (vault / "Templates").is_symlink()
    assert_original_vault(vault)


def test_update_command_reports_rolled_back_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    source, _scaffold = make_source(tmp_path)
    vault = make_vault(tmp_path)
    monkeypatch.setattr(update_mod, "git_dirty", lambda _root: (False, 0))
    monkeypatch.setattr(
        update_mod,
        "apply_update",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            update_mod.UpdateApplyError("Update failed; previous system layer restored")
        ),
    )

    code = update_mod.update(vault, source=source, apply=True)

    assert code == 1
    assert "previous system layer restored" in capsys.readouterr().out


def test_transaction_retains_backup_when_rollback_itself_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    write(vault / "AGENTS.md", "old\n")
    transaction = SystemLayerTransaction(vault, ["AGENTS.md"])
    monkeypatch.setattr(
        transaction,
        "restore",
        lambda: (_ for _ in ()).throw(OSError("rollback failure")),
    )

    with pytest.raises(UpdateRollbackError) as exc:
        with transaction:
            write(vault / "AGENTS.md", "new\n")
            raise OSError("apply failure")

    assert exc.value.backup_path.exists()
    assert (exc.value.backup_path / "AGENTS.md").read_text(encoding="utf-8") == "old\n"
    shutil.rmtree(exc.value.backup_path)
