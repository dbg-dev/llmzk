from __future__ import annotations

from pathlib import Path

from llmzk_tools import __version__
from llmzk_tools.config import write_config
from llmzk_tools import doctor as doctor_mod


def finding_messages(findings: list[doctor_mod.Finding], level: str | None = None) -> list[str]:
    return [f.message for f in findings if level is None or f.level == level]


def test_check_llmzk_config_accepts_matching_update_metadata(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    write_config(
        tmp_path,
        instance_name="AI",
        vault_relative_prefix="AI",
        link_style="vault_relative",
        installed_version=__version__,
        install_mode="copy",
        source_path=str(source),
    )
    findings: list[doctor_mod.Finding] = []

    doctor_mod.check_llmzk_config(findings, tmp_path)

    ok_messages = finding_messages(findings, "ok")
    assert any("version metadata matches" in msg for msg in ok_messages)
    assert any("Install mode recorded: copy" in msg for msg in ok_messages)
    assert any("Recorded source_path exists" in msg for msg in ok_messages)


def test_check_llmzk_config_warns_on_version_mismatch(tmp_path: Path) -> None:
    write_config(
        tmp_path,
        instance_name="AI",
        vault_relative_prefix="AI",
        link_style="vault_relative",
        installed_version="0.0.0",
        install_mode="copy",
        source_path="",
    )
    findings: list[doctor_mod.Finding] = []

    doctor_mod.check_llmzk_config(findings, tmp_path)

    warnings = finding_messages(findings, "warn")
    assert any("Version mismatch" in msg for msg in warnings)
    assert any("No source_path recorded" in msg for msg in warnings)


def test_check_llmzk_config_warns_when_symlink_mode_paths_are_not_symlinks(tmp_path: Path) -> None:
    (tmp_path / ".opencode").mkdir()
    (tmp_path / "Templates").mkdir()
    write_config(
        tmp_path,
        instance_name="AI",
        vault_relative_prefix="AI",
        link_style="vault_relative",
        installed_version=__version__,
        install_mode="symlink",
        source_path="",
    )
    findings: list[doctor_mod.Finding] = []

    doctor_mod.check_llmzk_config(findings, tmp_path)

    warnings = finding_messages(findings, "warn")
    assert any("install_mode is symlink but path is not a symlink: .opencode" in msg for msg in warnings)
    assert any("install_mode is symlink but path is not a symlink: Templates" in msg for msg in warnings)
