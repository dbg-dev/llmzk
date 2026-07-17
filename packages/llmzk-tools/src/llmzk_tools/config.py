"""llmzk instance configuration.

An llmzk instance can either live at the Obsidian vault root or inside a
subfolder of a larger Obsidian vault.  The tools operate from the llmzk
instance root, but Obsidian links may be written relative to the outer vault.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, cast

import yaml

CONTENT_ROOTS = {
    "00 Inbox", "00 Fleeting Notes", "01 Sources", "02 Literature Notes",
    "03 Permanent Notes", "04 Concept Notes", "05 Bridge Notes",
    "06 Contradiction Notes", "07 Index Notes", "08 Wiki Articles", "09 Media",
}
LOG_ROOTS = {"Logs"}
KNOWN_ROOTS = CONTENT_ROOTS | LOG_ROOTS
DURABLE_ROOTS = CONTENT_ROOTS - {"00 Inbox", "00 Fleeting Notes", "09 Media"}


@dataclass(frozen=True)
class LlmzkConfig:
    schema_version: int = 1
    instance_name: str = "root"
    vault_relative_prefix: str = ""
    link_style: str = "local"  # local | vault_relative
    installed_version: str = ""
    install_mode: str = "copy"  # copy | symlink
    source_path: str = ""

    @property
    def prefix(self) -> str:
        return normalize_prefix(self.vault_relative_prefix)

    def strip_prefix(self, target: str) -> str:
        """Return target with the configured vault-relative prefix removed."""
        target = clean_target_string(target)
        prefix = self.prefix
        if prefix and target == prefix:
            return ""
        if prefix and target.startswith(prefix + "/"):
            return target[len(prefix) + 1:]
        return target

    def to_local_target(self, target: str) -> str:
        """Canonicalize a wikilink target to an llmzk-instance-relative target."""
        return self.strip_prefix(target)

    def render_target(self, local_target: str) -> str:
        """Render an instance-relative target according to the configured link style."""
        local_target = clean_target_string(local_target)
        if not local_target:
            return local_target
        if self.link_style == "vault_relative" and self.prefix and starts_with_known_root(local_target):
            if local_target == self.prefix or local_target.startswith(self.prefix + "/"):
                return local_target
            return f"{self.prefix}/{local_target}"
        return local_target


@dataclass(frozen=True)
class ConfigField:
    expected_type: type[object]
    required: bool
    default: object
    choices: frozenset[object] | None = None
    allow_empty: bool = True


CONFIG_SCHEMA: dict[str, ConfigField] = {
    "schema_version": ConfigField(int, True, 1, frozenset({1})),
    "instance_name": ConfigField(str, True, "root", allow_empty=False),
    "vault_relative_prefix": ConfigField(str, True, ""),
    "link_style": ConfigField(
        str, True, "local", frozenset({"local", "vault_relative"})
    ),
    "installed_version": ConfigField(str, False, ""),
    "install_mode": ConfigField(
        str, False, "copy", frozenset({"copy", "symlink"})
    ),
    "source_path": ConfigField(str, False, ""),
}


@dataclass(frozen=True)
class ConfigLoadResult:
    config: LlmzkConfig
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    present_keys: frozenset[str] = frozenset()

    @property
    def valid(self) -> bool:
        return not self.errors


def normalize_prefix(prefix: str | None) -> str:
    if not prefix:
        return ""
    return str(prefix).strip().strip("/")


def clean_target_string(target: str) -> str:
    target = str(target).strip().strip("/")
    if target.endswith(".md"):
        target = target[:-3]
    return target.strip().strip("/")


def starts_with_known_root(target: str) -> bool:
    target = clean_target_string(target)
    if not target:
        return False
    first = PurePosixPath(target).parts[0]
    return first in KNOWN_ROOTS


def local_markdown_path(target: str) -> PurePosixPath | None:
    target = clean_target_string(target)
    if not target or "/" not in target:
        return None
    rel = PurePosixPath(target)
    if rel.is_absolute() or any(part in {"", ".", ".."} for part in rel.parts):
        return None
    if not rel.parts or rel.parts[0] not in KNOWN_ROOTS:
        return None
    if rel.suffix != ".md":
        rel = PurePosixPath(str(rel) + ".md")
    return rel


def validate_config_data(data: Any) -> ConfigLoadResult:
    """Validate parsed YAML against the supported llmzk config schema."""
    if not isinstance(data, dict):
        return ConfigLoadResult(
            config=LlmzkConfig(),
            errors=("configuration must be a YAML mapping",),
        )

    errors: list[str] = []
    warnings: list[str] = []
    values: dict[str, object] = {}

    non_string_keys = [key for key in data if not isinstance(key, str)]
    if non_string_keys:
        rendered = ", ".join(repr(key) for key in non_string_keys)
        errors.append(f"configuration keys must be strings: {rendered}")

    present_keys = frozenset(key for key in data if isinstance(key, str))
    unknown_keys = sorted(present_keys - CONFIG_SCHEMA.keys())
    for key in unknown_keys:
        warnings.append(f"unknown configuration key: {key}")

    for name, field in CONFIG_SCHEMA.items():
        if name not in data:
            if field.required:
                errors.append(f"missing required key: {name}")
            values[name] = field.default
            continue

        value = data[name]
        if type(value) is not field.expected_type:
            expected = field.expected_type.__name__
            errors.append(
                f"{name} must be {expected}; got {type(value).__name__}"
            )
            values[name] = field.default
            continue

        if not field.allow_empty and value == "":
            errors.append(f"{name} must not be empty")
            values[name] = field.default
            continue

        if field.choices is not None and value not in field.choices:
            allowed = ", ".join(repr(item) for item in sorted(field.choices, key=str))
            errors.append(f"{name} must be one of {allowed}; got {value!r}")
            values[name] = field.default
            continue

        values[name] = value

    prefix = normalize_prefix(cast(str, values["vault_relative_prefix"]))
    config = LlmzkConfig(
        schema_version=cast(int, values["schema_version"]),
        instance_name=cast(str, values["instance_name"]),
        vault_relative_prefix=prefix,
        link_style=cast(str, values["link_style"]),
        installed_version=cast(str, values["installed_version"]),
        install_mode=cast(str, values["install_mode"]),
        source_path=cast(str, values["source_path"]),
    )
    return ConfigLoadResult(
        config=config,
        errors=tuple(errors),
        warnings=tuple(warnings),
        present_keys=present_keys,
    )


def load_config_result(root: Path) -> ConfigLoadResult:
    """Load and validate ``.llmzk.yaml`` without raising user-data errors."""
    path = root / ".llmzk.yaml"
    if not path.exists():
        return ConfigLoadResult(
            config=LlmzkConfig(),
            errors=("configuration file does not exist",),
        )

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return ConfigLoadResult(
            config=LlmzkConfig(),
            errors=(f"cannot read configuration: {exc}",),
        )

    try:
        data: Any = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        detail = str(exc).splitlines()[0]
        return ConfigLoadResult(
            config=LlmzkConfig(),
            errors=(f"invalid YAML: {detail}",),
        )

    return validate_config_data(data)


def load_config(root: Path) -> LlmzkConfig:
    """Load a validated config, falling back safely for non-strict callers."""
    return load_config_result(root).config


def yaml_scalar(value: object) -> str:
    """Render one YAML scalar without document-end markers.

    yaml.safe_dump(..., default_flow_style=True) emits a trailing "..."
    for plain scalars.  Inline config writing needs just the scalar text.
    """
    dumped = yaml.safe_dump(value, default_flow_style=True, width=10_000).strip()
    lines = [line for line in dumped.splitlines() if line.strip() != "..."]
    return " ".join(lines).strip()


def write_config(root: Path, *, instance_name: str, vault_relative_prefix: str = "", link_style: str = "local", installed_version: str = "", install_mode: str = "copy", source_path: str = "") -> None:
    result = validate_config_data(
        {
            "schema_version": 1,
            "instance_name": str(instance_name),
            "vault_relative_prefix": normalize_prefix(vault_relative_prefix),
            "link_style": link_style,
            "installed_version": str(installed_version),
            "install_mode": install_mode,
            "source_path": str(source_path),
        }
    )
    if result.errors:
        raise ValueError("Invalid llmzk config: " + "; ".join(result.errors))

    config = result.config
    text = (
        "# llmzk instance configuration\n"
        "# If this llmzk instance lives inside a larger Obsidian vault, set\n"
        "# vault_relative_prefix to the folder path from the Obsidian vault root.\n"
        f"schema_version: {config.schema_version}\n"
        f"instance_name: {yaml_scalar(config.instance_name)}\n"
        f"vault_relative_prefix: {yaml_scalar(config.vault_relative_prefix)}\n"
        f"link_style: {yaml_scalar(config.link_style)}\n"
        f"installed_version: {yaml_scalar(config.installed_version)}\n"
        f"install_mode: {yaml_scalar(config.install_mode)}\n"
        f"source_path: {yaml_scalar(config.source_path)}\n"
    )
    (root / ".llmzk.yaml").write_text(text, encoding="utf-8")
