# AGENTS.example.md —— Vault 规则示例

> 复制到你的 vault 根目录并重命名为 `AGENTS.md`，按团队/个人情况增删。
> 这是脚手架规范的核心入口；与 `docs/rules/` 里的规范配套。

---

# AGENTS.md - 工作区规则（Vault 模板）

> 这个 Vault 是你的长期知识库与记忆库。所有"可复用"的内容都应该最终落盘到这里。

## 文件分区（强约束）

- `00-Inbox/`：临时收集（链接、截图、草稿、daily 待整理材料）
- `01-Articles/`：正式文章与可读文档
- `02-Notes/`：正式笔记主区
- `03-Projects/`：代码/脚本/项目（可执行资产 + README）
- `04-Memory/`：正式长期记忆（主题记忆、偏好、项目长期状态）
- `30-Tasks/`：计划与待办（日计划、周计划、任务清单）
- `40-Review/`：复盘与总结（周、月、年度、项目复盘）
- `70-System/`：系统层（Skills、Scripts、Tools、Configs、Workflows、Docs）
- `71-Wiki/`：LLM 知识库工作台（`71-01-raw/` 原料、`71-02-wiki/` 编译产出、`71-03-output/` 状态、`71-04-scripts/` 脚本）
- `80-Resources/`：资源与模板区
- `90-Archive/`：历史归档
- `91-Bases/`：数据库/基础数据
- `99-Attachments/`：附件（PDF/图片等）

## 落盘规范（必须）

### Frontmatter

所有 Markdown 文档顶部必须包含 frontmatter（用于知识图谱/检索/聚类）：

```yaml
---
title: 标题
aliases: []
category: 分类
created: YYYY-MM-DD HH:mm
updated: YYYY-MM-DD HH:mm
tags: [KnowledgeBase, ...]
published: true
---
```

### 统一生成器

优先使用生成器创建新笔记（保证一致性）：

```bash
OBSIDIAN_VAULT_DIR=<vault>
python3 70-System/70.03-Scripts/scripts/new-note.py --kind <kind> --title "<标题>"
```

### 命名约定

- 文章：`01-Articles/YYYY-MM-DD-标题.md`
- 复盘：`40-Review/.../YYYY-MM-DD-标题.md`
- 正式笔记：`02-Notes/YYYY-MM-DD-标题.md`
- 项目说明：`03-Projects/<ProjectName>/README.md`

## Python 开发规范（MUST / SHOULD / MAY）

### 注释

- **MUST**：关键业务逻辑、边界条件、异常分支写中文注释
- **MUST**：公共函数/类有 docstring（中文），说明入参、返回、异常、副作用
- **MUST NOT**：无意义注释（翻译式注释）

### 日志

- **MUST**：使用 logging，禁止 print 作为正式日志
- **MUST**：异常日志带堆栈（`exc_info=True`）
- **MUST NOT**：记录敏感信息（token、密码、cookie）
- **SHOULD**：级别约定为 DEBUG / INFO / WARNING / ERROR / CRITICAL

### 结构

- **MUST**：禁止单文件塞全部逻辑；分层：interface → service → domain → repository → common
- **SHOULD**：单函数 ≤ 80 行；控制嵌套（≤3 层），优先早返回

### 测试

- **MUST**：统一 pytest；bug 修复补回归测试
- **MUST**：TDD 遵循 Red → Green → Refactor

### 环境与配置

- **MUST**：配置放 `config.ini`/`yaml` 或环境变量，禁止硬编码；敏感配置走环境变量
- **MUST**：Python 用 `uv` 管理虚拟环境与依赖
- **MUST NOT**：用"注释掉旧代码"代替版本管理；不硬编码密钥

## 知识库问答引用规则（若回答"基于笔记/知识库"类问题）

- 必须引用具体笔记路径（Obsidian 可点开的相对路径优先）
- 推荐格式：`[[01-Articles/.../文件名|显示名]]` 或直接给 `01-Articles/.../文件名.md`
- Wiki 编译产出在 `71-02-wiki/`（只读），不要手动编辑；改源文件后跑编译

## 自动化原则

- 自动化默认"非破坏性"：巡检只报告，不自动移动/删除
- 涉及固定业务流程：优先用"脚本 / hook / 可验收输出"，不只靠自由发挥的提示词
- `00-Inbox/` 是临时入口，不应长期堆积正式内容；daily/草稿按规则迁移到 `02-Notes/`、`01-Articles/`

<!--
  按需增补：
  - 你的 Agent 触发/路由规则（例如"以某个关键词开头的内容转交给特定 agent"）
  - 团队特定规范（分支策略、发布流程、code review）
  - 安全红线（敏感目录、禁止提交内容）
-->