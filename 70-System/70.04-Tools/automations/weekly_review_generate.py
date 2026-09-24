#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time     : 2026/09/14 10:54
# @Filename : weekly_review_generate.py
# @Author   : Alan_Hsu

"""生成周复盘（保存到 01-Articles）。

扫描 01-Articles 本周内新增的文章，读取正文，总结整理成本周文章的复盘总结。
按工作区 AGENTS.md 规范输出唯一一份复盘文章，保存到 01-Articles/YYYY-MM-DD-周复盘.md。
"""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from datetime import datetime, timedelta
import os
from pathlib import Path

# ---- 配置（集中常量，避免散落硬编码，遵循 AGENTS.md 配置规范） ----
VAULT = Path(os.environ.get("OBSIDIAN_VAULT_DIR", str(Path.cwd())))
ARTICLE_DIR = VAULT / "01-Articles"
DEFAULT_DAYS = 7

NOW = datetime.now()
TS = NOW.strftime("%Y-%m-%d %H:%M")
TODAY = NOW.strftime("%Y-%m-%d")

# 文件名日期前缀：article 命名遵守 01-Articles/YYYY-MM-DD-标题.md
_FN_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-")

# frontmatter 分类/标签（遵循 AGENTS.md frontmatter-spec）
CATEGORY = "WeeklyReview"
TAGS = ["KnowledgeBase", "WeeklyReview", "Review", "OpenClaw", "Articles"]


# ---- 日志（遵循 AGENTS.md 日志规范） ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s:%(lineno)d %(message)s",
)
logger = logging.getLogger("weekly_review_generate")


class ArticleStats:
    """单篇本周新增文章的基础元信息。"""

    __slots__ = ("rel_path", "date", "title", "words", "head")

    def __init__(self, rel_path: Path, date: str, title: str, words: int, head: str):
        self.rel_path = str(rel_path)
        self.date = date
        self.title = title
        self.words = words
        self.head = head

    def wikilink(self) -> str:
        return f"[[{self.rel_path}|{self.title}]]"


