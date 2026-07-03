#!/usr/bin/env python3
"""
每日采集 bot 聊天数据 → data.csv

  python3 track.py      # 采集 → data.csv
  python3 build.py      # 生成 index.html
  ./setup.sh            # 首次初始化
  ./reset.sh            # 新活动清零
"""

import csv
import sys
from datetime import date
from pathlib import Path

import requests

ROOT = Path(__file__).parent
DATA = ROOT / "data.csv"
BOTS_FILE = ROOT / "bots.txt"

API = "https://hire.yukework.com/hireadmin/polyadmin/robot/list"
HEADERS = {
    "content-type": "application/json",
    "appid": "Poly",
    "origin": "https://hire.yukework.com",
    "referer": "https://hire.yukework.com/static/hms/",
}

try:
    from config import COOKIES
except ImportError:
    print("未找到 config.py")
    print("请先运行: cp config.example.py config.py")
    print("然后编辑 config.py 填入 Cookie")
    sys.exit(1)


def load_cids() -> list[str]:
    if len(sys.argv) > 1:
        return [x.strip() for x in sys.argv[1:] if x.strip()]
    if BOTS_FILE.exists():
        return [
            ln.strip()
            for ln in BOTS_FILE.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.startswith("#")
        ]
    print("用法: python3 track.py <cid1> <cid2> ...")
    print("或在 bots.txt 中每行写一个 cid，再运行 python3 track.py")
    sys.exit(1)


def fetch_bot(cid: str):
    r = requests.post(
        API,
        json={"sceneId": [cid], "pageSize": 10, "pageNum": 1},
        headers=HEADERS,
        cookies=COOKIES,
        timeout=20,
    )
    body = r.json()
    if body.get("errNo") != 0:
        raise RuntimeError(f"{cid}: {body.get('errstr')}")
    items = (body.get("data") or {}).get("list") or []
    if not items:
        return None
    b = items[0]
    return {
        "cid": b.get("sSceneId") or cid,
        "name": b.get("name", ""),
        "creator": b.get("createUser", ""),
        "chats": int(b.get("totalChatCnt") or 0),
    }


def save_row(today: str, row: dict):
    rows = []
    if DATA.exists():
        with DATA.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

    key = (today, row["cid"])
    rows = [r for r in rows if (r["date"], r["cid"]) != key]
    rows.append({
        "date": today,
        "cid": row["cid"],
        "name": row["name"],
        "creator": row["creator"],
        "chats": str(row["chats"]),
    })
    rows.sort(key=lambda r: (r["date"], r["cid"]))

    with DATA.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "cid", "name", "creator", "chats"])
        w.writeheader()
        w.writerows(rows)


def main():
    cids = load_cids()
    today = date.today().isoformat()
    print(f"日期 {today}，采集 {len(cids)} 个 bot\n")

    ok = 0
    for cid in cids:
        try:
            bot = fetch_bot(cid)
        except RuntimeError as e:
            print(f"  ✗ {cid}  {e}")
            continue
        if not bot:
            print(f"  ✗ {cid}  未找到")
            continue
        save_row(today, bot)
        ok += 1
        print(f"  ✓ {bot['name']} ({bot['cid']})  {bot['chats']} chats  [{bot['creator']}]")

    print(f"\n已写入 {DATA}（成功 {ok}/{len(cids)}）")
    if ok:
        print("运行 python3 build.py 更新排行榜页面")


if __name__ == "__main__":
    main()
