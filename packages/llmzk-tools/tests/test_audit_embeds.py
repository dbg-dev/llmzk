from pathlib import Path

from llmzk_tools.audit import audit


def test_audit_resolves_embedded_attachments(tmp_path: Path) -> None:
    media = tmp_path / "09 Media"
    media.mkdir()
    (media / "picture.png").write_bytes(b"image")
    notes = tmp_path / "01 Sources"
    notes.mkdir()
    (notes / "source.md").write_text(
        "![[picture.png|caption|500]]\n"
        "![[09 Media/picture.png|caption|500]]\n"
        "![[missing.png|caption|500]]\n"
        "![[wrong/picture.png|caption|500]]\n"
        "[[picture.png|caption|500]]\n",
        encoding="utf-8",
    )
    inbox = tmp_path / "00 Inbox"
    inbox.mkdir()
    (inbox / "raw.md").write_text(
        "![[picture.png|caption|500]]\n![[missing.png|caption|500]]\n",
        encoding="utf-8",
    )

    issues = audit(tmp_path)

    # The existing audit also includes inbox notes in this category.
    assert len(issues["unresolved-links"]) == 4
    assert any("missing.png" in issue for issue in issues["unresolved-links"])
    assert any("wrong/picture.png" in issue for issue in issues["unresolved-links"])
    assert len(issues["raw-inbox-unresolved-links"]) == 1
    assert "missing.png" in issues["raw-inbox-unresolved-links"][0]


def test_embedded_attachment_respects_configured_prefix(tmp_path: Path) -> None:
    (tmp_path / ".llmzk.yaml").write_text(
        "schema_version: 1\ninstance_name: AI\nvault_relative_prefix: AI\nlink_style: vault_relative\n",
        encoding="utf-8",
    )
    media = tmp_path / "09 Media"
    media.mkdir()
    (media / "picture.png").write_bytes(b"image")
    notes = tmp_path / "01 Sources"
    notes.mkdir()
    (notes / "source.md").write_text(
        "![[AI/09 Media/picture.png|caption|500]]\n"
        "![[Other/09 Media/picture.png|caption|500]]\n",
        encoding="utf-8",
    )

    issues = audit(tmp_path)

    assert len(issues["unresolved-links"]) == 1
    assert "Other/09 Media/picture.png" in issues["unresolved-links"][0]


def test_external_attachment_roots_are_opt_in(tmp_path: Path) -> None:
    vault = tmp_path / "instance"
    vault.mkdir()
    media = tmp_path / "img"
    media.mkdir()
    (media / "picture.png").write_bytes(b"image")
    notes = vault / "01 Sources"
    notes.mkdir()
    (notes / "source.md").write_text(
        "![[picture.png|caption|500]]\n"
        "![[img/picture.png|caption|500]]\n"
        "![[wrong/picture.png|caption|500]]\n"
        "![[missing.png|caption|500]]\n"
        "[[picture.png]]\n",
        encoding="utf-8",
    )
    assert len(audit(vault)["unresolved-links"]) == 5

    (vault / ".llmzk.yaml").write_text(
        "schema_version: 1\ninstance_name: test\nvault_relative_prefix: ''\n"
        "link_style: local\nattachment_roots:\n  - ../img\n",
        encoding="utf-8",
    )
    issues = audit(vault)["unresolved-links"]
    assert len(issues) == 3
    assert any("wrong/picture.png" in item for item in issues)
    assert any("missing.png" in item for item in issues)
    assert any("[[picture.png]]" in item for item in issues)
