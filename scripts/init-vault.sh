#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: ./scripts/init-vault.sh <vault-path> [options]

Create an installed llmzk OpenCode/Obsidian vault from this source checkout.

Options:
  --mode copy|symlink   Install .opencode and Templates by copy or symlink. Default: copy
  --git                 Initialize a Git repository in the vault. Default
  --no-git              Do not initialize Git
  --commit              Create an initial scaffold commit after git init
  --doctor              Run llmzk doctor after install. Default
  --no-doctor           Skip llmzk doctor
  --force               Allow installing into a non-empty vault and overwrite installed system paths
  -h, --help            Show this help

Examples:
  ./scripts/init-vault.sh ~/Vaults/MyResearchVault --mode copy --git --commit
  ./scripts/init-vault.sh ~/Vaults/MyResearchVault --mode symlink --git
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
MODE="copy"
DO_GIT=1
DO_COMMIT=0
DO_DOCTOR=1
FORCE=0

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
    --git)
      DO_GIT=1
      shift
      ;;
    --no-git)
      DO_GIT=0
      shift
      ;;
    --commit)
      DO_COMMIT=1
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
    --force)
      FORCE=1
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

if [[ "$MODE" != "copy" && "$MODE" != "symlink" ]]; then
  echo "--mode must be 'copy' or 'symlink'" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SCAFFOLD="$REPO_ROOT/scaffold"
VAULT="$(python3 -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).expanduser().resolve())' "$VAULT_PATH")"

if [[ ! -d "$SCAFFOLD" ]]; then
  echo "Could not find scaffold directory: $SCAFFOLD" >&2
  exit 1
fi

if [[ -e "$VAULT" && -n "$(find "$VAULT" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null || true)" && "$FORCE" -ne 1 ]]; then
  echo "Vault path is not empty: $VAULT" >&2
  echo "Use --force to install into an existing folder." >&2
  exit 1
fi

mkdir -p "$VAULT"

echo "llmzk source: $REPO_ROOT"
echo "Vault: $VAULT"
echo "Install mode: $MODE"

copy_file() {
  local src="$1"
  local dst="$2"
  if [[ -e "$dst" || -L "$dst" ]]; then
    if [[ "$FORCE" -ne 1 ]]; then
      echo "Refusing to overwrite existing file: $dst" >&2
      exit 1
    fi
    rm -f "$dst"
  fi
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
}

install_dir() {
  local src="$1"
  local dst="$2"
  if [[ -e "$dst" || -L "$dst" ]]; then
    if [[ "$FORCE" -ne 1 ]]; then
      echo "Refusing to overwrite existing path: $dst" >&2
      exit 1
    fi
    rm -rf "$dst"
  fi
  if [[ "$MODE" == "copy" ]]; then
    cp -R "$src" "$dst"
  else
    ln -s "$src" "$dst"
  fi
}

ensure_gitkeep() {
  local dir="$1"
  mkdir -p "$dir"
  touch "$dir/.gitkeep"
}

for name in AGENTS.md opencode.json .gitignore; do
  copy_file "$SCAFFOLD/$name" "$VAULT/$name"
done

install_dir "$SCAFFOLD/.opencode" "$VAULT/.opencode"
install_dir "$SCAFFOLD/Templates" "$VAULT/Templates"

VAULT_FOLDERS=(
  "00 Inbox"
  "00 Fleeting Notes"
  "01 Sources"
  "02 Literature Notes"
  "03 Permanent Notes"
  "04 Concept Notes"
  "05 Bridge Notes"
  "06 Contradiction Notes"
  "07 Index Notes"
  "08 Wiki Articles"
  "09 Media"
)

LOG_FOLDERS=(
  "Logs/Passports"
  "Logs/Decision Logs"
  "Logs/Candidate Reviews"
  "Logs/Review Queue"
)

for name in "${VAULT_FOLDERS[@]}"; do
  ensure_gitkeep "$VAULT/$name"
done
for name in "${LOG_FOLDERS[@]}"; do
  ensure_gitkeep "$VAULT/$name"
done

if [[ "$DO_GIT" -eq 1 ]]; then
  if [[ ! -d "$VAULT/.git" ]]; then
    git -C "$VAULT" init >/dev/null
    echo "Git: initialized repository"
  else
    echo "Git: existing repository detected"
  fi
  if [[ "$DO_COMMIT" -eq 1 ]]; then
    git -C "$VAULT" add AGENTS.md opencode.json .gitignore .opencode Templates \
      "00 Inbox" "00 Fleeting Notes" "01 Sources" "02 Literature Notes" \
      "03 Permanent Notes" "04 Concept Notes" "05 Bridge Notes" \
      "06 Contradiction Notes" "07 Index Notes" "08 Wiki Articles" "09 Media" Logs
    if git -C "$VAULT" diff --cached --quiet; then
      echo "Git: no scaffold changes to commit"
    else
      if git -C "$VAULT" commit -m "llmzk: initialize vault scaffold" >/dev/null; then
        echo "Git: created initial commit"
      else
        echo "Git: initial commit failed. This is often because user.name/user.email is not configured." >&2
      fi
    fi
  fi
fi

if [[ "$DO_DOCTOR" -eq 1 ]]; then
  echo
  echo "Running llmzk doctor..."
  if ! "$VAULT/.opencode/bin/llmzk" doctor "$VAULT" --quiet-ok; then
    echo "Doctor reported issues. Review the messages above before using the vault." >&2
  fi
fi

cat <<NEXT

Created llmzk vault scaffold.
Next:
  cd $VAULT
NEXT
if [[ "$DO_GIT" -eq 1 && "$DO_COMMIT" -eq 0 ]]; then
  echo '  git add . && git commit -m "llmzk: initialize vault scaffold"'
fi
cat <<NEXT
  opencode
  /llmzk-doctor
  /llmzk-git-status
  /llmzk-ingest 00 Inbox/<source>.md
  # Review the candidate file, then run /llmzk-write-approved Logs/Candidate Reviews/<file>.md
NEXT
