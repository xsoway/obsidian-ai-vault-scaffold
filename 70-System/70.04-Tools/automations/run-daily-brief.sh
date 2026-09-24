#!/usr/bin/env bash
set -euo pipefail
# 每日驾驶舱生成器
# 用法: OBSIDIAN_VAULT_DIR=/path/to/vault run-daily-brief.sh
SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
VAULT_DIR="${OBSIDIAN_VAULT_DIR:-$(cd "$SELF_DIR/../../.." && pwd)}"
export OBSIDIAN_VAULT_DIR="$VAULT_DIR"
AUTODIR="$(cd "$(dirname "$0")" && pwd)"
# 解析 Python 解释器：优先 OBSIDIAN_PYTHON，否则 homebrew 3.13，否则系统 python3
if [[ -n "${OBSIDIAN_PYTHON:-}" ]]; then PY="$OBSIDIAN_PYTHON";
elif [[ -x /opt/homebrew/bin/python3.13 ]]; then PY=/opt/homebrew/bin/python3.13;
else PY=python3; fi
cd "$VAULT_DIR"
echo "=== 开始每日驾驶舱 ==="
"$PY" "$AUTODIR/daily_brief.py"
echo ""
echo "=== 每日驾驶舱完成 ==="
