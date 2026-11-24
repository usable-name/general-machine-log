# -*- coding: utf-8 -*-
"""生成 STATE.md 状态快照（通用版）。

用法：
    python tools/gen-state.py

改内容就改下面的 PATHS / TOOLS / REDLINES。
"""
import io, os, re, sys, json, glob, shutil, subprocess, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "STATE.md")

# ── 按你的机器改 ──
PATHS = [
    ("代码项目", "D:\\Projects"),
    ("工具脚本", "D:\\Apps"),
    ("下载",     "D:\\Downloads"),
    ("工作区",   "D:\\Work"),
]
TOOLS = ["git", "node", "python", "docker", "code"]

REDLINES = [
    "**（第一条红线）**——写明为什么不能做、后果是什么",
    "**（第二条）**",
    "**（第三条）**",
]


def run(cmd, timeout=20):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return (r.stdout or "").strip()
    except Exception:
        return ""


def main():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    L = []
    A = L.append

    A("# 本机当前状态快照")
    A("")
    A("> **这是给智能体最快上手的一页。** 想知道「这台机器现在什么样」先读这里；")
    A("> 想知道「为什么变成这样」读 `OUTLINE.md`（按主题）和 `log/`（按时间）。")
    A("")
    A("**快照时间**：%s　｜　**生成方式**：`python tools/gen-state.py`" % now)
    A("")
    A("---")
    A("")
    A("## 磁盘")
    A("")
    A("| 盘 | 总容量 | 可用 | 可用率 |")
    A("|---|---|---|---|")
    for d in ("C", "D"):
        try:
            t, u, f = shutil.disk_usage(d + ":\\")
            A("| **%s** | %.1f GB | %.1f GB | %.0f%% |" % (d, t/2**30, f/2**30, f*100.0/t))
        except Exception:
            A("| **%s** | — | — | — |" % d)
    A("")
    A("## 关键路径")
    A("")
    A("| 项 | 路径 | 存在 |")
    A("|---|---|---|")
    for name, p in PATHS:
        A("| %s | `%s` | %s |" % (name, p, "✅" if os.path.exists(p) else "❌"))
    A("")
    A("## 已装工具")
    A("")
    A("| 命令 | 版本 |")
    A("|---|---|")
    for cmd in TOOLS:
        ver = run("%s --version 2>&1 | head -1" % cmd)
        A("| `%s` | %s |" % (cmd, (ver.replace("|", "\\|")[:60] if ver else "未安装")))
    A("")
    A("## 本仓库")
    A("")
    A("| 项 | 值 |")
    A("|---|---|")
    logs = sorted(glob.glob(os.path.join(BASE, "log", "*.md")))
    entries = sum(len(re.findall(r"^## ", open(f, encoding="utf-8").read(), re.M)) for f in logs)
    A("| 日志文件 | %d 个 |" % len(logs))
    A("| 日志条目 | %d 条 |" % entries)
    if logs:
        A("| 最新日志 | %s |" % os.path.basename(logs[-1]))
    cnt = run('git -C "%s" rev-list --count HEAD' % BASE)
    if cnt:
        A("| git 提交数 | %s |" % cnt)
    A("")
    A("---")
    A("")
    A("## 红线（动手前必读）")
    A("")
    for i, r in enumerate(REDLINES, 1):
        A("%d. %s" % (i, r))
    A("")
    A("---")
    A("")
    A("*本文件由 `tools/gen-state.py` 生成，手工修改会被覆盖。*")
    A("")

    open(OUT, "w", encoding="utf-8").write("\n".join(L))
    print("已生成: %s (%d 行)" % (OUT, len(L)))


if __name__ == "__main__":
    main()
