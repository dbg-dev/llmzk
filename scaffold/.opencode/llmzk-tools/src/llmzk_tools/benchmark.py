#!/usr/bin/env python3
"""Regression benchmark checks for llmzk-generated vaults.

This tool intentionally does not run an LLM. It checks an existing generated
vault against small, human-maintained benchmark expectations.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import fnmatch
import json as json_lib

import tyro
import yaml

from llmzk_tools.audit import audit
from llmzk_tools.config import LlmzkConfig, load_config
from llmzk_tools.frontmatter import parse_frontmatter
from llmzk_tools.wikilink import WIKILINK_RE, strip_wikilink_target


@dataclass
class Finding:
    case: str
    level: str
    check: str
    message: str


@dataclass
class CaseResult:
    name: str
    findings: list[Finding] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for f in self.findings if f.level == "pass")

    @property
    def warnings(self) -> int:
        return sum(1 for f in self.findings if f.level == "warn")

    @property
    def failed(self) -> int:
        return sum(1 for f in self.findings if f.level == "fail")

    @property
    def score(self) -> float:
        counted = self.passed + self.failed
        if counted == 0:
            return 100.0
        return round(100.0 * self.passed / counted, 1)


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Benchmark file must contain a YAML mapping: {path}")
    return data


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    data, body, _raw = parse_frontmatter(text)
    return data, body


def add(result: CaseResult, level: str, check: str, message: str) -> None:
    result.findings.append(Finding(result.name, level, check, message))


def canonical_item(item: str, config: LlmzkConfig) -> str:
    item = str(item).strip().strip("/")
    return config.to_local_target(item)


def resolve_item(vault: Path, item: str, config: LlmzkConfig) -> Path:
    direct = vault / str(item)
    if direct.exists():
        return direct
    canonical = canonical_item(str(item), config)
    candidate = vault / canonical
    if candidate.exists():
        return candidate
    if not canonical.endswith(".md") and str(item).endswith(".md"):
        return vault / f"{canonical}.md"
    return candidate


def path_exists(vault: Path, item: str, config: LlmzkConfig) -> bool:
    return resolve_item(vault, item, config).exists()


IGNORED_GLOB_PARTS = {".git", ".hg", ".svn", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "node_modules"}


def ignored_benchmark_path(path: Path) -> bool:
    """Return True for paths benchmark globs should never read.

    Benchmark globs are for checking generated vault files. Broad patterns such
    as `**/*.md` must not descend into Git internals, virtual environments,
    macOS metadata, or directories. Returning only regular files prevents
    `Path.read_text()` from being called on directories matched by broad globs.
    """
    if any(part in IGNORED_GLOB_PARTS for part in path.parts):
        return True
    if "__MACOSX" in path.parts:
        return True
    if path.name.startswith("._"):
        return True
    if path.name == ".DS_Store":
        return True
    return False


def glob_matches(vault: Path, pattern: str, config: LlmzkConfig) -> list[Path]:
    # pathlib glob is enough for normal glob patterns. Keep the output restricted
    # to readable files so text checks and artifact checks never try read_text()
    # on directories, .git paths, virtualenv files, or macOS metadata.
    patterns = [str(pattern)]
    seen: set[Path] = set()
    out: list[Path] = []
    for pat in patterns:
        for p in vault.glob(pat):
            if ignored_benchmark_path(p):
                continue
            if not p.is_file():
                continue
            if p not in seen:
                seen.add(p)
                out.append(p)
    return sorted(out)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _spec_label(spec: Any) -> str:
    if isinstance(spec, dict):
        for key in ("role", "name", "label", "description", "path", "glob"):
            if spec.get(key):
                return str(spec[key])
        for key in ("path_any_of", "glob_any_of", "target_any_of", "any_of"):
            values = _as_list(spec.get(key))
            if values:
                return "any_of(" + ", ".join(str(v) for v in values[:3]) + (")" if len(values) <= 3 else ", ...)")
        return str(spec)
    return str(spec)


def path_candidates(spec: Any) -> list[str]:
    """Return acceptable path candidates for file/text checks.

    Benchmark expectations should encode semantic roles with acceptable aliases
    instead of forcing one exact filename. Supported forms:

    - "04 Concept Notes/X.md"
    - {path: "04 Concept Notes/X.md"}
    - {path_any_of: ["04 Concept Notes/X.md", "04 Concept Notes/Y.md"]}
    - {any_of: [{path: "..."}, {path: "..."}]}
    """
    if isinstance(spec, str):
        return [spec]
    if not isinstance(spec, dict):
        return []
    out: list[str] = []
    out.extend(str(x) for x in _as_list(spec.get("path")))
    out.extend(str(x) for x in _as_list(spec.get("paths")))
    out.extend(str(x) for x in _as_list(spec.get("path_any_of")))
    for option in _as_list(spec.get("any_of")):
        out.extend(path_candidates(option))
    # preserve order while deduplicating
    return list(dict.fromkeys(x for x in out if x))


def glob_candidates(spec: Any) -> list[str]:
    if isinstance(spec, str):
        return [spec] if any(char in spec for char in "*?[]") else []
    if not isinstance(spec, dict):
        return []
    out: list[str] = []
    out.extend(str(x) for x in _as_list(spec.get("glob")))
    out.extend(str(x) for x in _as_list(spec.get("globs")))
    out.extend(str(x) for x in _as_list(spec.get("glob_any_of")))
    for option in _as_list(spec.get("any_of")):
        out.extend(glob_candidates(option))
    return list(dict.fromkeys(x for x in out if x))


def existing_paths(vault: Path, spec: Any, config: LlmzkConfig) -> list[Path]:
    out: list[Path] = []
    seen: set[Path] = set()
    for item in path_candidates(spec):
        path = resolve_item(vault, item, config)
        if path.exists() and path.is_file() and not ignored_benchmark_path(path) and path not in seen:
            seen.add(path)
            out.append(path)
    for pattern in glob_candidates(spec):
        for path in glob_matches(vault, pattern, config):
            if path not in seen:
                seen.add(path)
                out.append(path)
    return sorted(out)


def exclude_patterns(spec: Any) -> list[str]:
    if not isinstance(spec, dict):
        return []
    out: list[str] = []
    out.extend(str(x) for x in _as_list(spec.get("exclude")))
    out.extend(str(x) for x in _as_list(spec.get("exclude_glob")))
    out.extend(str(x) for x in _as_list(spec.get("exclude_globs")))
    return [x for x in out if x]


def excluded_by_spec(path: Path, vault: Path, spec: Any, config: LlmzkConfig) -> bool:
    rel_path = rel(path, vault).replace("\\", "/")
    canonical = canonical_item(rel_path, config).replace("\\", "/")
    for pattern in exclude_patterns(spec):
        pat = canonical_item(pattern, config).replace("\\", "/")
        variants = {pattern.replace("\\", "/"), pat}
        for variant in variants:
            if fnmatch.fnmatch(rel_path, variant) or fnmatch.fnmatch(canonical, variant):
                return True
            # Treat a bare folder exclusion like "Logs" as "Logs/**".
            stripped = variant.rstrip("/")
            if rel_path == stripped or rel_path.startswith(stripped + "/"):
                return True
            if canonical == stripped or canonical.startswith(stripped + "/"):
                return True
    return False


def text_targets(vault: Path, spec: dict[str, Any], config: LlmzkConfig) -> list[Path]:
    targets = existing_paths(vault, spec, config)
    return [p for p in targets if not excluded_by_spec(p, vault, spec, config)]


def check_required_files(result: CaseResult, vault: Path, required: list[Any], config: LlmzkConfig) -> None:
    for spec in required:
        matches = existing_paths(vault, spec, config)
        label = _spec_label(spec)
        if matches:
            add(result, "pass", "required_file", f"{label} -> {rel(matches[0], vault)}")
        else:
            candidates = path_candidates(spec) or glob_candidates(spec)
            add(result, "fail", "required_file", f"missing {label}: expected one of {candidates}")


def check_forbidden_files(result: CaseResult, vault: Path, forbidden: list[Any], config: LlmzkConfig) -> None:
    for spec in forbidden:
        label = _spec_label(spec)
        matches = existing_paths(vault, spec, config)
        if matches:
            add(result, "fail", "forbidden_file", f"forbidden {label} matched {len(matches)} file(s): {', '.join(rel(m, vault) for m in matches[:5])}")
        else:
            add(result, "pass", "forbidden_file", label)


def check_required_globs(result: CaseResult, vault: Path, items: list[dict[str, Any]], config: LlmzkConfig) -> None:
    for spec in items:
        min_count = int(spec.get("min", 1))
        patterns = glob_candidates(spec)
        matches = [m for m in existing_paths(vault, spec, config) if not excluded_by_spec(m, vault, spec, config)]
        label = _spec_label(spec)
        if len(matches) >= min_count:
            add(result, "pass", "required_glob", f"{label} matched {len(matches)}")
        else:
            add(result, "fail", "required_glob", f"{label} matched {len(matches)}, expected at least {min_count}; patterns={patterns}")


def check_required_text(result: CaseResult, vault: Path, items: list[dict[str, Any]], config: LlmzkConfig) -> None:
    for spec in items:
        targets = text_targets(vault, spec, config)
        label = _spec_label(spec)
        if not targets:
            add(result, "fail", "required_text", f"no target matched {label}: {spec}")
            continue
        # Default: every matching target must satisfy the text check. For alias
        # specs, set target_mode: any to accept the first semantically equivalent
        # note that satisfies the content condition.
        target_mode = str(spec.get("target_mode", "all"))
        target_findings: list[tuple[Path, list[str]]] = []
        for target in targets:
            text = target.read_text(encoding="utf-8")
            missing: list[str] = []
            for needle in spec.get("contains", []) or []:
                if str(needle) not in text:
                    missing.append(repr(str(needle)))
            any_needles = [str(n) for n in spec.get("contains_any", []) or []]
            if any_needles and not any(n in text for n in any_needles):
                missing.append("one of " + repr(any_needles))
            target_findings.append((target, missing))

        if target_mode == "any":
            ok_targets = [target for target, missing in target_findings if not missing]
            if ok_targets:
                add(result, "pass", "required_text", f"{label} satisfied by {rel(ok_targets[0], vault)}")
            else:
                add(result, "fail", "required_text", f"{label} not satisfied by any target: " + "; ".join(f"{rel(t, vault)} missing {m}" for t, m in target_findings))
            continue

        for target, missing in target_findings:
            if missing:
                for item in missing:
                    add(result, "fail", "required_text", f"{rel(target, vault)} missing {item}")
            else:
                add(result, "pass", "required_text", f"{rel(target, vault)} satisfied required text")


def check_forbidden_text(result: CaseResult, vault: Path, items: list[dict[str, Any]], config: LlmzkConfig) -> None:
    for spec in items:
        targets = text_targets(vault, spec, config)
        label = _spec_label(spec)
        if not targets:
            add(result, "warn", "forbidden_text", f"no target matched {label}: {spec}")
            continue
        for target in targets:
            text = target.read_text(encoding="utf-8")
            for needle in spec.get("contains", []) or []:
                if str(needle) in text:
                    add(result, "fail", "forbidden_text", f"{rel(target, vault)} contains forbidden text {needle!r}")
                else:
                    add(result, "pass", "forbidden_text", f"{rel(target, vault)} avoids {needle!r}")


def _wikilink_target(inner: str, config: LlmzkConfig) -> str:
    return config.to_local_target(strip_wikilink_target(inner))


def wikilink_target_candidates(spec: Any) -> list[str]:
    if isinstance(spec, str):
        return [spec]
    if not isinstance(spec, dict):
        return []
    out: list[str] = []
    out.extend(str(x) for x in _as_list(spec.get("target")))
    out.extend(str(x) for x in _as_list(spec.get("link")))
    out.extend(str(x) for x in _as_list(spec.get("target_any_of")))
    out.extend(str(x) for x in _as_list(spec.get("link_any_of")))
    for option in _as_list(spec.get("any_of")):
        out.extend(wikilink_target_candidates(option))
    return list(dict.fromkeys(x for x in out if x))


def check_required_wikilinks(result: CaseResult, vault: Path, items: list[dict[str, Any]], config: LlmzkConfig) -> None:
    for spec in items:
        targets = text_targets(vault, spec, config)
        label = _spec_label(spec)
        if not targets:
            add(result, "fail", "required_wikilink", f"missing target {label}: {spec}")
            continue
        for target in targets:
            text = target.read_text(encoding="utf-8")
            actual_targets = {_wikilink_target(m.group(1), config) for m in WIKILINK_RE.finditer(text)}
            for link in spec.get("links", []) or []:
                candidates = wikilink_target_candidates(link)
                expected_targets = []
                for candidate in candidates:
                    inner = candidate[2:-2] if candidate.startswith("[[") and candidate.endswith("]]") else candidate
                    expected_targets.append(_wikilink_target(inner, config))
                if any(expected in actual_targets for expected in expected_targets):
                    add(result, "pass", "required_wikilink", f"{rel(target, vault)} has one of {expected_targets}")
                else:
                    add(result, "fail", "required_wikilink", f"{rel(target, vault)} missing one of {expected_targets}")

def check_audit(result: CaseResult, vault: Path, spec: dict[str, Any]) -> None:
    if not spec:
        return
    issues = audit(vault)
    for key in spec.get("zero", []) or []:
        count = len(issues.get(str(key), []))
        if count == 0:
            add(result, "pass", "audit_zero", f"{key}: 0")
        else:
            add(result, "fail", "audit_zero", f"{key}: {count}")
    for key, limit in (spec.get("max", {}) or {}).items():
        count = len(issues.get(str(key), []))
        if count <= int(limit):
            add(result, "pass", "audit_max", f"{key}: {count} <= {limit}")
        else:
            add(result, "fail", "audit_max", f"{key}: {count} > {limit}")
    for key, minimum in (spec.get("min", {}) or {}).items():
        count = len(issues.get(str(key), []))
        if count >= int(minimum):
            add(result, "pass", "audit_min", f"{key}: {count} >= {minimum}")
        else:
            add(result, "fail", "audit_min", f"{key}: {count} < {minimum}")


def check_review_artifacts(result: CaseResult, vault: Path, spec: dict[str, Any], config: LlmzkConfig) -> None:
    if not spec:
        return
    for group_name, items in spec.items():
        if not isinstance(items, list):
            continue
        for item in items:
            min_count = int(item.get("min", 1))
            matches = [m for m in existing_paths(vault, item, config) if not excluded_by_spec(m, vault, item, config)]
            label = _spec_label(item)
            if len(matches) >= min_count:
                add(result, "pass", f"artifact_{group_name}", f"{label} matched {len(matches)}")
            else:
                patterns = glob_candidates(item) or path_candidates(item)
                add(result, "fail", f"artifact_{group_name}", f"{label} matched {len(matches)}, expected at least {min_count}; candidates={patterns}")
                continue
            wanted_status = item.get("status")
            if wanted_status:
                ok = False
                for match in matches:
                    data, _ = split_frontmatter(match.read_text(encoding="utf-8"))
                    if data.get("status") == wanted_status:
                        ok = True
                        break
                if ok:
                    add(result, "pass", f"artifact_{group_name}_status", f"{label} has status {wanted_status}")
                else:
                    add(result, "fail", f"artifact_{group_name}_status", f"{label} has no artifact with status {wanted_status}")


def run_case(case_file: Path, vault: Path) -> CaseResult:
    config = load_config(vault)
    data = read_yaml(case_file)
    result = CaseResult(name=str(data.get("name") or case_file.parent.name))
    checks = data.get("checks") or {}
    if not isinstance(checks, dict):
        add(result, "fail", "schema", "checks must be a mapping")
        return result

    check_required_files(result, vault, checks.get("required_files", []) or [], config)
    check_forbidden_files(result, vault, checks.get("forbidden_files", []) or [], config)
    check_required_globs(result, vault, checks.get("required_globs", []) or [], config)
    check_required_text(result, vault, checks.get("required_text", []) or [], config)
    check_forbidden_text(result, vault, checks.get("forbidden_text", []) or [], config)
    check_required_wikilinks(result, vault, checks.get("required_wikilinks", []) or [], config)
    check_review_artifacts(result, vault, checks.get("review_artifacts", {}) or {}, config)
    check_audit(result, vault, checks.get("audit", {}) or {})

    for item in data.get("manual_rubric", []) or []:
        add(result, "warn", "manual_rubric", str(item))
    return result


def discover_cases(path: Path) -> list[Path]:
    path = path.expanduser()
    if path.is_file():
        return [path]
    direct = path / "benchmark.yaml"
    if direct.exists():
        return [direct]
    return sorted(path.rglob("benchmark.yaml"))


def results_to_json(results: list[CaseResult]) -> list[dict[str, Any]]:
    return [
        {
            "name": result.name,
            "score": result.score,
            "passed": result.passed,
            "warnings": result.warnings,
            "failed": result.failed,
            "findings": [finding.__dict__ for finding in result.findings],
        }
        for result in results
    ]


def run(
    benchmark_path: tyro.conf.Positional[Path],
    vault: Path = Path("."),
    json: bool = False,
    fail_on_warn: bool = False,
) -> int:
    """Run llmzk regression benchmark expectations against an existing vault."""
    vault = vault.expanduser().resolve()
    cases = discover_cases(benchmark_path)
    if not cases:
        raise SystemExit(f"No benchmark.yaml files found under {benchmark_path}")

    results = [run_case(case, vault) for case in cases]
    if json:
        print(json_lib.dumps(results_to_json(results), indent=2))
    else:
        print(f"llmzk benchmark: {benchmark_path}")
        print(f"Vault: {vault}")
        print()
        for result in results:
            print(f"## {result.name}")
            print(f"Score: {result.score}/100  pass={result.passed} warn={result.warnings} fail={result.failed}")
            for finding in result.findings:
                if finding.level == "fail":
                    print(f"  [FAIL] {finding.check}: {finding.message}")
                elif finding.level == "warn":
                    print(f"  [WARN] {finding.check}: {finding.message}")
            print()
        total_pass = sum(r.passed for r in results)
        total_warn = sum(r.warnings for r in results)
        total_fail = sum(r.failed for r in results)
        counted = total_pass + total_fail
        score = 100.0 if counted == 0 else round(100.0 * total_pass / counted, 1)
        print(f"Overall: {score}/100  cases={len(results)} pass={total_pass} warn={total_warn} fail={total_fail}")

    failed = any(result.failed for result in results)
    warned = any(result.warnings for result in results)
    return 1 if failed or (fail_on_warn and warned) else 0


def main() -> int:
    return tyro.cli(run)


if __name__ == "__main__":
    raise SystemExit(main())
