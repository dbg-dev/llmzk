"""llmzk instance configuration.

An llmzk instance can either live at the Obsidian vault root or inside a
subfolder of a larger Obsidian vault.  The tools operate from the llmzk
instance root, but Obsidian links may be written relative to the outer vault.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

CONTENT_ROOTS = {
    "00 Inbox", "00 Fleeting Notes", "01 Sources", "02 Literature Notes",
    "03 Permanent Notes", "04 Concept Notes", "05 Bridge Notes",
    "06 Contradiction Notes", "07 Index Notes", "08 Wiki Articles", "09 Media",
}
LOG_ROOTS = {"Logs"}
KNOWN_ROOTS = CONTENT_ROOTS | LOG_ROOTS
DURABLE_ROOTS = CONTENT_ROOTS - {"00 Inbox", "00 Fleeting Notes"}


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


def load_config(root: Path) -> LlmzkConfig:
    path = root / ".llmzk.yaml"
    if not path.exists():
        return LlmzkConfig()
    try:
        data: Any = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return LlmzkConfig()
    if not isinstance(data, dict):
        return LlmzkConfig()
    prefix = normalize_prefix(data.get("vault_relative_prefix", ""))
    link_style = str(data.get("link_style") or ("vault_relative" if prefix else "local"))
    if link_style not in {"local", "vault_relative"}:
        link_style = "vault_relative" if prefix else "local"
    return LlmzkConfig(
        schema_version=int(data.get("schema_version", 1) or 1),
        instance_name=str(data.get("instance_name") or (prefix or "root")),
        vault_relative_prefix=prefix,
        link_style=link_style,
        installed_version=str(data.get("installed_version") or ""),
        install_mode=str(data.get("install_mode") or "copy"),
        source_path=str(data.get("source_path") or ""),
    )


def yaml_scalar(value: object) -> str:
    """Render one YAML scalar without document-end markers.

    yaml.safe_dump(..., default_flow_style=True) emits a trailing "..."
    for plain scalars.  Inline config writing needs just the scalar text.
    """
    dumped = yaml.safe_dump(value, default_flow_style=True, width=10_000).strip()
    lines = [line for line in dumped.splitlines() if line.strip() != "..."]
    return " ".join(lines).strip()


def write_config(root: Path, *, instance_name: str, vault_relative_prefix: str = "", link_style: str = "local", installed_version: str = "", install_mode: str = "copy", source_path: str = "") -> None:
    prefix = normalize_prefix(vault_relative_prefix)
    if link_style not in {"local", "vault_relative"}:
        raise ValueError("link_style must be 'local' or 'vault_relative'")
    if install_mode not in {"copy", "symlink"}:
        raise ValueError("install_mode must be 'copy' or 'symlink'")
    text = (
        "# llmzk instance configuration\n"
        "# If this llmzk instance lives inside a larger Obsidian vault, set\n"
        "# vault_relative_prefix to the folder path from the Obsidian vault root.\n"
        "schema_version: 1\n"
        f"instance_name: {yaml_scalar(str(instance_name))}\n"
        f"vault_relative_prefix: {yaml_scalar(prefix)}\n"
        f"link_style: {yaml_scalar(link_style)}\n"
        f"installed_version: {yaml_scalar(str(installed_version))}\n"
        f"install_mode: {yaml_scalar(install_mode)}\n"
        f"source_path: {yaml_scalar(str(source_path))}\n"
    )
    (root / ".llmzk.yaml").write_text(text, encoding="utf-8")
