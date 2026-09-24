# Frontmatter 规范（通用 Vault 模板）

> 目标：所有落盘到 Vault 的 Markdown 文档，统一具备可检索、可聚类、可做知识图谱的元数据。
> 本规范是脚手架默认约定，可按团队或个人主题调整 `category` 与 `tags` 建议值。

## 必填字段

```yaml
---
title: 标题
aliases: []
category: 分类
created: YYYY-MM-DD HH:mm
updated: YYYY-MM-DD HH:mm
tags: []
published: true
---
```

## 字段含义

- `title`：文档主标题（与一级标题一致或更短）
- `aliases`：别名列表（默认空数组，不自动生成）
- `category`：单值分类（用于聚类、导航）
- `created/updated`：创建/更新时间（`YYYY-MM-DD HH:mm`）
- `tags`：多标签（用于知识图谱、交叉检索）

## category 建议值（示例）

- 核心概念
- 工程实践
- 学习笔记
- 复盘总结
- 项目文档
- 研报/归档

## tags 建议（最小集）

- `KnowledgeBase`（所有文档默认加）
- 主题标签：如 `AIAgent` `Cron` `ModelRouting`
- 方法标签：如 `EngineeringPractice` `Workflow`

## 自动标签策略 v1（轻量规则）

优先级：路径映射 > 关键词弱匹配 > 保底。

### 路由依赖的路径映射（与 `new-note.py` 的 KIND_TO_DIR 对应）

| kind | 目标目录 | 自动标签 |
| --- | --- | --- |
| `knowledge` | `01-Articles/Knowledge` | `Knowledge` `Archive` |
| `learning` | `01-Articles/Learning` | `Learning` `Notes` |
| `article` | `01-Articles` | — |
| `project` | `03-Projects` | `Project` `Engineering` |

### 关键词弱匹配（命中才加）

| 关键词 | 标签 |
| --- | --- |
| pruning/上下文/裁剪 | `ContextPruning` |
| QMD/检索/向量 | `QMD` `Memory` |
| cron/定时任务 | `Cron` |
| 模型/路由/分层/routing/model | `ModelRouting` |

### 保底

- 始终加：`KnowledgeBase`

## 工具支持

- 新笔记：`templates/scripts/new-note.py`（按 kind 自动生成 frontmatter + 骨架）
- 补 frontmatter：`templates/scripts/add-frontmatter.py`（扫描既有无 frontmatter 文件）