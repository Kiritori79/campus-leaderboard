#!/bin/bash
# 每日自动采集 & 推送
# 由 launchd 在每天 17:30 触发

cd "/Users/taoying/Desktop/校园排行榜" || exit 1
LOG="auto.log"

echo "===== $(date '+%Y-%m-%d %H:%M:%S') =====" >> "$LOG"
/usr/bin/python3 track.py >> "$LOG" 2>&1
echo "---" >> "$LOG"
/usr/bin/python3 build.py >> "$LOG" 2>&1
echo "---" >> "$LOG"
git push >> "$LOG" 2>&1
echo "" >> "$LOG"
