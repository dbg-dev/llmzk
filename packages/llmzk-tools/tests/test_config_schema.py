from __future__ import annotations

from pathlib import Path

from llmzk_tools.config import (
    LlmzkConfig,
    load_config,
    load_config_result,
    validate_config_data,
    write_config,
)


def valid_data() -> dict[str, object]:
    return {
        "schema_version": 1,
        "instance_name": "research",
        "vault_relative_prefix": "AI",
        "link_style": "vault_relative",
        "installed_version": "0.5.7.2",
        "install_mode": "copy",
        "source_path": "/tmp/llmzk",
    }


def test_validate_config_accepts_supported_schema() -> None:
    result = validate_config_data(valid_data())

    assert result.valid
    assert result.errors == ()
    assert result.warnings == ()
    assert result.config.instance_name == "research"
    assert result.config.prefix == "AI"


def test_validate_config_rejects_non_mapping() -> None:
    result = validate_config_data(["not", "a", "mapping"])

    assert not result.valid
    assert result.config == LlmzkConfig()
    assert "must be a YAML mapping" in result.errors[0]


def test_validate_config_rejects_wrong_field_type() -> None:
    data = valid_data()
    data["schema_version"] = "1"

    result = validate_config_data(data)

    assert not result.valid
    assert "schema_version must be int; got str" in result.errors


def test_validate_config_rejects_bool_as_integer() -> None:
    data = valid_data()
    data["schema_version"] = True

    result = validate_config_data(data)

    assert "schema_version must be int; got bool" in result.errors


def test_validate_config_rejects_unsupported_schema_version() -> None:
    data = valid_data()
    data["schema_version"] = 2

    result = validate_config_data(data)

    assert any("schema_version must be one of 1" in error for error in result.errors)


def test_validate_config_rejects_missing_required_key() -> None:
    data = valid_data()
    del data["instance_name"]

    result = validate_config_data(data)

    assert "missing required key: instance_name" in result.errors


def test_validate_config_rejects_empty_instance_name() -> None:
    data = valid_data()
    data["instance_name"] = ""

    result = validate_config_data(data)

    assert "instance_name must not be empty" in result.errors


def test_validate_config_rejects_unknown_enum_value() -> None:
    data = valid_data()
    data["install_mode"] = "hardlink"

    result = validate_config_data(data)

    assert any("install_mode must be one of" in error for error in result.errors)


def test_validate_config_warns_on_unknown_key() -> None:
    data = valid_data()
    data["instal_mode"] = "copy"

    result = validate_config_data(data)

    assert result.valid
    assert result.warnings == ("unknown configuration key: instal_mode",)


def test_load_config_result_reports_invalid_yaml(tmp_path: Path) -> None:
    (tmp_path / ".llmzk.yaml").write_text("schema_version: [\n", encoding="utf-8")

    result = load_config_result(tmp_path)

    assert not result.valid
    assert result.errors[0].startswith("invalid YAML:")


def test_load_config_never_raises_for_invalid_values(tmp_path: Path) -> None:
    (tmp_path / ".llmzk.yaml").write_text(
        "schema_version: unknown\ninstance_name: x\n"
        "vault_relative_prefix: ''\nlink_style: local\n",
        encoding="utf-8",
    )

    assert load_config(tmp_path) == LlmzkConfig(instance_name="x")


def test_write_config_round_trips_through_schema(tmp_path: Path) -> None:
    write_config(
        tmp_path,
        instance_name="research",
        vault_relative_prefix="AI",
        link_style="vault_relative",
        installed_version="0.5.7.2",
        install_mode="symlink",
        source_path="/tmp/source",
    )

    result = load_config_result(tmp_path)

    assert result.valid
    assert result.config.instance_name == "research"
    assert result.config.install_mode == "symlink"


def test_write_config_rejects_values_outside_schema(tmp_path: Path) -> None:
    try:
        write_config(tmp_path, instance_name="", install_mode="hardlink")
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("write_config accepted invalid schema values")

    assert "instance_name must not be empty" in message
    assert "install_mode must be one of" in message
