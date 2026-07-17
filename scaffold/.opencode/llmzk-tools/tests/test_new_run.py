from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from llmzk_tools.new_run import run, slugify


# slugify


def test_slugify_lowercases_and_replaces_non_alnum() -> None:
    assert slugify("Nielsen Backpropagation!") == "nielsen-backpropagation"


def test_slugify_strips_leading_trailing_dashes() -> None:
    assert slugify("---Foo Bar---") == "foo-bar"


def test_slugify_collapses_runs_of_separators() -> None:
    assert slugify("a   b/c.d") == "a-b-c-d"


def test_slugify_empty_falls_back_to_run() -> None:
    assert slugify("") == "run"


def test_slugify_only_punctuation_falls_back_to_run() -> None:
    assert slugify("!!! --- ???") == "run"


# run


def test_run_creates_passport_and_decision_log(tmp_path: Path) -> None:
    code = run("ingest", "Nielsen Backpropagation", tmp_path)
    assert code == 0
    today = dt.date.today().isoformat()
    workflow_id = f"{today}-ingest-nielsen-backpropagation"
    passport = tmp_path / "Logs" / "Passports" / f"{workflow_id}.md"
    decision = tmp_path / "Logs" / "Decision Logs" / f"{workflow_id}.md"
    assert passport.exists()
    assert decision.exists()
    ptext = passport.read_text(encoding="utf-8")
    assert "type: passport" in ptext
    assert f"workflow_id: {workflow_id}" in ptext
    assert "workflow_type: ingest" in ptext
    assert "status: started" in ptext
    assert "Nielsen Backpropagation" in ptext
    dtext = decision.read_text(encoding="utf-8")
    assert f"# Decision Log - {workflow_id}" in dtext
    assert "Nielsen Backpropagation" in dtext
    assert "Concept notes to create or update" in dtext
    assert "Notes deliberately not created" in dtext


@pytest.mark.parametrize("kind", ["ingest", "promote", "synthesize", "review"])
def test_run_supports_all_workflow_kinds(tmp_path: Path, kind: str) -> None:
    code = run(kind, "example", tmp_path)
    assert code == 0
    today = dt.date.today().isoformat()
    workflow_id = f"{today}-{kind}-example"
    assert (tmp_path / "Logs" / "Passports" / f"{workflow_id}.md").exists()
    assert (tmp_path / "Logs" / "Decision Logs" / f"{workflow_id}.md").exists()
    ptext = (tmp_path / "Logs" / "Passports" / f"{workflow_id}.md").read_text(encoding="utf-8")
    assert f"workflow_type: {kind}" in ptext


def test_run_is_idempotent_does_not_overwrite_existing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(dt, "date", type("FixedDate", (dt.date,), {"today": staticmethod(lambda: dt.date(2026, 1, 2))}))
    code = run("ingest", "example", tmp_path)
    assert code == 0
    passport = tmp_path / "Logs" / "Passports" / "2026-01-02-ingest-example.md"
    decision = tmp_path / "Logs" / "Decision Logs" / "2026-01-02-ingest-example.md"
    passport.write_text("CUSTOM-PASSPORT\n", encoding="utf-8")
    decision.write_text("CUSTOM-DECISION\n", encoding="utf-8")
    code = run("ingest", "example", tmp_path)
    assert code == 0
    assert passport.read_text(encoding="utf-8") == "CUSTOM-PASSPORT\n"
    assert decision.read_text(encoding="utf-8") == "CUSTOM-DECISION\n"


def test_run_prints_paths(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = run("ingest", "example", tmp_path)
    assert code == 0
    out = capsys.readouterr().out
    assert "Passports" in out
    assert "Decision Logs" in out


def test_run_workflow_id_uses_slugified_name(tmp_path: Path) -> None:
    code = run("promote", "Automatic Differentiation!", tmp_path)
    assert code == 0
    today = dt.date.today().isoformat()
    workflow_id = f"{today}-promote-automatic-differentiation"
    assert (tmp_path / "Logs" / "Passports" / f"{workflow_id}.md").exists()


def test_run_creates_log_directories_if_missing(tmp_path: Path) -> None:
    assert not (tmp_path / "Logs").exists()
    code = run("ingest", "example", tmp_path)
    assert code == 0
    assert (tmp_path / "Logs" / "Passports").is_dir()
    assert (tmp_path / "Logs" / "Decision Logs").is_dir()
