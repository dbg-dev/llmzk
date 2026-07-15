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
import re

import tyro
import yaml

from llmzk_tools.audit import audit
from llmzk_tools.config import LlmzkConfig, load_config

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


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
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        data = {}
    if not isinstance(data, dict):
        data = {}
    return data, text[match.end():]


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
    return False


def glob_matches(vault: Path, pattern: str, config: LlmzkConfig) -> list[Path]:
    # pathlib glob is enough for normal glob patterns. Keep the output restricted
    # to readable files so text checks and artifact checks never try read_text()
    # on directories, .git paths, virtualenv files, or macOS metadata.
    patterns = [str(pattern)]
    canonical = canonical_item(str(pattern), config)
    if canonical not in patterns:
        patterns.append(canonical)
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


def check_required_files(result: CaseResult, vault: Path, required: list[str], config: LlmzkConfig) -> None:
    for item in required:
        if path_exists(vault, item, config):
            add(result, "pass", "required_file", item)
        else:
            add(result, "fail", "required_file", f"missing: {item}")


def check_forbidden_files(result: CaseResult, vault: Path, forbidden: list[str], config: LlmzkConfig) -> None:
    for item in forbidden:
        if any(char in item for char in "*?[]"):
            matches = glob_matches(vault, item, config)
            if matches:
                add(result, "fail", "forbidden_file", f"forbidden pattern matched {len(matches)} file(s): {item}")
            else:
                add(result, "pass", "forbidden_file", item)
        elif path_exists(vault, item, config):
            add(result, "fail", "forbidden_file", f"exists: {item}")
        else:
            add(result, "pass", "forbidden_file", item)


def check_required_globs(result: CaseResult, vault: Path, items: list[dict[str, Any]], config: LlmzkConfig) -> None:
    for spec in items:
        pattern = str(spec.get("glob", ""))
        min_count = int(spec.get("min", 1))
        matches = glob_matches(vault, pattern, config)
        if len(matches) >= min_count:
            add(result, "pass", "required_glob", f"{pattern} matched {len(matches)}")
        else:
            add(result, "fail", "required_glob", f"{pattern} matched {len(matches)}, expected at least {min_count}")


def text_targets(vault: Path, spec: dict[str, Any], config: LlmzkConfig) -> list[Path]:
    if "path" in spec:
        target = resolve_item(vault, str(spec["path"]), config)
        return [] if ignored_benchmark_path(target) or not target.is_file() else [target]
    if "glob" in spec:
        return glob_matches(vault, str(spec["glob"]), config)
    return []


def check_required_text(result: CaseResult, vault: Path, items: list[dict[str, Any]], config: LlmzkConfig) -> None:
    for spec in items:
        targets = text_targets(vault, spec, config)
        if not targets:
            add(result, "fail", "required_text", f"no target matched: {spec}")
            continue
        for target in targets:
            if not target.exists():
                add(result, "fail", "required_text", f"missing target: {rel(target, vault)}")
                continue
            text = target.read_text(encoding="utf-8")
            for needle in spec.get("contains", []) or []:
                if str(needle) in text:
                    add(result, "pass", "required_text", f"{rel(target, vault)} contains {needle!r}")
                else:
                    add(result, "fail", "required_text", f"{rel(target, vault)} missing {needle!r}")
            any_needles = [str(n) for n in spec.get("contains_any", []) or []]
            if any_needles:
                if any(n in text for n in any_needles):
                    add(result, "pass", "required_text_any", f"{rel(target, vault)} contains one of {any_needles}")
                else:
                    add(result, "fail", "required_text_any", f"{rel(target, vault)} contains none of {any_needles}")


def check_forbidden_text(result: CaseResult, vault: Path, items: list[dict[str, Any]], config: LlmzkConfig) -> None:
    for spec in items:
        targets = text_targets(vault, spec, config)
        if not targets:
            add(result, "warn", "forbidden_text", f"no target matched: {spec}")
            continue
        for target in targets:
            if not target.exists():
                add(result, "warn", "forbidden_text", f"missing target: {rel(target, vault)}")
                continue
            text = target.read_text(encoding="utf-8")
            for needle in spec.get("contains", []) or []:
                if str(needle) in text:
                    add(result, "fail", "forbidden_text", f"{rel(target, vault)} contains forbidden text {needle!r}")
                else:
                    add(result, "pass", "forbidden_text", f"{rel(target, vault)} avoids {needle!r}")


def _wikilink_target(inner: str, config: LlmzkConfig) -> str:
    inner = inner.replace(r"\|", "|").strip()
    target = inner.split("|", 1)[0].split("#", 1)[0].strip().strip("/")
    if target.endswith(".md"):
        target = target[:-3]
    return config.to_local_target(target)


def check_required_wikilinks(result: CaseResult, vault: Path, items: list[dict[str, Any]], config: LlmzkConfig) -> None:
    for spec in items:
        target = resolve_item(vault, str(spec.get("path", "")), config)
        if not target.exists():
            add(result, "fail", "required_wikilink", f"missing target: {rel(target, vault)}")
            continue
        text = target.read_text(encoding="utf-8")
        actual_targets = {_wikilink_target(m.group(1), config) for m in WIKILINK_RE.finditer(text)}
        for link in spec.get("links", []) or []:
            link_text = str(link)
            inner = link_text[2:-2] if link_text.startswith("[[") and link_text.endswith("]]" ) else link_text
            expected_target = _wikilink_target(inner, config)
            if expected_target in actual_targets:
                add(result, "pass", "required_wikilink", f"{rel(target, vault)} has target {expected_target}")
            else:
                add(result, "fail", "required_wikilink", f"{rel(target, vault)} missing target {expected_target}")

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
            pattern = str(item.get("glob", ""))
            min_count = int(item.get("min", 1))
            matches = glob_matches(vault, pattern, config)
            if len(matches) >= min_count:
                add(result, "pass", f"artifact_{group_name}", f"{pattern} matched {len(matches)}")
            else:
                add(result, "fail", f"artifact_{group_name}", f"{pattern} matched {len(matches)}, expected at least {min_count}")
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
                    add(result, f"pass", f"artifact_{group_name}_status", f"{pattern} has status {wanted_status}")
                else:
                    add(result, f"fail", f"artifact_{group_name}_status", f"{pattern} has no artifact with status {wanted_status}")


def run_case(case_file: Path, vault: Path) -> CaseResult:
    config = load_config(vault)
    data = read_yaml(case_file)
    result = CaseResult(name=str(data.get("name") or case_file.parent.name))
    checks = data.get("checks") or {}
    if not isinstance(checks, dict):
        add(result, "fail", "schema", "checks must be a mapping")
        return result

    check_required_files(result, vault, [str(x) for x in checks.get("required_files", []) or []], config)
    check_forbidden_files(result, vault, [str(x) for x in checks.get("forbidden_files", []) or []], config)
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
