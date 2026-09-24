#!/usr/bin/env bash
set -euo pipefail

# Create a note via new-note.py, then append body (from file or stdin).
#
# Usage:
#   openclaw-dropin.sh --kind knowledge --title "xxx" --source "url" --body-file ./body.md
#   echo "content" | openclaw-dropin.sh --kind learning --title "yyy"

BASE="${OBSIDIAN_VAULT_DIR:-$(pwd)}"
SELF_DIR="$(cd "$(dirname "$0")" && pwd)"; NEW_NOTE="$SELF_DIR/new-note.py"

KIND=""
TITLE=""
CATEGORY=""
TAGS=""
SOURCE=""
DATE_OVERRIDE=""
NO_DATE_PREFIX=0
OPEN_NOTE=0
BODY_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --kind) KIND="$2"; shift 2;;
    --title) TITLE="$2"; shift 2;;
    --category) CATEGORY="$2"; shift 2;;
    --tags) TAGS="$2"; shift 2;;
    --source) SOURCE="$2"; shift 2;;
    --date) DATE_OVERRIDE="$2"; shift 2;;
    --no-date-prefix) NO_DATE_PREFIX=1; shift 1;;
    --open) OPEN_NOTE=1; shift 1;;
    --body-file) BODY_FILE="$2"; shift 2;;
    *) echo "Unknown arg: $1"; exit 2;;
  esac
done

if [[ -z "$KIND" || -z "$TITLE" ]]; then
  echo "Missing --kind/--title" >&2
  exit 2
fi

ARGS=("--kind" "$KIND" "--title" "$TITLE")
[[ -n "$CATEGORY" ]] && ARGS+=("--category" "$CATEGORY")
[[ -n "$TAGS" ]] && ARGS+=("--tags" "$TAGS")
[[ -n "$SOURCE" ]] && ARGS+=("--source" "$SOURCE")
[[ -n "$DATE_OVERRIDE" ]] && ARGS+=("--date" "$DATE_OVERRIDE")
[[ $NO_DATE_PREFIX -eq 1 ]] && ARGS+=("--no-date-prefix")

OUT_PATH=$("$NEW_NOTE" "${ARGS[@]}")

# Append body
if [[ -n "$BODY_FILE" ]]; then
  cat "$BODY_FILE" >> "$OUT_PATH"
else
  if [ ! -t 0 ]; then
    cat >> "$OUT_PATH"
  fi
fi



# Optionally open in Obsidian
if [[ $OPEN_NOTE -eq 1 ]]; then
  # Convert absolute path to vault-relative path
  REL=${OUT_PATH#"$BASE/"}
  obsidian-cli open --vault "\$(basename "$BASE")" --file "$REL" >/dev/null 2>&1 || true
fi

echo "$OUT_PATH"
