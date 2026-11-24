#!/bin/sh
# 生成 STATE.md 状态快照
#
# 用法：./tools/gen-state.sh
#
# 数据来源：
#   - 磁盘：df
#   - 关键路径：本脚本内的 PATHS 列表
#   - 工具链：command -v 探测
#   - 仓库统计：git
#
# 想让 STATE.md 包含更多内容，改下面的 PATHS 和 TOOLS 即可。

set -e

BASE="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$BASE/STATE.md"
NOW=$(date '+%Y-%m-%d %H:%M')

# ── 按你的机器改这两组 ──
PATHS="
代码项目:/Projects
工具脚本:/Apps
下载:/Downloads
工作区:/Work
"
# 格式：显示名:绝对路径   （每行一个）

TOOLS="
git
node
python3
docker
"
# 想探测哪些命令就列哪些

# ── 开始生成 ──
{
    echo "# 本机当前状态快照"
    echo ""
    echo "> **这是给智能体最快上手的一页。** 想知道「这台机器现在什么样」先读这里；"
    echo "> 想知道「为什么变成这样」读 \`OUTLINE.md\`（按主题）和 \`log/\`（按时间）。"
    echo ""
    echo "**快照时间**：$NOW"
    echo ""
    echo "---"
    echo ""
    echo "## 磁盘"
    echo ""
    echo "| 盘 | 状态 |"
    echo "|---|---|"
    df -h 2>/dev/null | awk 'NR>1 {print "| **" $1 "** | " $2 " total, " $4 " free (" $5 " used) |"}' | head -10
    echo ""
    echo "## 关键路径"
    echo ""
    echo "| 项 | 路径 | 存在 |"
    echo "|---|---|---|"
    echo "$PATHS" | while IFS=: read -r name path; do
        [ -z "$name" ] && continue
        if [ -e "$path" ]; then mark="✅"; else mark="❌"; fi
        echo "| $name | \`$path\` | $mark |"
    done
    echo ""
    echo "## 已装工具"
    echo ""
    echo "| 命令 | 版本 / 路径 |"
    echo "|---|---|"
    echo "$TOOLS" | while read -r cmd; do
        [ -z "$cmd" ] && continue
        if command -v "$cmd" >/dev/null 2>&1; then
            p=$(command -v "$cmd")
            v=$("$cmd" --version 2>/dev/null | head -1 || echo "")
            [ -z "$v" ] && v="$p"
            echo "| \`$cmd\` | $v |"
        else
            echo "| \`$cmd\` | 未安装 |"
        fi
    done
    echo ""
    echo "## 本仓库"
    echo ""
    echo "| 项 | 值 |"
    echo "|---|---|"
    logcount=$(ls "$BASE/log"/*.md 2>/dev/null | wc -l | tr -d ' ')
    entrycount=$(grep -h '^## ' "$BASE/log"/*.md 2>/dev/null | wc -l | tr -d ' ')
    echo "| 日志文件 | $logcount 个 |"
    echo "| 日志条目 | $entrycount 条 |"
    if [ -d "$BASE/.git" ]; then
        echo "| git 提交数 | $(git -C "$BASE" rev-list --count HEAD 2>/dev/null || echo '?') |"
        echo "| 最后提交 | $(git -C "$BASE" log -1 --format='%ci' 2>/dev/null || echo '?') |"
    fi
    echo ""
    echo "---"
    echo ""
    echo "## 红线（动手前必读）"
    echo ""
    echo "> **改这里：换成你自己机器的红线。判断标准是「删掉这条后智能体还能安全行动吗」——能，就不是红线。**"
    echo ""
    echo "1. **（第一条）**"
    echo "2. **（第二条）**"
    echo "3. **（第三条）**"
    echo ""
    echo "---"
    echo ""
    echo "*本文件由 \`tools/gen-state.sh\` 生成，手工修改会被覆盖。*"
} > "$OUT"

echo "已生成: $OUT"
