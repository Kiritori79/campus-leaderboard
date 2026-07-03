#!/bin/bash
# 一键安装 / 卸载每日自动抓取定时任务（Mac）
# 用法:
#   ./install_cron.sh           # 默认每天 9:00
#   ./install_cron.sh 10:30     # 指定时间
#   ./install_cron.sh --remove  # 卸载

set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$(command -v python3)"
LOG="$DIR/auto.log"
MARKER="# dynamic-leaderboard-track"

usage() {
  echo "用法:"
  echo "  ./install_cron.sh           每天 9:00 自动运行"
  echo "  ./install_cron.sh 10:30     指定时间（24小时制）"
  echo "  ./install_cron.sh --remove  移除定时任务"
}

remove_cron() {
  if ! crontab -l >/dev/null 2>&1; then
    echo "当前没有定时任务"
    exit 0
  fi
  crontab -l 2>/dev/null | grep -v "$MARKER" | grep -v "track.py && .*build.py" | crontab - 2>/dev/null || true
  echo "已移除动态排行榜定时任务"
}

if [[ "${1:-}" == "--remove" || "${1:-}" == "-r" ]]; then
  remove_cron
  exit 0
fi

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ -z "$PYTHON" ]]; then
  echo "未找到 python3，请先安装 Python"
  exit 1
fi

# 解析时间，默认 9:00
TIME="${1:-9:00}"
if [[ "$TIME" =~ ^([0-9]{1,2}):([0-9]{2})$ ]]; then
  HOUR="${BASH_REMATCH[1]}"
  MIN="${BASH_REMATCH[2]}"
else
  echo "时间格式错误，请用 9:00 或 10:30 这种格式"
  exit 1
fi

if (( HOUR < 0 || HOUR > 23 || MIN < 0 || MIN > 59 )); then
  echo "时间超出范围"
  exit 1
fi

JOB="$MIN $HOUR * * * cd $DIR && $PYTHON track.py && $PYTHON build.py >> $LOG 2>&1 $MARKER"

# 合并现有 crontab，去掉旧条目后追加
TMP="$(mktemp)"
if crontab -l >/dev/null 2>&1; then
  crontab -l 2>/dev/null | grep -v "$MARKER" | grep -v "track.py && .*build.py" > "$TMP" || true
else
  : > "$TMP"
fi
echo "$JOB" >> "$TMP"
crontab "$TMP"
rm -f "$TMP"

echo "✓ 已安装定时任务"
echo "  时间: 每天 $(printf '%02d:%02d' "$HOUR" "$MIN")"
echo "  目录: $DIR"
echo "  日志: $LOG"
echo ""
echo "注意: 电脑关机或休眠时不会执行，需保持该时刻电脑开机。"
echo "查看任务: crontab -l"
echo "卸载任务: ./install_cron.sh --remove"
