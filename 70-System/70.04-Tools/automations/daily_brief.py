#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time     : 2026/05/02 10:05
# @Filename : daily_brief.py
# @Author   : Alan_Hsu
"""每日驾驶舱生成器。

输出路径：02-Notes/YYYY-MM-DD-每日驾驶舱.md
- 读取 00-Inbox/todo-backlog.md（P0/P1/P2/P3）
- 生成：Top 3 / 推进 / 等反馈 / 决策 / 委派 / 低能量 / 不做 / 提醒
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import subprocess
import os
import re

VAULT = Path(os.environ.get("OBSIDIAN_VAULT_DIR", str(Path.cwd())))
OUTDIR = VAULT / "02-Notes"
TODO_BACKLOG = VAULT / "00-Inbox" / "todo-backlog.md"


def git_log(days: int = 3):
    try:
        out = subprocess.check_output(
            ["git", "log", f"--since={days} days ago", "--oneline"],
            cwd=VAULT, encoding="utf-8"
        )
        return out.strip()
    except subprocess.CalledProcessError:
        return ""


def read_todo_backlog():
    if not TODO_BACKLOG.exists():
        return [], [], [], []
    text = TODO_BACKLOG.read_text(encoding="utf-8")
    p0, p1, p2, p3 = [], [], [], []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("- [ ] [P0]"):
            p0.append(re.sub(r"^\- \[ \] \[P0\]\s*", "", line))
        elif line.startswith("- [ ] [P1]"):
            p1.append(re.sub(r"^\- \[ \] \[P1\]\s*", "", line))
        elif line.startswith("- [ ] [P2]"):
            p2.append(re.sub(r"^\- \[ \] \[P2\]\s*", "", line))
        elif line.startswith("- [ ] [P3]"):
            p3.append(re.sub(r"^\- \[ \] \[P3\]\s*", "", line))
    return p0, p1, p2, p3


def main():
    today = datetime.now().strftime('%Y-%m-%d')
    out = OUTDIR / f"{today}-每日驾驶舱.md"

    p0, p1, p2, p3 = read_todo_backlog()

    lines = []
    lines.append('---')
    lines.append(f'title: {today} 每日驾驶舱')
    lines.append('aliases: []')
    lines.append('category: PersonalOps')
    lines.append(f'created: {today}')
    lines.append(f'updated: {today}')
    lines.append('tags: [Daily, PersonalOps]')
    lines.append('---\n')
    lines.append(f'# {today} 每日驾驶舱\n')

    lines.append('## 一、今天最重要的 3 件事')
    if p0:
        for item in p0[:3]:
            lines.append(f'- [ ] {item}')
    else:
        lines.append('- 无 P0 事项\n')

    lines.append('\n## 二、今天必须推进但不必做完')
    if p1:
        for item in p1[:5]:
            lines.append(f'- [ ] {item}')
    else:
        lines.append('- 无 P1 事项\n')

    lines.append('\n## 三、今天等待反馈 / 需要催办')
    lines.append('- （暂无，可手动添加）\n')

    lines.append('\n## 四、今天需要拍板的事')
    lines.append('- （暂无，可手动添加）\n')

    lines.append('\n## 五、今天可委派的事')
    lines.append('- （暂无，可手动添加）\n')

    lines.append('\n## 六、低能量时可做的小事')
    lines.append('- 检查 00-Inbox/ 有没有新东西')
    lines.append('- 跑一下 Wiki 增量编译（71-Wiki/71-04-scripts/wiki-compile.py）')
    lines.append('- 看看 71-Wiki/71-03-output/ 有没有新 lint 报告\n')

    lines.append('\n## 七、今天明确不做')
    lines.append('- （暂无，可手动添加）\n')

    lines.append('\n## 八、今日提醒')
    lines.append('- 每周日自动生成周复盘')
    lines.append('- Wiki 编译已由 cron 自动执行（09:15 / 18:15）\n')

    lines.append('\n## 最近 3 天 git 提交')
    log = git_log(3)
    if log:
        for line in log.splitlines():
            lines.append(f'- {line}')
    else:
        lines.append('- 无\n')

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print(f'wrote {out}')


if __name__ == "__main__":
    main()
