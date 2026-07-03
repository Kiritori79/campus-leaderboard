#!/bin/bash
# 首次使用：安装依赖 + 初始化配置 + 生成空页面
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "▸ 安装 Python 依赖…"
pip3 install -r requirements.txt -q

if [[ ! -f config.py ]]; then
  cp config.example.py config.py
  echo "▸ 已创建 config.py — 请填入浏览器 Cookie"
else
  echo "▸ config.py 已存在，跳过"
fi

python3 build.py

echo ""
echo "✓ 初始化完成"
echo ""
echo "下一步："
echo "  1. 编辑 activity.txt  — 活动名称"
echo "  2. 编辑 config.py      — Cookie"
echo "  3. 编辑 bots.txt       — bot cid"
echo "  4. python3 track.py && python3 build.py --open"
echo ""
echo "开始新活动: ./reset.sh"
