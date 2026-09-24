# 定时任务接入指南（cron 与 launchd）

本脚手架把「日常脚本」和「定时执行」解耦：脚本是幂等的、可手动 `OBSIDIAN_VAULT_DIR=...` 触发；定时只是把脚本挂到系统调度上。

## 提供的自动化任务

| 脚本 | 作用 | 建议触发 |
| --- | --- | --- |
| `run-daily-brief.sh` → `daily_brief.py` | 每日驾驶舱：读 `00-Inbox/todo-backlog.md` 的 P0–P3，生成当日推进清单到 `02-Notes/` | 每天 09:00 |
| `inbox_auto_normalize.py` | Inbox 自动规范化：补 frontmatter、保守迁移到 Notes/Articles/Wiki-raw | 每天 09:05 |
| `brain_to_reminders.py` | 把 P0/P1 推送到 Apple Reminders（依赖 `remindctl`） | 每天 09:10（可选） |
| `run-daily-timesheet.sh` → `daily-timesheet-minimal.py` | 按当日 git 提交生成工时记录到 `10-Work/timesheets/` | 每天 18:10 |
| `run-weekly-review-only.sh` → `weekly_review_generate.py` | 周复盘：扫描本周新增 Articles 总结成一篇复盘 | 每周日 18:00 |
| `71-Wiki/71-04-scripts/…` | LLM Wiki 编译 / 体检（需对接 llm-wiki-knowledge-vault） | 每天 09:15 / 18:15，每周一体检 |

所有脚本都读取 `OBSIDIAN_VAULT_DIR`：cron / launchd 需显式传入。

## 前提

- `PYTHON=python3` 且 Python ≥ 3.11。
- 创建日志目录：`70-System/70.06-Workflows/automation-runtime/logs/`。
- `daily_brief.py` / `weekly_review_generate.py` 依赖 `git`（读取提交历史）；vault 需是 git 仓库。

## 方式 A：cron（macOS / Linux 通用）

1. 复制模板：

```bash
cp 70-System/70.05-Configs/templates/cron.template my-cron.txt
# 把 <VAULT> 替换为你的 vault 绝对路径
```

2. 装载：

```bash
crontab my-cron.txt          # 覆盖
# 或
crontab -e                   # 手动粘贴
```

3. 验证：

```bash
crontab -l
```

## 方式 B：launchd（macOS，适合需要环境变量/日志分离）

参考 `70-System/70.05-Configs/templates/launchd.example.plist`：

1. 把 `<SCRIPT_ABS_PATH>`、Label、`OBSIDIAN_VAULT_DIR`、日志路径改成你的。
2. 放入 `~/Library/LaunchAgents/` 并装载：

```bash
launchctl load ~/Library/LaunchAgents/com.example.obsidian-vault.job.plist
```

## 日志

任务各自写日志到 `70-System/70.06-Workflows/automation-runtime/logs/`：

```bash
tail -f 70-System/70.06-Workflows/automation-runtime/logs/cron-daily-brief.log
```

## 调试建议

- 任务不生效：先手动跑一次脚本看 stderr。
- 路径问题：确认 `OBSIDIAN_VAULT_DIR` 已导出。
- cron 环境较干净：`PATH` 已在模板顶部显式声明。
- 幂等验证：`inbox_auto_normalize` 有 `--dry-run` 支持（看脚本参数）；`add-frontmatter` 同理。