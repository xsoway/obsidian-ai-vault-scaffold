#!/usr/bin/env python3
"""Inbox auto-normalize (minimal-risk).

- Scan 00-Inbox for new/modified markdown files.
- Ensure frontmatter exists.
- Add or merge title, category, tags, created, updated.
- Move notes conservatively to 02-Notes, 01-Articles, or 71-Wiki/71-01-raw.
- 文件名前缀优先保留“原始创建日期”，而不是脚本运行日期。
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

VAULT = Path(os.environ.get("OBSIDIAN_VAULT_DIR", str(Path.cwd())))
INBOX = VAULT / "00-Inbox"
AUTOMATION_RUNTIME_DIR = VAULT / "70-System" / "70.06-Workflows" / "automation-runtime"
STATE_PATH = AUTOMATION_RUNTIME_DIR / "state.json"
LOG_DIR = AUTOMATION_RUNTIME_DIR / "logs"

CATEGORY_MAP = {
    "note": "Notes",
    "article": "Articles",
    "wiki": "Wiki",
}

FRONT_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def now_datetime() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def now_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def extract_date_prefix(text: str) -> str | None:
    match = re.match(r"^(\d{4}-\d{2}-\d{2})", text.strip())
    return match.group(1) if match else None


def normalize_tag(tag: str) -> str:
    """将 tag 规范化：去空格、去非法字符，返回合法 Obsidian tag.

    Obsidian tag 规则：不允许空格，允许字母/数字/连字符/下划线/斜杠/CJK。
    空格替换为连字符，多余连字符合并，首尾连字符去除。
    """
    tag = tag.strip()
    # 空格 → 连字符
    tag = re.sub(r"\s+", "-", tag)
    # 去除 Obsidian tag 不允许的字符（保留字母/数字/连字符/下划线/斜杠/点/CJK）
    tag = re.sub(r"[^\w\-./\u4e00-\u9fff\u3400-\u4dbf]+", "", tag)
    # 合并连续连字符
    tag = re.sub(r"-{2,}", "-", tag)
    # 首尾连字符去除
    tag = tag.strip("-")
    return tag


def safe_slug(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[\\/:*?\"<>|]", "", text)
    text = re.sub(r"-+", "-", text)
    return text[:80] if len(text) > 80 else text


def clean_title_candidate(text: str) -> str:
    """清洗候选标题，避免把 Markdown 垃圾符号和整段废话塞进文件名。"""
    text = text.strip()
    text = re.sub(r"^#{1,6}\s*", "", text)
    text = re.sub(r"^[-*+]\s+", "", text)
    text = re.sub(r"^\d+[.)]\s*", "", text)
    text = re.sub(r"^`{1,3}|`{1,3}$", "", text)
    text = re.sub(r"^\*\*(.*?)\*\*$", r"\1", text)
    text = re.sub(r"^__(.*?)__$", r"\1", text)
    text = re.sub(r"\[\[([^|\]]+)\|?[^\]]*\]\]", r"\1", text)
    text = re.sub(r"\[(.*?)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    text = text.strip("#-*_`> ：:|，,。.[]()（）")
    return text.strip()


def is_good_title_candidate(text: str) -> bool:
    if not text:
        return False
    if len(text) < 4 or len(text) > 100:
        return False
    if text.count(" ") > 20:
        return False
    bad_prefixes = (
        "你:",
        "ai:",
        "assistant:",
        "user:",
        "http://",
        "https://",
    )
    lower = text.lower()
    if lower.startswith(bad_prefixes):
        return False
    bad_exact = {
        "正文",
        "这是正文",
        "这里是正文",
        "待整理",
        "untitled",
        "temp",
    }
    if lower in bad_exact:
        return False
    return True


def parse_frontmatter(text: str):
    m = FRONT_RE.match(text)
    if not m:
        return None, text
    fm = m.group(1)
    body = text[m.end():]
    data = {}
    for line in fm.splitlines():
        if not line.strip() or line.strip().startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        data[k.strip()] = v.strip()
    return data, body


def render_frontmatter(data: dict) -> str:
    keys = ["title", "aliases", "category", "created", "updated", "tags"]
    out = ["---"]
    for k in keys:
        if k in data:
            out.append(f"{k}: {data[k]}")
    for k in sorted(set(data.keys()) - set(keys)):
        out.append(f"{k}: {data[k]}")
    out.append("---\n")
    return "\n".join(out)


@dataclass
class Decision:
    kind: str
    title: str
    tags: list[str]


def extract_keywords(text: str, max_keywords: int = 8) -> list[str]:
    keywords = set()
    lower = text.lower()
    keyword_patterns = [
        (r"openclaw", "OpenClaw"),
        (r"llm\s*wiki", "LLMWiki"),
        (r"wiki", "Wiki"),
        (r"automation|cron|launchd|定时", "Automation"),
        (r"skill", "Skill"),
        (r"agent", "Agent"),
        (r"obsidian", "Obsidian"),
        (r"git|github", "Git"),
        (r"daily|日报", "Daily"),
        (r"weekly|周报|周复盘", "Weekly"),
        (r"review|复盘", "Review"),
        (r"note|笔记", "Note"),
        (r"article|文章", "Article"),
        (r"project|项目", "Project"),
        (r"testing|测试", "Testing"),
        (r"code|代码", "Code"),
        (r"ai|人工智能", "AI"),
        (r"prompt|提示词", "Prompt"),
        (r"memory|记忆", "Memory"),
    ]
    for pattern, tag in keyword_patterns:
        if re.search(pattern, lower):
            keywords.add(tag)
    for m in re.finditer(r"\*\*([^*]+)\*\*", text):
        word = normalize_tag(m.group(1).strip())
        if 2 <= len(word) <= 30:
            keywords.add(word)
    for m in re.finditer(r"\[\[([^|\]]+)\|?[^]]*\]\]", text):
        word = normalize_tag(m.group(1).strip())
        if 2 <= len(word) <= 30:
            keywords.add(word)
    return sorted(keywords)[:max_keywords]


def extract_better_title(text: str, path: Path) -> str:
    heading_candidates = []
    for line in text.splitlines():
        if re.match(r"^#{1,6}\s+", line.strip()):
            heading_candidates.append(line)

    for line in heading_candidates:
        candidate = clean_title_candidate(line)
        if is_good_title_candidate(candidate):
            return candidate[:100]

    for line in text.splitlines():
        candidate = clean_title_candidate(line)
        if is_good_title_candidate(candidate):
            return candidate[:100]

    paragraphs = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
    if paragraphs:
        first_p = clean_title_candidate(paragraphs[0].splitlines()[0])
        for prefix in ["请帮我", "我想", "我需要", "帮我", "如何", "怎么", "什么是", "关于"]:
            if first_p.startswith(prefix):
                first_p = first_p[len(prefix):].strip()
        if is_good_title_candidate(first_p):
            return first_p[:80]

    keywords = extract_keywords(text, max_keywords=5)
    return "-".join(keywords)[:60] if keywords else path.stem


def normalize_markdown_body(text: str) -> str:
    text = re.sub(r"^(#{1,6})([^\s#])", r"\1 \2", text, flags=re.M)
    text = re.sub(r"^(\*|\-|\+)([^\s])", r"\1 \2", text, flags=re.M)
    text = re.sub(r"^(\d+\.)([^\s])", r"\1 \2", text, flags=re.M)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def decide(text: str, path: Path) -> Decision:
    title = extract_better_title(text, path)
    lower = text.lower()
    tags = extract_keywords(text, max_keywords=10)
    if len(tags) < 3:
        if any(k in lower for k in ["llm wiki", "schema", "ingest", "lint"]):
            tags.extend(["LLMWiki", "KnowledgeBase", "OpenClaw"])
        elif len(text) > 8000 or ("## " in text and text.count("##") > 8):
            tags.extend(["Article", "Draft", "KnowledgeBase"])
        else:
            tags.extend(["Note", "Inbox", "OpenClaw"])
    tags = list(dict.fromkeys(tags))
    if any(k in lower for k in ["llm wiki", "schema", "ingest", "lint"]):
        return Decision("wiki", title, tags)
    if len(text) > 8000 or ("## " in text and text.count("##") > 8):
        return Decision("article", title, tags)
    return Decision("note", title, tags)


def target_dir(kind: str) -> Path:
    if kind == "article":
        return VAULT / "01-Articles"
    if kind == "wiki":
        return VAULT / "71-Wiki" / "71-01-raw"
    return VAULT / "02-Notes"


def resolve_created_datetime(path: Path, frontmatter: dict) -> str:
    created = str(frontmatter.get("created", "")).strip()
    if created:
        return created

    date_from_name = extract_date_prefix(path.stem)
    if date_from_name:
        return f"{date_from_name} 00:00"

    stat = path.stat()
    birth_ts = getattr(stat, "st_birthtime", None)
    if birth_ts:
        return datetime.fromtimestamp(birth_ts).strftime("%Y-%m-%d %H:%M")
    return datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")


def resolve_filename_date(path: Path, created_datetime: str) -> str:
    date_from_name = extract_date_prefix(path.stem)
    if date_from_name:
        return date_from_name
    date_from_created = extract_date_prefix(created_datetime)
    if date_from_created:
        return date_from_created
    stat = path.stat()
    birth_ts = getattr(stat, "st_birthtime", None)
    if birth_ts:
        return datetime.fromtimestamp(birth_ts).strftime("%Y-%m-%d")
    return datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d")


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"files": {}}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    state = load_state()
    changed = []
    for p in INBOX.glob("*.md"):
        if p.name.startswith("."):
            continue
        mtime = int(p.stat().st_mtime)
        rec = state["files"].get(str(p), {})
        if rec.get("mtime") == mtime:
            # mtime 未变但文件仍在 Inbox → 上次处理了但 move 失败，只重试 move
            retries = rec.get("move_retries", 0)
            if retries >= 3:
                print(f"WARN: skipping {p.name} (move failed {retries} times)")
                continue
            try:
                text = p.read_text(encoding="utf-8")
                fm, body = parse_frontmatter(text)
                if fm is None:
                    fm = {}
                d = decide(body, p)
                created_datetime = resolve_created_datetime(p, fm)
                filename_date = resolve_filename_date(p, created_datetime)
                dest_dir = target_dir(d.kind)
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest = dest_dir / f"{filename_date}-{safe_slug(d.title)}.md"
                if dest.exists():
                    dest = dest_dir / p.name
                p.replace(dest)
                changed.append({"from": str(p), "to": str(dest), "kind": d.kind, "retry": True})
                print(f"MOVE-RETRY [{d.kind}] {p.name} -> {dest.relative_to(VAULT)}")
                state["files"][str(dest)] = {"mtime": int(dest.stat().st_mtime)}
                state["files"].pop(str(p), None)
            except Exception as e:
                print(f"WARN: move retry failed for {p.name}: {e}")
                state["files"][str(p)] = {"mtime": mtime, "move_retries": retries + 1}
            continue
        try:
            text = p.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(text)
            if fm is None:
                fm = {}
            d = decide(body, p)
            fm.setdefault("title", d.title)
            fm.setdefault("aliases", "[]")
            fm["category"] = CATEGORY_MAP[d.kind]
            created_datetime = resolve_created_datetime(p, fm)
            filename_date = resolve_filename_date(p, created_datetime)
            fm["created"] = created_datetime
            fm["updated"] = now_datetime()
            existing_tags = []
            tv = fm.get("tags", "[]")
            m = re.match(r"\[(.*)\]", tv.strip())
            if m and m.group(1).strip():
                existing_tags = [normalize_tag(x.strip()) for x in m.group(1).split(",") if x.strip()]
            tags = list(dict.fromkeys([*existing_tags, *d.tags, "OpenClaw"]))
            # 过滤掉规范化后为空的 tag
            tags = [t for t in tags if t]
            fm["tags"] = "[" + ", ".join(tags) + "]"
            new_text = render_frontmatter(fm) + normalize_markdown_body(body.lstrip("\n"))
            p.write_text(new_text, encoding="utf-8")
            dest_dir = target_dir(d.kind)
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / f"{filename_date}-{safe_slug(d.title)}.md"
            if dest.exists():
                dest = dest_dir / p.name
            p.replace(dest)
            changed.append({"from": str(p), "to": str(dest), "kind": d.kind})
            print(f"MOVE [{d.kind}] {p.name} -> {dest.relative_to(VAULT)}")
            state["files"][str(dest)] = {"mtime": int(dest.stat().st_mtime)}
            state["files"].pop(str(p), None)
        except Exception as e:
            print(f"ERROR: failed to process {p.name}: {e}")
            # 不更新 state，下次运行会重试
    save_state(state)
    if changed:
        log_path = LOG_DIR / f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        log_path.write_text(json.dumps(changed, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"changed {len(changed)} files; log: {log_path}")
    else:
        print(f"no changes (vault={VAULT}, inbox={INBOX})")


if __name__ == "__main__":
    main()
