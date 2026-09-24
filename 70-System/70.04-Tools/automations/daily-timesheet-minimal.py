#!/usr/bin/env python3
"""Minimal daily timesheet generator.

- Scan today's git commits in this repo
- Write to 01-PERSONAL-OPS/06-TIMESHEETS/timesheet-YYYY-MM-DD.md
"""

from __future__ import annotations

import os
import subprocess
from datetime import datetime
from pathlib import Path

VAULT = Path(os.environ.get("OBSIDIAN_VAULT_DIR", str(Path.cwd())))
OUTDIR = VAULT / "10-Work" / "timesheets"


def git_log_today():
    today = datetime.now().strftime('%Y-%m-%d')
    try:
        author = subprocess.check_output(
            ["git", "config", "user.name"],
            cwd=VAULT,
            encoding="utf-8",
        ).strip()
        out = subprocess.check_output([
            "git", "log", 
            "--oneline", 
            f"--since={today} 00:00", 
            f"--until={today} 23:59",
            f"--author={author}"
        ], cwd=VAULT, encoding="utf-8")
        return out.strip()
    except subprocess.CalledProcessError:
        return ""


def main():
    today = datetime.now().strftime('%Y-%m-%d')
    out = OUTDIR / f"timesheet-{today}.md"
    log = git_log_today()

    lines = []
    lines.append('---')
    lines.append(f'title: {today} 工时记录')
    lines.append('aliases: []')
    lines.append('category: PersonalOps')
    lines.append(f'created: {today}')
    lines.append(f'updated: {today}')
    lines.append('tags: [Daily, Timesheet]')
    lines.append('---\n')
    lines.append(f'# {today} 工时记录\n')

    lines.append('## 今日 git 提交')
    if log:
        for line in log.splitlines():
            lines.append(f'- {line}')
    else:
        lines.append('- 无\n')

    lines.append('## 手动补充（可选）')
    lines.append('- [ ] 项目 A：XXX（可手动补充）\n')

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print(f'wrote {out}')


if __name__ == "__main__":
    main()
