# Docs

## 指南（guides）

- [getting-started.md](guides/getting-started.md) —— 初始化 + 快速上手
- [timers.md](guides/timers.md) —— cron / launchd 定时任务接入

## 规范（rules）

规范文档按 Vault 约定统一放在 `70-System/70.07-Docs/rules/`：

- [frontmatter-spec.md](../70-System/70.07-Docs/rules/frontmatter-spec.md) —— frontmatter 必填字段、category/tags 建议、自动标签策略
- [document-routing.md](../70-System/70.07-Docs/rules/document-routing.md) —— 内容归口与目录路由规则

## 核心资产位置

| 资产 | 位置 |
| --- | --- |
| 日常脚本 | `70-System/70.03-Scripts/scripts/` |
| 定时自动化 | `70-System/70.04-Tools/automations/` |
| 配置 / cron / launchd 模板 | `70-System/70.05-Configs/templates/` |
| 工作区规则模板 | `AGENTS.example.md`（放 vault 根） |

顶层另有 [README.md](../README.md) 与 [NOTICE.md](../NOTICE.md)。