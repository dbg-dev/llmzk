#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: ./scripts/update-vault.sh <vault-path> [options]

Update an existing installed llmzk vault from this source checkout.
Only system paths are updated: AGENTS.md, opencode.json, .gitignore,
.opencode/, Templates/, and .llmzk.yaml metadata. Durable notes and Logs are not touched.

Options:
  --mode copy|symlink   Update .opencode and Templates by copy or symlink. Default: existing install_mode or copy
  --apply               Apply the update. Without this, report planned changes only
  --allow-dirty         Allow applying when the vault Git tree is dirty
  --doctor              Run llmzk doctor after applying. Default
  --no-doctor           Skip doctor after applying
  -h, --help            Show this help

Examples:
  ./scripts/update-vault.sh ~/Vaults/AI
  ./scripts/update-vault.sh ~/Vaults/AI --apply
  ./scripts/update-vault.sh ~/Vaults/AI --mode symlink --apply
USAGE
}

if [[ $# -eq 0 ]]; then
  usage
  exit 1
fi

case "${1:-}" in
  -h|--help)
    usage
    exit 0
    ;;
esac

VAULT_PATH="$1"
shift
MODE="auto"
APPLY=0
ALLOW_DIRTY=0
DO_DOCTOR=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="${2:-}"
      shift 2
      ;;
    --mode=*)
      MODE="${1#*=}"
      shift
      ;;
    --apply)
      APPLY=1
      shift
      ;;
    --allow-dirty)
      ALLOW_DIRTY=1
      shift
      ;;
    --doctor)
      DO_DOCTOR=1
      shift
      ;;
    --no-doctor)
      DO_DOCTOR=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VAULT="$(python3 -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).expanduser().resolve())' "$VAULT_PATH")"

if [[ ! -x "$VAULT/.opencode/bin/llmzk" ]]; then
  echo "Installed vault wrapper not found: $VAULT/.opencode/bin/llmzk" >&2
  echo "For very old installs, rerun init-vault.sh with --force after backing up." >&2
  exit 1
fi

ARGS=(update "$VAULT" --source "$REPO_ROOT" --mode "$MODE")
if [[ "$APPLY" -eq 1 ]]; then
  ARGS+=(--apply)
fi
if [[ "$ALLOW_DIRTY" -eq 1 ]]; then
  ARGS+=(--allow-dirty)
fi

"$VAULT/.opencode/bin/llmzk" "${ARGS[@]}"

if [[ "$APPLY" -eq 1 && "$DO_DOCTOR" -eq 1 ]]; then
  echo
  echo "Running llmzk doctor after update..."
  "$VAULT/.opencode/bin/llmzk" doctor "$VAULT"
fi
