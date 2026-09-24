#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time     : 2026/05/04 09:20
# @Filename : brain_to_reminders.py
# @Author   : Alan_HSU
"""brain-to-reminders: 把今日 P0/P1 推到 Apple Reminders.

从 00-Inbox/todo-backlog.md 提取 P0/P1 项，通过 remindctl 写入
"Brain今日" 列表，去重后逐条添加。
"""

from __future__ import annotations

import datetime
import re
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import os; VAULT_DIR = Path(os.environ.get('OBSIDIAN_VAULT_DIR', str(Path.cwd())))
LIST_NAME = "Brain今日"
TZ = "Asia/Shanghai"


def _now() -> datetime.date:
    """获取当前日期（上海时区）."""
    return datetime.datetime.now(ZoneInfo(TZ)).date()


def _run(cmd: list[str], **kwargs) -> str:
    """执行子命令并返回 stdout."""
    try:
        return subprocess.check_output(cmd, encoding="utf-8", stderr=subprocess.DEVNULL, **kwargs).strip()
    except subprocess.CalledProcessError:
        return ""


def extract_items(todo_path: Path) -> list[str]:
    """从 todo-backlog.md 提取 P0/P1 待办项."""
    if not todo_path.exists():
        print(f"WARN: {todo_path} not found")
        return []
    text = todo_path.read_text(encoding="utf-8")
    items = []
    for line in text.splitlines():
        m = re.match(r"^- \[ \] \[P[01]\]\s*(.+)$", line)
        if m:
            items.append(m.group(1).strip())
    return items[:10]


def get_existing_titles() -> set[str]:
    """获取 Reminders 列表中已有的标题，用于去重."""
    out = _run(["remindctl", "list", LIST_NAME, "--plain"])
    if not out:
        return set()
    titles: set[str] = set()
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            titles.add(parts[1])
    return titles


def main() -> None:
    date_str = _now().strftime("%Y-%m-%d")
    print(f"[{date_str}] brain-to-reminders start")

    # 检查 remindctl 是否可用
    if not _run(["which", "remindctl"]):
        print("ERROR: remindctl not installed")
        sys.exit(1)

    # 确保列表存在
    _run(["remindctl", "list", LIST_NAME, "--create"])

    # 提取待办项
    todo_path = VAULT_DIR / "00-Inbox" / "todo-backlog.md"
    items = extract_items(todo_path)

    if not items:
        print("[WARN] No items extracted")
        return

    # 去重
    existing = get_existing_titles()
    count = 0
    for item in items:
        title = f"[{date_str}] {item}"
        if item in existing or title in existing:
            print(f"[skip] already exists: {item}")
            continue
        _run(["remindctl", "add", "--title", title, "--list", LIST_NAME, "--due", f"{date_str} 21:00"])
        print(f"[add] {item}")
        count += 1

    print(f"[{date_str}] done — added {count} reminders to '{LIST_NAME}'")


if __name__ == "__main__":
    main()
