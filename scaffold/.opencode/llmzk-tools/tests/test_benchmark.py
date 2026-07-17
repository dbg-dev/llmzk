from __future__ import annotations

import json as json_lib
from pathlib import Path

import pytest

from llmzk_tools.benchmark import (
    CaseResult,
    add,
    canonical_item,
    check_audit,
    check_forbidden_files,
    check_forbidden_text,
    check_required_files,
    check_required_globs,
    check_required_text,
    check_required_wikilinks,
    check_review_artifacts,
    discover_cases,
    excluded_by_spec,
    exclude_patterns,
    existing_paths,
    glob_candidates,
    glob_matches,
    ignored_benchmark_path,
    path_candidates,
    path_exists,
    read_yaml,
    rel,
    resolve_item,
    results_to_json,
    run,
    run_case,
    text_targets,
    wikilink_target_candidates,
)
from llmzk_tools.config import LlmzkConfig


def write(path: Path, text: str = "x\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def make_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    vault.mkdir()
    write(vault / ".llmzk.yaml", "schema_version: 1\ninstance_name: root\nvault_relative_prefix: ''\nlink_style: local\n")
    return vault


CFG = LlmzkConfig()


# --- CaseResult properties ---


def test_caseresult_counts_and_score():
    r = CaseResult(name="t")
    add(r, "pass", "c", "m")
    add(r, "fail", "c", "m")
    add(r, "warn", "c", "m")
    add(r, "pass", "c", "m")
    assert r.passed == 2
    assert r.warnings == 1
    assert r.failed == 1
    assert r.score == 66.7


def test_caseresult_score_no_checks():
    assert CaseResult(name="t").score == 100.0


# --- rel ---


def test_rel_relative(tmp_path: Path):
    assert rel(tmp_path / "a.md", tmp_path) == "a.md"


def test_rel_value_error_fallback(tmp_path: Path):
    other = tmp_path / "other"
    assert rel(other, tmp_path / "vault") == str(other)


# --- read_yaml ---


def test_read_yaml_dict(tmp_path: Path):
    p = write(tmp_path / "b.yaml", "name: t\nchecks: {}\n")
    assert read_yaml(p) == {"name": "t", "checks": {}}


def test_read_yaml_empty(tmp_path: Path):
    p = write(tmp_path / "b.yaml", "")
    assert read_yaml(p) == {}


def test_read_yaml_non_dict_raises(tmp_path: Path):
    p = write(tmp_path / "b.yaml", "- item\n")
    with pytest.raises(ValueError, match="YAML mapping"):
        read_yaml(p)


# --- canonical_item / resolve_item / path_exists ---


def test_canonical_item_strips_slashes():
    assert canonical_item("/X/", CFG) == "X"


def test_resolve_item_direct(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "X.md")
    assert resolve_item(vault, "04 Concept Notes/X.md", CFG) == vault / "04 Concept Notes" / "X.md"


def test_resolve_item_canonical_fallback(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "X.md")
    cfg = LlmzkConfig(vault_relative_prefix="AI", link_style="vault_relative")
    assert resolve_item(vault, "AI/04 Concept Notes/X.md", cfg) == vault / "04 Concept Notes" / "X.md"


def test_resolve_item_md_suffix_fallback(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "X.md")
    assert resolve_item(vault, "04 Concept Notes/X.md", CFG) == vault / "04 Concept Notes" / "X.md"


def test_resolve_item_missing_returns_candidate(tmp_path: Path):
    vault = make_vault(tmp_path)
    assert resolve_item(vault, "04 Concept Notes/Missing.md", CFG) == vault / "04 Concept Notes" / "Missing.md"


def test_path_exists_true_and_false(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "X.md")
    assert path_exists(vault, "04 Concept Notes/X.md", CFG)
    assert not path_exists(vault, "04 Concept Notes/Missing.md", CFG)


# --- ignored_benchmark_path ---


@pytest.mark.parametrize("path,ignored", [
    (Path("/v/.git/config"), True),
    (Path("/v/.venv/lib.py"), True),
    (Path("/v/__MACOSX/x"), True),
    (Path("/v/._file.md"), True),
    (Path("/v/.DS_Store"), True),
    (Path("/v/04 Concept Notes/X.md"), False),
])
def test_ignored_benchmark_path(path: Path, ignored: bool):
    assert ignored_benchmark_path(path) is ignored


# --- glob_matches ---


def test_glob_matches_files(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "A.md")
    write(vault / "04 Concept Notes" / "B.md")
    assert len(glob_matches(vault, "04 Concept Notes/*.md", CFG)) == 2


def test_glob_matches_skips_dirs_and_ignored(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "A.md")
    (vault / "04 Concept Notes" / "sub").mkdir()
    write(vault / ".git" / "ignored.md")
    results = glob_matches(vault, "**/*", CFG)
    assert all(p.is_file() for p in results)
    assert all(".git" not in p.parts for p in results)


# --- path_candidates ---


def test_path_candidates_string():
    assert path_candidates("a.md") == ["a.md"]


def test_path_candidates_dict_path():
    assert path_candidates({"path": "a.md"}) == ["a.md"]


def test_path_candidates_dict_paths_list():
    assert path_candidates({"paths": ["a.md", "b.md"]}) == ["a.md", "b.md"]


def test_path_candidates_path_any_of():
    assert path_candidates({"path_any_of": ["a.md", "b.md"]}) == ["a.md", "b.md"]


def test_path_candidates_any_of_nested():
    assert path_candidates({"any_of": [{"path": "a.md"}, {"path": "b.md"}]}) == ["a.md", "b.md"]


def test_path_candidates_non_dict():
    assert path_candidates(42) == []


def test_path_candidates_dedup():
    assert path_candidates({"path": "a.md", "path_any_of": ["a.md", "b.md"]}) == ["a.md", "b.md"]


# --- glob_candidates ---


def test_glob_candidates_string_wildcard():
    assert glob_candidates("*.md") == ["*.md"]


def test_glob_candidates_string_no_wildcard():
    assert glob_candidates("a.md") == []


def test_glob_candidates_dict_glob():
    assert glob_candidates({"glob": "**/*.md"}) == ["**/*.md"]


def test_glob_candidates_dict_globs():
    assert glob_candidates({"globs": ["a/*.md", "b/*.md"]}) == ["a/*.md", "b/*.md"]


def test_glob_candidates_glob_any_of():
    assert glob_candidates({"glob_any_of": ["a/*.md"]}) == ["a/*.md"]


def test_glob_candidates_non_dict():
    assert glob_candidates(42) == []


# --- existing_paths ---


def test_existing_paths_via_path(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "X.md")
    assert len(existing_paths(vault, "04 Concept Notes/X.md", CFG)) == 1


def test_existing_paths_via_glob(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "A.md")
    write(vault / "04 Concept Notes" / "B.md")
    assert len(existing_paths(vault, {"glob": "04 Concept Notes/*.md"}, CFG)) == 2


def test_existing_paths_dedup(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "X.md")
    spec = {"path": "04 Concept Notes/X.md", "glob": "04 Concept Notes/*.md"}
    assert len(existing_paths(vault, spec, CFG)) == 1


# --- exclude_patterns / excluded_by_spec ---


def test_exclude_patterns_from_dict():
    assert exclude_patterns({"exclude": ["Logs", "tmp"]}) == ["Logs", "tmp"]


def test_exclude_patterns_exclude_glob():
    assert exclude_patterns({"exclude_glob": ["*.tmp"]}) == ["*.tmp"]


def test_exclude_patterns_exclude_globs():
    assert exclude_patterns({"exclude_globs": ["a", "b"]}) == ["a", "b"]


def test_exclude_patterns_non_dict():
    assert exclude_patterns([]) == []


def test_excluded_by_spec_folder_prefix(tmp_path: Path):
    vault = make_vault(tmp_path)
    path = vault / "Logs" / "run.md"
    assert excluded_by_spec(path, vault, {"exclude": ["Logs"]}, CFG)


def test_excluded_by_spec_fnmatch(tmp_path: Path):
    vault = make_vault(tmp_path)
    path = vault / "tmp" / "x.md"
    assert excluded_by_spec(path, vault, {"exclude": ["tmp/*"]}, CFG)


def test_excluded_by_spec_not_excluded(tmp_path: Path):
    vault = make_vault(tmp_path)
    path = vault / "04 Concept Notes" / "X.md"
    assert not excluded_by_spec(path, vault, {"exclude": ["Logs"]}, CFG)


# --- text_targets ---


def test_text_targets_excludes(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "X.md", "content\n")
    write(vault / "Logs" / "run.md", "content\n")
    targets = text_targets(vault, {"glob": "**/*.md", "exclude": ["Logs"]}, CFG)
    assert all("Logs" not in str(t) for t in targets)


# --- check_required_files ---


def test_check_required_files_pass(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "X.md")
    r = CaseResult(name="t")
    check_required_files(r, vault, ["04 Concept Notes/X.md"], CFG)
    assert r.passed == 1
    assert r.failed == 0


def test_check_required_files_fail(tmp_path: Path):
    vault = make_vault(tmp_path)
    r = CaseResult(name="t")
    check_required_files(r, vault, ["04 Concept Notes/Missing.md"], CFG)
    assert r.failed == 1


# --- check_forbidden_files ---


def test_check_forbidden_files_pass(tmp_path: Path):
    vault = make_vault(tmp_path)
    r = CaseResult(name="t")
    check_forbidden_files(r, vault, ["04 Concept Notes/Missing.md"], CFG)
    assert r.passed == 1


def test_check_forbidden_files_fail(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "X.md")
    r = CaseResult(name="t")
    check_forbidden_files(r, vault, ["04 Concept Notes/X.md"], CFG)
    assert r.failed == 1


# --- check_required_globs ---


def test_check_required_globs_pass(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "A.md")
    write(vault / "04 Concept Notes" / "B.md")
    r = CaseResult(name="t")
    check_required_globs(r, vault, [{"glob": "04 Concept Notes/*.md", "min": 2}], CFG)
    assert r.passed == 1


def test_check_required_globs_fail_below_min(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "A.md")
    r = CaseResult(name="t")
    check_required_globs(r, vault, [{"glob": "04 Concept Notes/*.md", "min": 2}], CFG)
    assert r.failed == 1


# --- check_required_text ---


def test_check_required_text_all_mode_pass(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "X.md", "important phrase\n")
    r = CaseResult(name="t")
    check_required_text(r, vault, [{"path": "04 Concept Notes/X.md", "contains": ["important phrase"]}], CFG)
    assert r.passed == 1


def test_check_required_text_all_mode_fail(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "X.md", "other text\n")
    r = CaseResult(name="t")
    check_required_text(r, vault, [{"path": "04 Concept Notes/X.md", "contains": ["important phrase"]}], CFG)
    assert r.failed == 1


def test_check_required_text_any_mode_pass(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "X.md", "JVP\n")
    r = CaseResult(name="t")
    spec = {"path": "04 Concept Notes/X.md", "target_mode": "any", "contains_any": ["JVP", "tangent"]}
    check_required_text(r, vault, [spec], CFG)
    assert r.passed == 1


def test_check_required_text_any_mode_fail(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "X.md", "other\n")
    r = CaseResult(name="t")
    spec = {"path": "04 Concept Notes/X.md", "target_mode": "any", "contains_any": ["JVP", "tangent"]}
    check_required_text(r, vault, [spec], CFG)
    assert r.failed == 1


def test_check_required_text_no_target(tmp_path: Path):
    vault = make_vault(tmp_path)
    r = CaseResult(name="t")
    check_required_text(r, vault, [{"path": "04 Concept Notes/Missing.md", "contains": ["x"]}], CFG)
    assert r.failed == 1


# --- check_forbidden_text ---


def test_check_forbidden_text_pass(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "X.md", "clean text\n")
    r = CaseResult(name="t")
    check_forbidden_text(r, vault, [{"glob": "**/*.md", "contains": ["forbidden"]}], CFG)
    assert r.passed == 1


def test_check_forbidden_text_fail(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "X.md", "forbidden phrase\n")
    r = CaseResult(name="t")
    check_forbidden_text(r, vault, [{"glob": "**/*.md", "contains": ["forbidden"]}], CFG)
    assert r.failed == 1


def test_check_forbidden_text_no_target_warns(tmp_path: Path):
    vault = make_vault(tmp_path)
    r = CaseResult(name="t")
    check_forbidden_text(r, vault, [{"glob": "nonexistent/*.md", "contains": ["forbidden"]}], CFG)
    assert r.warnings == 1


# --- wikilink_target_candidates ---


def test_wikilink_target_candidates_string():
    assert wikilink_target_candidates("X") == ["X"]


def test_wikilink_target_candidates_dict_target():
    assert wikilink_target_candidates({"target": "X"}) == ["X"]


def test_wikilink_target_candidates_dict_link():
    assert wikilink_target_candidates({"link": "X"}) == ["X"]


def test_wikilink_target_candidates_target_any_of():
    assert wikilink_target_candidates({"target_any_of": ["X", "Y"]}) == ["X", "Y"]


def test_wikilink_target_candidates_link_any_of():
    assert wikilink_target_candidates({"link_any_of": ["X"]}) == ["X"]


def test_wikilink_target_candidates_any_of_nested():
    assert wikilink_target_candidates({"any_of": [{"target": "X"}, {"target": "Y"}]}) == ["X", "Y"]


def test_wikilink_target_candidates_non_dict():
    assert wikilink_target_candidates(42) == []


# --- check_required_wikilinks ---


def test_check_required_wikilinks_pass(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "07 Index Notes" / "I.md", "# Index\n\n- [[04 Concept Notes/X|X]]\n")
    r = CaseResult(name="t")
    spec = {"path": "07 Index Notes/I.md", "links": ["[[04 Concept Notes/X|X]]"]}
    check_required_wikilinks(r, vault, [spec], CFG)
    assert r.passed == 1


def test_check_required_wikilinks_fail(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "07 Index Notes" / "I.md", "# Index\n\n- [[Other]]\n")
    r = CaseResult(name="t")
    spec = {"path": "07 Index Notes/I.md", "links": ["[[04 Concept Notes/X|X]]"]}
    check_required_wikilinks(r, vault, [spec], CFG)
    assert r.failed == 1


def test_check_required_wikilinks_no_target(tmp_path: Path):
    vault = make_vault(tmp_path)
    r = CaseResult(name="t")
    spec = {"path": "07 Index Notes/Missing.md", "links": ["[[X]]"]}
    check_required_wikilinks(r, vault, [spec], CFG)
    assert r.failed == 1


# --- check_audit ---


def test_check_audit_zero_pass(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "X.md", "---\ntype: concept\n---\n\n# X\n")
    r = CaseResult(name="t")
    check_audit(r, vault, {"zero": ["unresolved-links"]})
    assert r.passed >= 1


def test_check_audit_zero_fail(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "X.md", "---\ntype: concept\n---\n\nSee [[Nonexistent]].\n")
    r = CaseResult(name="t")
    check_audit(r, vault, {"zero": ["unresolved-links"]})
    assert r.failed >= 1


def test_check_audit_max_pass(tmp_path: Path):
    vault = make_vault(tmp_path)
    r = CaseResult(name="t")
    check_audit(r, vault, {"max": {"unresolved-links": 100}})
    assert r.passed >= 1


def test_check_audit_max_fail(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "X.md", "---\ntype: concept\n---\n\nSee [[A]]. See [[B]].\n")
    r = CaseResult(name="t")
    check_audit(r, vault, {"max": {"unresolved-links": 0}})
    assert r.failed >= 1


def test_check_audit_min_pass(tmp_path: Path):
    vault = make_vault(tmp_path)
    r = CaseResult(name="t")
    check_audit(r, vault, {"min": {"unresolved-links": 0}})
    assert r.passed >= 1


def test_check_audit_min_fail(tmp_path: Path):
    vault = make_vault(tmp_path)
    r = CaseResult(name="t")
    check_audit(r, vault, {"min": {"unresolved-links": 100}})
    assert r.failed >= 1


def test_check_audit_empty_spec():
    r = CaseResult(name="t")
    check_audit(r, Path("/tmp"), {})
    assert len(r.findings) == 0


# --- check_review_artifacts ---


def test_check_review_artifacts_pass(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "Logs" / "Passports" / "run.md", "---\nstatus: started\n---\n\n# Run\n")
    r = CaseResult(name="t")
    spec = {"passports": [{"glob": "Logs/Passports/*.md", "min": 1}]}
    check_review_artifacts(r, vault, spec, CFG)
    assert r.passed >= 1


def test_check_review_artifacts_fail_below_min(tmp_path: Path):
    vault = make_vault(tmp_path)
    r = CaseResult(name="t")
    spec = {"passports": [{"glob": "Logs/Passports/*.md", "min": 1}]}
    check_review_artifacts(r, vault, spec, CFG)
    assert r.failed >= 1


def test_check_review_artifacts_status_pass(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "Logs" / "Passports" / "run.md", "---\nstatus: started\n---\n\n# Run\n")
    r = CaseResult(name="t")
    spec = {"passports": [{"glob": "Logs/Passports/*.md", "min": 1, "status": "started"}]}
    check_review_artifacts(r, vault, spec, CFG)
    assert r.passed >= 2


def test_check_review_artifacts_status_fail(tmp_path: Path):
    vault = make_vault(tmp_path)
    write(vault / "Logs" / "Passports" / "run.md", "---\nstatus: started\n---\n\n# Run\n")
    r = CaseResult(name="t")
    spec = {"passports": [{"glob": "Logs/Passports/*.md", "min": 1, "status": "applied"}]}
    check_review_artifacts(r, vault, spec, CFG)
    assert r.failed >= 1


def test_check_review_artifacts_non_list_items_skipped():
    r = CaseResult(name="t")
    check_review_artifacts(r, Path("/tmp"), {"bad": "not-a-list"}, CFG)
    assert len(r.findings) == 0


def test_check_review_artifacts_empty_spec():
    r = CaseResult(name="t")
    check_review_artifacts(r, Path("/tmp"), {}, CFG)
    assert len(r.findings) == 0


# --- run_case ---


def test_run_case_manual_rubric(tmp_path: Path):
    vault = make_vault(tmp_path)
    case = write(tmp_path / "case" / "benchmark.yaml", "name: t\nchecks: {}\nmanual_rubric:\n  - \"Check wording\"\n")
    result = run_case(case, vault)
    assert result.warnings == 1
    assert any("Check wording" in f.message for f in result.findings)


def test_run_case_checks_not_mapping(tmp_path: Path):
    vault = make_vault(tmp_path)
    case = write(tmp_path / "case" / "benchmark.yaml", "name: t\nchecks: \"not-a-dict\"\n")
    result = run_case(case, vault)
    assert result.failed == 1
    assert any("must be a mapping" in f.message for f in result.findings)


# --- discover_cases ---


def test_discover_cases_single_file(tmp_path: Path):
    p = write(tmp_path / "bench.yaml", "name: t\n")
    assert discover_cases(p) == [p]


def test_discover_cases_dir_with_direct_benchmark(tmp_path: Path):
    d = tmp_path / "case"
    d.mkdir()
    p = write(d / "benchmark.yaml", "name: t\n")
    assert discover_cases(d) == [p]


def test_discover_cases_dir_rglob(tmp_path: Path):
    p1 = write(tmp_path / "a" / "benchmark.yaml", "name: a\n")
    p2 = write(tmp_path / "b" / "benchmark.yaml", "name: b\n")
    found = discover_cases(tmp_path)
    assert sorted(found) == sorted([p1, p2])


# --- results_to_json ---


def test_results_to_json():
    r = CaseResult(name="t")
    add(r, "pass", "c", "m")
    data = results_to_json([r])
    assert data[0]["name"] == "t"
    assert data[0]["passed"] == 1
    assert data[0]["score"] == 100.0
    assert len(data[0]["findings"]) == 1


# --- run ---


def test_run_json_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "X.md")
    case_dir = tmp_path / "case"
    write(case_dir / "benchmark.yaml", "name: t\nchecks:\n  required_files:\n    - \"04 Concept Notes/X.md\"\n")
    code = run(case_dir, vault=vault, json=True)
    assert code == 0
    out = capsys.readouterr().out
    data = json_lib.loads(out)
    assert data[0]["name"] == "t"
    assert data[0]["passed"] >= 1


