# 71-Wiki —— LLM 知识库工作台（占位）

`71-Wiki/` 是 Vault 内的 LLM 知识库子系统：从文章/笔记/原料三路收集 Markdown 源，增量编译为概念互链的 Wiki 产物。

## 目录约定

| 目录 | 作用 | 说明 |
| --- | --- | --- |
| `71-01-raw/` | Wiki 专属原料（剪藏/RSS/外部导入） | 源材料 |
| `71-02-wiki/` | 编译产出（文章页 + 概念页） | 只读，脚本生成，不手改 |
| `71-03-output/` | 运行时状态、编译报告、cron 日志 | 运行时 |
| `71-04-scripts/` | 编译/索引/lint/搜索/归档脚本 | 脚本 |

## 编译管线（各脚本职责与产出）

该系统是一段**单向管线**，每步一个独立脚本，可单独跑、也可由 cron 串联：

```text
源收集                        增量编译                    索引          体检          查询
01-Articles ─┐                                              │              │              │
02-Notes   ──┤ → wiki-compile → 文章页+概念页 → wiki-index → wiki-lint → wiki-search → wiki-archive
71-01-raw  ──┘   (写入 71-02-wiki)   (INDEX/SUMMARY)  (HEALTH-REPORT)  (全文检索)  (归档优质成果)
```

1. **`wiki-compile.py`**（编译）：从 `01-Articles/`、`02-Notes/`、`71-01-raw/` 三路收集 Markdown，增量编译（按 `mtime` 跳过未变文件），渲染**文章页 + 概念页**进 `71-02-wiki/`，落 `compile-report.json` 到 `71-03-output/`。`--full` 强制全量重编。
2. **`wiki-index.py`**（索引）：重生成 `INDEX.md`（文章 + 一句话摘要）与 `SUMMARY.md`（主题概览）。
3. **`wiki-lint.py`**（体检）：断链/缺失摘要检查 → `HEALTH-REPORT.md`，非破坏性。
4. **`wiki-search.py`**（检索）：`wiki-search.py "<关键词>" [--top N] [--json]` 朴素全文检索。
5. **`wiki-archive.py`**（归档）：把高质量问答/探索成果归档回 wiki。

## 编译脚本说明

`71-04-scripts/` 是本脚手架的**占位**。可运行的完整实现独立维护在开源仓库：

> **`llm-wiki-knowledge-vault`** —— 独立的 LLM Wiki 编译子系统（`wiki-compile.py` / `wiki-index.py` / `wiki-lint.py` / `wiki-search.py` / `wiki-archive.py`）。

**接入方式**：把该仓库的 `71-04-scripts/` 内容复制到本目录即可。其增量编译模式默认从 `01-Articles/`、`02-Notes/`、`71-01-raw/` 三路收集源资料，与本脚手架的路由规范天然一致。

## 为什么不在这里重复放一套脚本

避免双份维护。编译子系统有独立的测试、发布与版本节奏；脚手架职责是**目录规范 + 日常脚本 + 自动化**，两者解耦。

## cron 接入（参考）
```cron
# 编译 + 索引：每日 09:15 / 18:15
15 9,18 * * * cd "<VAULT>/71-Wiki" && "${OBSIDIAN_PYTHON:-/opt/homebrew/bin/python3.13}" 71-04-scripts/wiki-compile.py && "${OBSIDIAN_PYTHON:-/opt/homebrew/bin/python3.13}" 71-04-scripts/wiki-index.py >> 71-03-output/cron.log 2>&1

# 每周体检：周一 09:20
20 9 * * 1 cd "<VAULT>/71-Wiki" && "${OBSIDIAN_PYTHON:-/opt/homebrew/bin/python3.13}" 71-04-scripts/wiki-lint.py >> 71-03-output/cron-lint.log 2>&1
```
