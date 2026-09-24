#!/usr/bin/env bash
set -euo pipefail

# QMD Noise Guard: detect noise dirs/files inside indexed content roots.
# Policy: report only (no deletes/moves).

VAULT="${OBSIDIAN_VAULT_DIR:-$(pwd)}"
ROOTS=(
  "$VAULT/90-System/_index"
  "$VAULT/01-Articles/OpenClaw"
  "$VAULT/01-Articles/Knowledge"
  "$VAULT/01-Articles/Learning"
)

NOISE_DIRS=("_index" "bak-md" ".obsidian" "stubs""_index" "bak-md" ".obsidian")
NOISE_FILES_REGEX='(\.DS_Store$|\.swp$|\.tmp$|\.bak$|\.deleted\.|\.reset\.)'

found=0
for r in "${ROOTS[@]}"; do
  if [[ ! -d "$r" ]]; then
    echo "[skip] missing: $r"
    continue
  fi
  echo "== scan: $r =="
  for nd in "${NOISE_DIRS[@]}"; do
    while IFS= read -r p; do
      [[ -z "$p" ]] && continue
      echo "[noise-dir] $p"
      found=$((found+1))
    done < <(find "$r" -type d -name "$nd" 2>/dev/null || true)
  done

  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    echo "[noise-file] $f"
    found=$((found+1))
  done < <(find "$r" -type f | egrep -E "$NOISE_FILES_REGEX" 2>/dev/null || true)

done

echo "---"
echo "noise_hits=$found"
exit 0