def test_run_text_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    vault = make_vault(tmp_path)
    write(vault / "04 Concept Notes" / "X.md")
    case_dir = tmp_path / "case"
    write(case_dir / "benchmark.yaml", "name: t\nchecks:\n  required_files:\n    - \"04 Concept Notes/X.md\"\n")
    code = run(case_dir, vault=vault)
    assert code == 0
    out = capsys.readouterr().out
    assert "Score:" in out
    assert "Overall:" in out


def test_run_fails_on_failed_check(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    vault = make_vault(tmp_path)
    case_dir = tmp_path / "case"
    write(case_dir / "benchmark.yaml", "name: t\nchecks:\n  required_files:\n    - \"04 Concept Notes/Missing.md\"\n")
    code = run(case_dir, vault=vault)
    assert code == 1


def test_run_fail_on_warn(tmp_path: Path):
    vault = make_vault(tmp_path)
    case_dir = tmp_path / "case"
    write(case_dir / "benchmark.yaml", "name: t\nchecks: {}\nmanual_rubric:\n  - \"check\"\n")
    code = run(case_dir, vault=vault, fail_on_warn=True)
    assert code == 1


def test_run_no_cases_raises(tmp_path: Path):
    vault = make_vault(tmp_path)
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(SystemExit, match="No benchmark.yaml"):
        run(empty, vault=vault)
