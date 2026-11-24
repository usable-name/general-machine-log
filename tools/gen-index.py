# -*- coding: utf-8 -*-
"""从 log/*.md 自动生成索引表，插入 OUTLINE.md 的标记区块。

用法：
    python tools/gen-index.py

原理：只替换 <!-- INDEX:BEGIN --> 和 <!-- INDEX:END --> 之间的内容，
不动其它任何部分（借鉴 Backlog.md 的 SECTION 标记做法）。
"""
import io
import os
import re
import sys
import glob

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTLINE = os.path.join(BASE, "OUTLINE.md")
BEGIN = "<!-- INDEX:BEGIN -->"
END = "<!-- INDEX:END -->"


def collect():
    """从 log/*.md 收集每天的条目：日期 -> [标题列表]"""
    days = []
    for f in sorted(glob.glob(os.path.join(BASE, "log", "*.md"))):
        date = os.path.basename(f)[:-3]          # 2026-11-24
        text = open(f, encoding="utf-8").read()
        titles = re.findall(r"(?m)^## (\d{2}:\d{2})\s+(.+)$", text)
        if titles:
            days.append((date, titles))
    days.sort(reverse=True)                       # 日期倒序
    return days


def build(days):
    L = []
    L.append(BEGIN)
    L.append("")
    L.append("> **本表由 `tools/gen-index.py` 自动生成，不要手改。**")
    L.append("> 详情去 `log/YYYY-MM-DD.md` 查。")
    L.append("")
    L.append("| 日期 | 条目 | 摘要 |")
    L.append("|---|---|---|")
    for date, titles in days:
        n = len(titles)
        # 摘要取当天最后一条（通常是最重要的收尾）或第一条
        summary_src = titles[-1][1] if titles else ""
        summary = summary_src.replace("|", "\\|")[:70]
        L.append("| **%s** | %d 条 | %s |" % (date, n, summary))
    L.append("")
    L.append(END)
    return "\n".join(L)


def main():
    if not os.path.exists(OUTLINE):
        print("找不到 OUTLINE.md")
        return 1
    t = open(OUTLINE, encoding="utf-8").read()

    days = collect()
    block = build(days)

    if BEGIN in t and END in t:
        # 替换标记之间的内容
        pattern = re.escape(BEGIN) + r".*?" + re.escape(END)
        new = re.sub(pattern, block, t, flags=re.S)
    else:
        # 没有标记，追加到文件末尾
        new = t.rstrip() + "\n\n## 附：变更时间索引\n\n" + block + "\n"

    open(OUTLINE, "w", encoding="utf-8").write(new)
    print("已更新索引：%d 天" % len(days))
    for d, ts in days:
        print("  %s  %d 条" % (d, len(ts)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
