from __future__ import annotations

from pathlib import Path

from llmzk_tools import doctor as doctor_mod


def messages(findings: list[doctor_mod.Finding], level: str) -> list[str]:
    return [finding.message for finding in findings if finding.level == level]


def write_config_text(root: Path, text: str) -> None:
    (root / ".llmzk.yaml").write_text(text, encoding="utf-8")


def test_doctor_reports_invalid_yaml_as_failure(tmp_path: Path) -> None:
    write_config_text(tmp_path, "schema_version: [\n")
    findings: list[doctor_mod.Finding] = []

    doctor_mod.check_llmzk_config(findings, tmp_path)

    assert any("Invalid .llmzk.yaml: invalid YAML" in message for message in messages(findings, "fail"))


def test_doctor_reports_invalid_schema_version_type(tmp_path: Path) -> None:
    write_config_text(
        tmp_path,
        "schema_version: unknown\n"
        "instance_name: research\n"
        "vault_relative_prefix: ''\n"
        "link_style: local\n"
        "installed_version: ''\n"
        "install_mode: copy\n"
        "source_path: ''\n",
    )
    findings: list[doctor_mod.Finding] = []

    doctor_mod.check_llmzk_config(findings, tmp_path)

    assert any("schema_version must be int; got str" in message for message in messages(findings, "fail"))


def test_doctor_reports_invalid_install_mode_as_failure(tmp_path: Path) -> None:
    write_config_text(
        tmp_path,
        "schema_version: 1\n"
        "instance_name: research\n"
        "vault_relative_prefix: ''\n"
        "link_style: local\n"
        "installed_version: ''\n"
        "install_mode: hardlink\n"
        "source_path: ''\n",
    )
    findings: list[doctor_mod.Finding] = []

    doctor_mod.check_llmzk_config(findings, tmp_path)

    assert any("install_mode must be one of" in message for message in messages(findings, "fail"))


def test_doctor_warns_on_unknown_configuration_key(tmp_path: Path) -> None:
    write_config_text(
        tmp_path,
        "schema_version: 1\n"
        "instance_name: research\n"
        "vault_relative_prefix: ''\n"
        "link_style: local\n"
        "installed_version: ''\n"
        "install_mode: copy\n"
        "source_path: ''\n"
        "instal_mode: copy\n",
    )
    findings: list[doctor_mod.Finding] = []

    doctor_mod.check_llmzk_config(findings, tmp_path)

    assert any("unknown configuration key: instal_mode" in message for message in messages(findings, "warn"))
    assert messages(findings, "fail") == []