def compute_window(days: int = DEFAULT_DAYS) -> tuple[datetime, datetime]:
    """返回复盘统计窗口 [start, NOW)，start 为 days 天前的零点。"""
    end = NOW
    start = (NOW - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return start, end


def parse_file_date(filename: str) -> str | None:
    """从文件名 `YYYY-MM-DD-标题.md` 解析日期；命名不规范返回 None。"""
    m = _FN_DATE_RE.match(filename)
    if not m:
        return None
    return m.group(1)


def _strip_frontmatter(text: str) -> str:
    """去掉文档头部的 YAML frontmatter（--- 包裹），返回正文。"""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return text


def _extract_title(text: str) -> str:
    """优先取 frontmatter 的 title，其次取第一个 # 标题，否则文件名。"""
    m = re.search(r"^title:\s*(.+)$", text, flags=re.MULTILINE)
    if m:
        return m.group(1).strip().strip('"')
    h = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
    if h:
        return h.group(1).strip()
    return ""


def recent_articles(days: int = DEFAULT_DAYS) -> list[ArticleStats]:
    """扫描 01-Articles 本周(按文件名日期)新增文章，返回按日期倒序的列表。"""
    start, _ = compute_window(days)
    start_day = start.strftime("%Y-%m-%d")
    end_day = NOW.strftime("%Y-%m-%d")

    stats: list[ArticleStats] = []
    if not ARTICLE_DIR.exists():
        logger.warning("01-Articles 目录不存在: %s", ARTICLE_DIR)
        return stats

    for p in sorted(ARTICLE_DIR.glob("*.md")):
        fdate = parse_file_date(p.name)
        # 按文件名日期判断是否属于本周；命名不规范的文件不纳入（避免误统计批量 touch 的历史文件）
        if not fdate:
            logger.debug("跳过命名不规范的 article: %s", p.name)
            continue
        if not (start_day <= fdate <= end_day):
            continue
        try:
            raw = p.read_text(encoding="utf-8", errors="ignore")
        except OSError as e:
            logger.warning("读取失败 %s: %s", p.name, e)
            continue
        body = _strip_frontmatter(raw)
        title = _extract_title(raw) or Path(p.stem).name
        words = len(re.findall(r"\S+", body))
        head = " ".join(body.split())[:200]
        stats.append(ArticleStats(p.relative_to(VAULT), fdate, title, words, head))

    stats.sort(key=lambda s: s.date, reverse=True)
    return stats


def build_review(articles: list[ArticleStats], days: int = DEFAULT_DAYS) -> str:
    """基于本周新增文章生成复盘正文（含 frontmatter）。"""
    start, end = compute_window(days)

    total_words = sum(a.words for a in articles)
    # 按发布日期归组，便于按天/按主题排列
    by_date: dict[str, list[ArticleStats]] = defaultdict(list)
    for a in articles:
        by_date[a.date].append(a)

    lines: list[str] = [
        "---",
        f"title: {TODAY}-周复盘：本周 {len(articles)} 篇文章的沉淀与复盘",
        "aliases: [本周复盘, Weekly Review]",
        f"category: {CATEGORY}",
        f"created: {TS}",
        f"updated: {TS}",
        f"tags: {_fmt_tags(TAGS)}",
        "published: true",
        "---",
        "",
        f"# {TODAY} 周复盘（{start.strftime('%Y-%m-%d')} → {end.strftime('%Y-%m-%d')}）",
        "",
        "## 1. 统计窗口",
        "",
        f"- 时间范围：`{start.strftime('%Y-%m-%d')}` 到 `{end.strftime('%Y-%m-%d')}`",
        f"- 统计口径：按文件名日期落在本周窗口内的 `01-Articles/` 文章（共 **{len(articles)}** 篇，合计约 **{total_words:,}** 字）",
        "",
        "## 2. 本周一句话总结",
        "",
        f"- 本周共沉淀 **{len(articles)}** 篇文章，聚焦「{_pick_focus(articles)}」这组主线。",
        "",
        "## 3. 本周新增文章清单",
        "",
    ]

    if articles:
        lines.append("| 日期 | 标题 | 字数 |")
        lines.append("|---|---|---:|")
        for a in articles:
            lines.append(f"| {a.date} | {a.wikilink()} | {a.words:,} |")
    else:
        lines.append("（本周 `01-Articles/` 无新增文章）")

    lines += ["", "## 4. 本周主题复盘", ""]
    lines += _topic_review(articles)

    lines += ["", "## 5. 本周观察", ""]
    lines += [
        "- 文章即资产：`01-Articles/` 同时作为 `71-Wiki` 源①，沉淀后会被编译进知识库，形成可检索闭环。",
        "- 写作主线：注意保持「能落地、能复用、能验收」的取舍，避免只罗列工具资讯。",
    ]

    lines += ["", "## 6. 下周建议", ""]
    lines += [
        "- 继续把每周折腾收敛成可复用文章，回填 `01-Articles/`。",
        "- 对长期未更新的主题，考虑合并或归档，保持目录干净。",
    ]
    return "\n".join(lines)


def _fmt_tags(tags: list[str]) -> str:
    """把 tag 列表格式化为 YAML inline list。"""
    return "[" + ", ".join(tags) + "]"


def _pick_focus(articles: list[ArticleStats]) -> str:
    """根据本周文章标题共性粗判一条主线（仅供一句话总结留白，可人工修正）。"""
    if not articles:
        return "待定"
    cats: dict[str, int] = defaultdict(int)
    for a in articles:
        head = (a.title + " " + a.head).lower()
        for kw, label in (
            ("agent", "Agent/自动化"),
            ("openclaw", "OpenClaw"),
            ("wiki", "知识库"),
            ("测试", "测试"),
            ("ai", "AI 应用"),
            ("复盘", "复盘方法论"),
        ):
            if kw in head:
                cats[label] += 1
    if not cats:
        return "待补"
    return max(cats.items(), key=lambda kv: kv[1])[0]


def _topic_review(articles: list[ArticleStats]) -> list[str]:
    """把本周文章按主题聚类，产出简要复盘要点。"""
    if not articles:
        return ["- 本周无新增文章，无需复盘。"]

    out: list[str] = []
    buckets: list[tuple[str, list[ArticleStats]]] = []

    def _bucket(label: str, items: list[ArticleStats]) -> None:
        if items:
            buckets.append((label, items))

    ai_agent = [a for a in articles if any(k in (a.title + a.head).lower() for k in ("agent", "openclaw", "automation"))]
    knowledge = [a for a in articles if any(k in (a.title + a.head).lower() for k in ("wiki", "知识库", "笔记"))]
    testing = [a for a in articles if any(k in (a.title + a.head).lower() for k in ("测试", "appium", "cua"))]
    others = [a for a in articles if a not in ai_agent and a not in knowledge and a not in testing]

    _bucket("Agent / 自动化", ai_agent)
    _bucket("知识库 / 笔记", knowledge)
    _bucket("测试工程", testing)
    _bucket("其他", others)

    for label, items in buckets:
        out.append(f"### {label}（{len(items)} 篇）")
        out.append("")
        for a in items[:6]:
            out.append(f"- **《{a.title}》**（{a.date}，{a.words:,} 字）：{a.head or '（无摘要）'}")
        out.append("")

    out += [
        "#### 复盘要点",
        "",
        "- **共同点**：本周文章整体围绕「把工具/流程收敛成可复用资产」。",
        "- **启发**：沉淀优先级应从「信息收集」转向「可执行、可验收、可检索」。",
        "- **下一步**：挑 1-2 篇最有复用价值的主题深化成技能/模板。",
    ]
    return out


def main(days: int = DEFAULT_DAYS) -> None:
    """入口：扫描本周文章 → 生成复盘 → 保存到 01-Articles。"""
    article_dir = Path(ARTICLE_DIR)
    article_dir.mkdir(parents=True, exist_ok=True)

    articles = recent_articles(days)
    if not articles:
        logger.warning("本周（%d 天）01-Articles 无新增文章，仍生成空复盘占位。", days)

    out = article_dir / f"{TODAY}-周复盘.md"
    out.write_text(build_review(articles, days) + "\n", encoding="utf-8")
    logger.info("已生成周复盘: %s（%d 篇）", out, len(articles))
    print(f"wrote {out}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="生成基于 01-Articles 本周新增文章的周复盘")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="统计窗口天数，默认 7")
    args = parser.parse_args()
    main(args.days)
