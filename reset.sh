#!/bin/bash
# 重置为全新活动（清空数据，保留模板与脚本）
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

rm -f data.csv index.html auto.log

cat > activity.txt << 'EOF'
你的活动名称
# ↑ 把第一行改成本次活动名称（页面副标题会显示）
# 改完后运行: python3 build.py
EOF

cat > bots.txt << 'EOF'
# 每行一个 bot cid（sSceneId），# 开头为注释
# 示例:
# 4pefe
# 4p7kS
EOF

if [[ ! -f config.py ]]; then
  cp config.example.py config.py
  echo "✓ 已创建 config.py（请填入 Cookie）"
fi

python3 build.py

echo ""
echo "✓ 新活动已就绪"
echo "  1. 编辑 activity.txt — 活动名称"
echo "  2. 编辑 config.py     — Cookie（若尚未配置）"
echo "  3. 编辑 bots.txt       — bot cid 列表"
echo "  4. python3 track.py    — 首次采集"
echo "  5. python3 build.py --open — 查看排行榜"
