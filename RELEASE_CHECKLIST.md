# Obsidian AI Vault Scaffold — 发布前检查清单

> 参照 `oss-release-prep` 的 `references/release-checklist.md` 逐项核对。每一项都有证据；缺证据即视为未通过。

**发布红线（HARD BLOCK）**：敏感信息（API key / token / cookie / 私钥 / 个人数据 / 绝对本机路径）严禁公开。任一命中即中止发布。当前扫描**零命中**。

## A. 版本库状态

- [x] `git init` 已做，且已提交（`git log` 有提交记录）。
  - 证据：`git log` 可见首个提交。
- [x] 默认分支为 `main`。
  - 证据：`git branch` 显示 `main`。
- [x] 无未提交的敏感文件被跟踪（凭据 / `.env` / 私钥 / 构建产物）。
  - 证据：`git ls-files` 清单仅含脚手架文件；`.obsidian`、`vault.env`、`*.pem`、`*.key` 均在 `.gitignore`。

## B. 必备文件

- [x] `README.md`（英文版）存在，结构完整（徽章 + 定位 + 目录 + 快速开始 + 结构/用法 + FAQ + 路线图 + 贡献 + License + 维护者）。
- [x] `README.zh-CN.md`（中文版）存在，顶部 `<a href="./README.md">English</a>` 切换链接正确。
  - 证据：文件存在；`README.md` 顶部 `<a href="./README.zh-CN.md">中文</a>`，双向互指。
- [x] `LICENSE` 存在（MIT，版权 2026 Alan Hsu）。
- [x] `.gitignore` 排除运行产物、IDE 文件、OS 文件、密钥。
  - 证据：排除 `__pycache__/`、`.DS_Store`、`vault.env`、`.obsidian`、`71-02-wiki/*`、`71-03-output/*`、`.env`、`*.pem`、`*.key` 等。
- [x] `.gitattributes` 存在（`* text=auto eol=lf`）。——本次补全。

## C. README 质量

- [x] 结构：徽章 + 定位 + 目录 + 快速开始 + 结构/用法 + License + 维护者。
- [x] 快速开始里每个命令有依据且能跑通。
  - 证据：全部 8 个 `.py` 通过 `python3 -m py_compile`；全部 7 个 `.sh`（含 `initialize.sh`）通过 `bash -n`。
- [x] 目录树、配置项、功能描述与代码一致，无过时/虚构内容。
- [x] 双语两版结构镜像、覆盖同一组主题。

## D. 敏感信息扫描（发布红线）

- [x] 无真实 API key / token / cookie / 私钥 / 密码。
  - 证据：对 `*.md/*.yaml/*.yml/*.py/*.sh/*.json/*.plist` 跑密钥正则（`sk-…`、`ghp_…`、`xox…`、`AKIA…`、`authorization:`、`api key`、`api_key`、`secret`、`bearer …`、`BEGIN … PRIVATE KEY`）→ 一律无命中。
- [x] 无模型默认凭据 / 示例密钥 / 高熵占位疑似值。
  - 证据：`(key|token|secret|password|api)[^=]*=\s*"…"` 高熵赋值扫描无命中。
- [x] 无个人数据（真实姓名/邮箱/手机/地址/身份证）。
  - 证据：邮箱正则扫描无命中。
- [x] 无绝对本机路径（`/Users/…`、`/home/…`）。
  - 证据：绝对路径正则无命中；README 中的路径均为相对路径或 `<you>`/`/path/to/…` 占位。
- [x] `.env`、凭据文件、构建产物、日志文件不被 git 跟踪，且已在 `.gitignore`。
- [x] 示例、测试数据、README 代码块里无真实用户数据或密钥。

## E. 可验证性

- [x] 构建 / 测试命令已运行通过。
  - 证据：`py_compile`（8 个 `.py`）与 `bash -n`（7 个 `.sh`）全部退出码 0。本脚手架无独立单元测试套件；脚本以语法检查 + 非破坏性 dry-run 验证为主，已在 README 明示。
- [x] 依赖、运行环境（bash 3.2+ / python3 3.11+）、安装步骤在 README 有据可查。
- [x] 提供了校验/辅助脚本（`initialize.sh`）与运行方法、输出解读。

## F. 发布动作授权（绝不默认执行）

- [ ] `git push` / `gh repo create`：**未执行**，未获用户授权。

## G–K. 可发现性 / 主页 / Discussions / Release Assets / 发布质量门禁

- [ ] 仓库 `About` / `topics`：**未配置**，需在 GitHub 上设置（须用户授权 / 仓库已发布）。
- [ ] `index.html` 项目主页：**未生成**（可选；README 已承载完整内容，如需要再按 `oss-release-prep` H 节生成 gruvbox-material 黑金风格主页）。
- [ ] GitHub Discussions：**未启用**，需用户授权后开启。
- [ ] Release assets（`uv build` sdist/wheel）：**不适用**。本仓库是 Obsidian Vault 脚手架（无 Python 包构建入口），发布时以源码 tag + GitHub release notes 为准，可附 `initialize.sh` 校验脚本。
- [ ] 发布质量门禁（外部 reviewer 代码审查）：**未执行**。发布前建议由独立 reviewer 复核本次 README / 结构改动。

## 结论

核心发布阻断项已清零：双语 README、`.gitattributes` 已补齐；敏感信息扫描零命中；脚本全部通过语法校验；首个提交已建立（`main` 分支）。剩余 G/F 类项为外部动作或可选优化，需用户显式授权后再执行。