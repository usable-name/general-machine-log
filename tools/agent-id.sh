#!/bin/sh
# 输出当前智能体的标识：<平台>-<模型>-<对话id>
# 用法：./tools/agent-id.sh [模型名]
#
# 平台和对话 id 自动从环境变量推断；模型名各平台不统一暴露，需手动传入，
# 不传则用 unknown。
#
# 支持的平台环境变量（按优先级）：
#   CLAUDE_SESSION_ID     Claude Code
#   CURSOR_SESSION_ID     Cursor
#   CODEX_SESSION_ID      Codex
#   CODEBUDDY_SESSION_ID  WorkBuddy / CodeBuddy
#   DSH_SESSION_ID        DeepSeek Harness
#   AGENT_PLATFORM/AGENT_CONV_ID   手动指定（兜底）
#
# 想加自己的平台，在下面「平台探测」段加一段即可。

MODEL="${1:-unknown}"
PLATFORM=""
CONV=""

# 取对话 id 前 8 位：先剥掉各家可能带的固定前缀，再截断
short_id() {
    printf '%s' "$1" \
        | sed -e 's/^session-//' -e 's/^sess_//' -e 's/^conv-//' \
        | cut -c1-8
}

# ── 平台探测（按优先级，命中即停）──
detect() {
    [ -n "$PLATFORM" ] && return 0
    var_name="$1"
    label="$2"
    eval "val=\$$var_name"
    if [ -n "$val" ]; then
        PLATFORM="$label"
        CONV=$(short_id "$val")
    fi
}

detect CLAUDE_SESSION_ID    "Claude"
detect CURSOR_SESSION_ID    "Cursor"
detect CODEX_SESSION_ID     "Codex"
detect CODEBUDDY_SESSION_ID "WorkBuddy"
detect DSH_SESSION_ID       "DSH"
detect WINDSURF_SESSION_ID  "Windsurf"
detect CLINE_SESSION_ID     "Cline"

# ── 兜底：从工作区目录名取（形如 2026-10-26-19-47-59）──
if [ -z "$PLATFORM" ]; then
    PLATFORM="${AGENT_PLATFORM:-unknown}"
    CONV=$(basename "$(pwd)" 2>/dev/null | sed 's/[^0-9-]//g' | cut -c1-10)
    [ -z "$CONV" ] && CONV="${AGENT_CONV_ID:-none}"
fi

printf '%s-%s-%s\n' "$PLATFORM" "$MODEL" "$CONV"
