#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Obsidian AI Vault Scaffold — 一键初始化
# 用本仓库作为模板，生成一个独立可用的 Obsidian Vault。
#
# 用法:
#   ./initialize.sh /path/to/new-vault
#
# 说明:
#   - 复制标准分区目录、70-System 系统层（脚本/自动化/配置/规范）
#   - 生成 vault.env 配置
#   - 排除本仓库的 .git 与运行时产物
#   - 不会覆盖已存在/非空文件
#
# 依赖: bash 3.2+, rsync, python3 (3.11+)
# ============================================================

SCAFFOLD_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="${1:-}"

if [[ -z "$TARGET" ]]; then
  echo "用法: $0 /path/to/new-vault" >&2
  exit 2
fi

if [[ -e "$TARGET" && -n "$(ls -A "$TARGET" 2>/dev/null)" ]]; then
  echo "错误: 目标目录 '$TARGET' 已存在且非空（避免覆盖）。" >&2
  exit 2
fi

echo "==> 从脚手架复制到: $TARGET"

# 复制全部骨架（排除 git 与运行时产物、日志）
rsync -a \
  --exclude='.git/' \
  --exclude='*.pyc' \
  --exclude='__pycache__/' \
  --exclude='.DS_Store' \
  --exclude='*.log' \
  "$SCAFFOLD_DIR/" "$TARGET/"

# 生成 vault.env（从模板复制并写入实际路径）
CONFIG_DIR="$TARGET/70-System/70.05-Configs"
cp "$CONFIG_DIR/templates/vault.env.example" "$CONFIG_DIR/vault.env"
sed -i '' "s|OBSIDIAN_VAULT_DIR=.*|OBSIDIAN_VAULT_DIR=${TARGET}|" "$CONFIG_DIR/vault.env"

# 脚本可执行位
chmod +x "$TARGET"/70-System/70.03-Scripts/scripts/*.sh 2>/dev/null || true
chmod +x "$TARGET"/70-System/70.04-Tools/automations/*.sh 2>/dev/null || true

echo ""
echo "==> 完成。Vault 骨架已生成:"
echo "    $TARGET"
echo ""
echo "下一步:"
echo "  1) 用 Obsidian 打开 $TARGET 作为 vault"
echo "  2) 编辑 $CONFIG_DIR/vault.env 填写个人配置"
echo "  3) 试建笔记:"
echo "     OBSIDIAN_VAULT_DIR=$TARGET python3 $TARGET/70-System/70.03-Scripts/scripts/new-note.py --kind learning --title '我的第一条笔记'"
echo "  4) 接入定时任务: 见 docs/guides/timers.md 或复制 70-System/70.05-Configs/templates/cron.template"
echo ""