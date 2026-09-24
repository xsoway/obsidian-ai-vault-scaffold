#!/usr/bin/env python3
"""Create a new Obsidian markdown note with standard frontmatter + skeleton.

Design goals:
- Single entrypoint for OpenClaw-generated notes.
- Deterministic structure, safe filenames.
- Auto tags v1: path mapping + keyword weak match + KnowledgeBase.
- Does NOT overwrite existing files.

Examples:
  new-note.py --kind knowledge --title "信用利差因子研报" --source "https://..."
  new-note.py --kind learning --title "Python asyncio" --tags "AI,Python" 
  new-note.py --kind openclaw --title "OpenClaw 优化复盘" --category "OpenClaw"

"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from datetime import date

import os; VAULT = Path(os.environ.get('OBSIDIAN_VAULT_DIR', str(Path.cwd())))
ARTICLES = VAULT / '01-Articles'
PROJECTS = VAULT / '03-Projects'

KIND_TO_DIR = {
    'knowledge': ARTICLES / 'Knowledge',
    'learning': ARTICLES / 'Learning',
    'openclaw': ARTICLES / 'OpenClaw',
    'article': ARTICLES,
    'project': PROJECTS,
}

DEFAULT_CATEGORY = {
    'knowledge': '研报/归档',
    'learning': '学习笔记',
    'openclaw': 'OpenClaw',
    'article': '工程实践',
    'project': '项目文档',
}

PATH_TAGS = {
    'knowledge': ['Knowledge', 'Archive'],
    'learning': ['Learning', 'Notes'],
    'openclaw': ['OpenClaw', 'AIAgent'],
    'article': [],
    'project': ['Project', 'Engineering'],
}

KEYWORD_TAGS = [
    (re.compile(r"pruning|上下文|裁剪", re.I), ['ContextPruning']),
    (re.compile(r"QMD|检索|向量", re.I), ['QMD', 'Memory']),
    (re.compile(r"cron|定时任务", re.I), ['Cron']),
    (re.compile(r"模型|路由|分层|routing|model", re.I), ['ModelRouting']),
]


def slugify(title: str) -> str:
    s = title.strip()
    s = re.sub(r'[\\/:*?"<>|]', '-', s)
    s = re.sub(r'\s+', ' ', s)
    s = s.replace('—', '-').replace('–', '-')
    return s[:120].strip()


def uniq(seq):
    out=[]
    for x in seq:
        if x and x not in out:
            out.append(x)
    return out


def compute_tags(kind: str, body_hint: str, extra_tags: list[str]) -> list[str]:
    tags = ['KnowledgeBase']
    tags += PATH_TAGS.get(kind, [])
    for rx, ts in KEYWORD_TAGS:
        if rx.search(body_hint):
            tags += ts
    tags += extra_tags
    return uniq(tags)


def frontmatter(title: str, category: str, tags: list[str], created: str, updated: str, source_type: str|None=None, source_url: str|None=None) -> str:
    # aliases strategy A: always []
    tags_str = ', '.join(tags)
    return (
        '---\n'
        f'title: {title}\n'
        'aliases: []\n'
        f'category: {category}\n'
        f'created: {created}\n'
        f'updated: {updated}\n'
        f'tags: [{tags_str}]\n'
        '---\n\n'
    )


def skeleton(kind: str, title: str, source: str | None) -> str:
    if kind == 'knowledge':
        return (
            f'# {title}\n\n'
            '## 摘要\n\n'
            '## 关键要点\n\n'
            '## 原文/来源\n\n'
            + (f'- {source}\n\n' if source else '')
            + '## 我的判断\n'
        )
    if kind == 'learning':
        return (
            f'# {title}\n\n'
            '## 核心概念\n\n'
            '## 示例\n\n'
            '## 常见坑\n\n'
            '## 关联\n- \n'
        )
    if kind == 'openclaw':
        return (
            f'# {title}\n\n'
            '## 背景\n\n'
            '## 目标\n\n'
            '## 实施过程\n\n'
            '## 结果与验收\n\n'
            '## 风险与注意事项\n\n'
            '## 后续优化\n'
        )
    if kind == 'project':
        return (
            f'# {title}\n\n'
            '## 目标\n\n'
            '## 当前状态\n\n'
            '## 里程碑\n\n'
            '## 资料\n'
        )
    # generic
    return f'# {title}\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kind', choices=sorted(KIND_TO_DIR.keys()), required=True)
    ap.add_argument('--title', required=True)
    ap.add_argument('--category', default=None)
    ap.add_argument('--tags', default='')
    ap.add_argument('--source', default='')
    ap.add_argument('--source-type', default='')
    ap.add_argument('--date', default=None, help='YYYY-MM-DD override')
    ap.add_argument('--no-date-prefix', action='store_true')
    args = ap.parse_args()

    kind = args.kind
    title = args.title.strip()
    if not title:
        raise SystemExit('empty title')

    d = args.date or date.today().isoformat()
    category = args.category or DEFAULT_CATEGORY.get(kind, '工程实践')
    extra_tags = [t.strip() for t in args.tags.split(',') if t.strip()]
    source = args.source.strip() or None
    source_type = args.source_type.strip() or None

    # filename
    name = slugify(title)
    if kind in ('knowledge','learning','openclaw','article') and not args.no_date_prefix:
        filename = f'{d}-{name}.md'
    else:
        filename = f'{name}.md'

    outdir = KIND_TO_DIR[kind]
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / filename
    if path.exists():
        raise SystemExit(f'file exists: {path}')

    body_hint = title + '\n' + (source or '')
    tags = compute_tags(kind, body_hint, extra_tags)

    text = frontmatter(title=title, category=category, tags=tags, created=d, updated=d, source_type=source_type, source_url=(source or None))
    text += skeleton(kind, title, source)

    path.write_text(text, encoding='utf-8')
    print(str(path))

if __name__ == '__main__':
    main()
