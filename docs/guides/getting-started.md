# 快速上手

## 1. 初始化一个新的 Vault

```bash
git clone https://github.com/<you>/obsidian-ai-vault-scaffold.git
cd obsidian-ai-vault-scaffold
./initialize.sh /path/to/your-new-vault
```

`initialize.sh` 会在目标目录创建：

- 标准分区目录（00-Inbox … 99-Attachments）
- `70-System/*` 系统层结构与 `71-Wiki/*` 子目录
- 日常脚本 → `70-System/70.03-Scripts/scripts/`
- 自动化脚本 → `70-System/70.04-Tools/automations/`
- 规范文档 → `70-System/70.07-Docs/rules/`
- 生成 `70-System/70.05-Configs/vault.env`

## 2. 用 Obsidian 打开

把目标目录作为 Obsidian vault 打开。可选的 `.obsidian/` 配置由你自己管理。

## 3. 配置 vault.env

```bash
vim /path/to/your-new-vault/70-System/70.05-Configs/vault.env
```

至少确认 `OBSIDIAN_VAULT_DIR` 指向 vault 根目录。

## 4. 建第一条笔记

```bash
export OBSIDIAN_VAULT_DIR=/path/to/your-new-vault
python3 /path/to/your-new-vault/70-System/70.03-Scripts/scripts/new-note.py \
  --kind learning --title "Python asyncio" --tags "AI,Python"
```

会生成 `01-Articles/Learning/YYYY-MM-DD-Python-asyncio.md`，带规范 frontmatter 与骨架。

## 5. 接入定时任务（可选）

见 [docs/guides/timers.md](timers.md)：cron 模板 `70-System/70.05-Configs/templates/cron.template`、launchd 模板 `70-System/70.05-Configs/templates/launchd.example.plist`。

## 6. 接入 LLM Wiki（可选）

见 [71-Wiki/README.md](../../71-Wiki/README.md)：对接 `llm-wiki-knowledge-vault` 编译子系统。

---

## 手动使用（不跑 initialize.sh 时）

直接以本仓库为 vault，所有脚本就在 `70-System/` 规范位置：

| 脚本 | 路径 |
| --- | --- |
| 新建笔记 | `70-System/70.03-Scripts/scripts/new-note.py` |
| 补 frontmatter | `70-System/70.03-Scripts/scripts/add-frontmatter.py` |
| HTML → MD | `70-System/70.03-Scripts/scripts/html-to-md.py` |
| 收藏 URL | `70-System/70.03-Scripts/scripts/archive-url.sh` |
| 生成笔记(via new-note) | `70-System/70.03-Scripts/scripts/openclaw-dropin.sh` |
| 巡检噪音文件 | `70-System/70.03-Scripts/scripts/qmd-noise-guard.sh` |
| 每日驾驶舱 | `70-System/70.04-Tools/automations/run-daily-brief.sh` |
| Inbox 规范化 | `70-System/70.04-Tools/automations/inbox_auto_normalize.py` |
| 每日工时 | `70-System/70.04-Tools/automations/run-daily-timesheet.sh` |
| 周复盘 | `70-System/70.04-Tools/automations/run-weekly-review-only.sh` |
| P0/P1→提醒 | `70-System/70.04-Tools/automations/brain_to_reminders.py` |

## 环境变量

| 变量 | 用途 | 默认 |
| --- | --- | --- |
| `OBSIDIAN_VAULT_DIR` | vault 根目录绝对路径 | 当前工作目录 |
| `PYTHON` | Python 运行时（3.11+） | `python3` |