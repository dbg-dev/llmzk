from __future__ import annotations

from pathlib import Path

from llmzk_tools import update as update_mod


def test_update_rejects_invalid_config_before_reading_source(
    tmp_path: Path,
    capsys,
) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / ".llmzk.yaml").write_text(
        "schema_version: unknown\n"
        "instance_name: research\n"
        "vault_relative_prefix: ''\n"
        "link_style: local\n",
        encoding="utf-8",
    )

    code = update_mod.update(vault, source=tmp_path / "missing-source")

    assert code == 1
    output = capsys.readouterr().out
    assert "Invalid .llmzk.yaml" in output
    assert "schema_version must be int; got str" in output
    assert "Source repo does not contain scaffold" not in output
