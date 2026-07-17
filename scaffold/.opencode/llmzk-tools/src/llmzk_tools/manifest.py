"""Single source of truth for scaffold-managed files and folders.

Both doctor (presence checks) and update (stale-file detection) import from
here so there is one place to edit when the scaffold's file set changes.
"""
from __future__ import annotations

ROOT_FILES = ["AGENTS.md", "opencode.json", ".gitignore"]
SYSTEM_DIRS = [".opencode", "Templates"]

REQUIRED_OPEN_CODE_DIRS = [
    ".opencode/commands",
    ".opencode/agents",
    ".opencode/skills",
    ".opencode/docs",
    ".opencode/llmzk-tools",
    ".opencode/llmzk-tools/src/llmzk_tools",
    ".opencode/bin",
]

REQUIRED_COMMANDS = [
    "llmzk-audit.md",
    "llmzk-benchmark.md",
    "llmzk-doctor.md",
    "llmzk-fix-frontmatter.md",
    "llmzk-git-commit-message.md",
    "llmzk-git-diff.md",
    "llmzk-git-preflight.md",
    "llmzk-git-revert-run.md",
    "llmzk-git-status.md",
    "llmzk-ingest.md",
    "llmzk-write-approved.md",
    "llmzk-review-validate.md",
    "llmzk-promote-candidates.md",
    "llmzk-ingest-candidates.md",
    "llmzk-normalize-links.md",
    "llmzk-promote.md",
    "llmzk-review.md",
    "llmzk-review-candidates.md",
    "llmzk-synthesize.md",
    "llmzk-update.md",
]

REQUIRED_SKILLS = [
    "llmzk-audit/SKILL.md",
    "llmzk-git-safety/SKILL.md",
    "llmzk-ingest/SKILL.md",
    "llmzk-promote/SKILL.md",
    "llmzk-synthesize/SKILL.md",
]

REQUIRED_DOCS = [
    "SOUL.md",
    "STRUCTURE.md",
    "STYLE.md",
    "SCHEMA.md",
    "LINT_RULES.md",
    "GIT_POLICY.md",
    "OBSIDIAN_SKILLS.md",
    "OPERATING_PROFILES.md",
    "BENCHMARKS.md",
    "MULTI_INSTANCE.md",
    "MAINTENANCE.md",
]

REQUIRED_TOOLS = [
    "audit.py",
    "benchmark.py",
    "config.py",
    "doctor.py",
    "fix_frontmatter.py",
    "git_safety.py",
    "new_run.py",
    "normalize_links.py",
    "review.py",
    "update.py",
]

REQUIRED_TEMPLATES = [
    "source-note.md",
    "literature-note.md",
    "permanent-note.md",
    "concept-note.md",
    "bridge-note.md",
    "contradiction-note.md",
    "index-note.md",
    "passport.md",
    "decision-log.md",
    "candidate-review.md",
]

VAULT_FOLDERS = [
    "00 Inbox",
    "00 Fleeting Notes",
    "01 Sources",
    "02 Literature Notes",
    "03 Permanent Notes",
    "04 Concept Notes",
    "05 Bridge Notes",
    "06 Contradiction Notes",
    "07 Index Notes",
    "08 Wiki Articles",
    "09 Media",
]

LOG_FOLDERS = [
    "Logs/Passports",
    "Logs/Decision Logs",
    "Logs/Candidate Reviews",
    "Logs/Review Queue",
]

NEVER_TOUCH = VAULT_FOLDERS + ["Logs"]

SCAFFOLD_MANAGED_GLOBS = [
    ".opencode/commands/llmzk-*.md",
    ".opencode/agents/zk-*.md",
    ".opencode/skills/llmzk-*/**",
    ".opencode/bin/llmzk",
    ".opencode/llmzk-tools/**",
    ".opencode/package.json",
    ".opencode/package-lock.json",
    ".opencode/README.md",
]


def scaffold_managed_paths() -> list[str]:
    """Return the full list of scaffold-managed relative paths and globs.

    Combines explicit required-file lists (prefixed with their parent directory)
    with glob patterns for convention-based matching.
    """
    paths: list[str] = []
    paths.extend(ROOT_FILES)
    paths.extend(SCAFFOLD_MANAGED_GLOBS)
    paths.extend(f".opencode/commands/{name}" for name in REQUIRED_COMMANDS)
    paths.extend(f".opencode/skills/{name}" for name in REQUIRED_SKILLS)
    paths.extend(f".opencode/docs/{name}" for name in REQUIRED_DOCS)
    paths.extend(f".opencode/llmzk-tools/src/llmzk_tools/{name}" for name in REQUIRED_TOOLS)
    paths.extend(f"Templates/{name}" for name in REQUIRED_TEMPLATES)
    return paths
