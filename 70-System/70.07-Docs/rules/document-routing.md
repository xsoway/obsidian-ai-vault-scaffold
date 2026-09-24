# 文档归口与目录路由规则（通用）

> 解决"文件先落下来了，但后续没人收口"的问题，确保内容进入正确目录，而不是长期停留在 `00-Inbox/`。

## 1. 路由原则

1. **先判断内容属性，再决定目录**
2. **系统配置/脚本/工作流不放 Inbox**
3. **可读成文内容优先入 Articles**
4. **内部工作笔记、流程草稿优先入 Notes**
5. **重复/过时/备份副本不留主路径**

## 2. 目录路由表

| 内容类型 | 目标目录 | 说明 |
| --- | --- | --- |
| 临时收集、待整理素材 | `00-Inbox/` | 只做短暂停留 |
| 正式文章、可读分析、可发布文档 | `01-Articles/` | 必须有正式标题 |
| 正式笔记、内部规范、方法草稿 | `02-Notes/` | 适合持续迭代 |
| 代码、脚本、项目说明 | `03-Projects/` | 代码资产与 README |
| 长期记忆 | `04-Memory/` | 稳定偏好、长期状态 |
| 系统配置/规则/工作流 | `70-System/` | 配置、文档、技能、工作流 |
| 编译知识库产物 | `71-Wiki/71-02-wiki/` | 只读，不手改 |
| 重复、低信息、备份副本 | `90-Archive/` | 不占主路径 |

## 3. 判定口径

### 3.1 Inbox → System
运行/配置文件（如 `openclaw.json`、`config.ini`）→ `70-System/70.05-Configs/`。

### 3.2 Inbox → Articles
有完整正文、能独立阅读的草稿：先补正式标题，再迁到 `01-Articles/`。

### 3.3 Notes → Archive
空白模板、低信息测试残片、bak 副本 → `90-Archive/`。

### 3.4 Templates 单独保留
通用模板放 `80-Resources/80-Templates/`，不在 `02-Notes/` 保留多份空白实例。

## 4. 命名要求

- 文章：`YYYY-MM-DD-标题.md`
- 正式笔记：`02-Notes/YYYY-MM-DD-标题.md` 或语义化标题
- 归档副本：文件名加 `归档`、`备份`、`低信息` 后缀

## 5. Frontmatter 最低要求

所有正式 Markdown 至少包含：

```yaml
---
title: 标题
aliases: []
category: 分类
created: YYYY-MM-DD HH:mm
updated: YYYY-MM-DD HH:mm
tags: [KnowledgeBase]
---
```

详见 `docs/rules/frontmatter-spec.md`。

## 6. 快速判断口诀

> 能读、能复用、能引用的进主区；
> 占位、重复、备份、残片的进归档；
> 配置、规则、工作流的一律进系统目录。

## 7. 自动化辅助

`templates/automations/inbox_auto_normalize.py` 会保守地：为 Inbox 内新文件补 frontmatter、按 `CATEGORY_MAP` 迁移到 `02-Notes/` / `01-Articles/` / `71-01-raw/`，且保留文件名的原始创建日期前缀（不会改成运行日期）。