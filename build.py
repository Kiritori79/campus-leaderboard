#!/usr/bin/env python3
"""把 data.csv 转成可播放的排行榜页面 index.html"""

import csv
import json
import sys
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data.csv"
ACTIVITY = ROOT / "activity.txt"
TEMPLATE = ROOT / "viewer.html"
OUTPUT = ROOT / "index.html"


def load_activity_name() -> str:
    if ACTIVITY.exists():
        for line in ACTIVITY.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                return line
    return "活动排行榜"


def date_range(start: str, end: str) -> list[str]:
    a = datetime.strptime(start, "%Y-%m-%d").date()
    b = datetime.strptime(end, "%Y-%m-%d").date()
    days = []
    cur = a
    while cur <= b:
        days.append(cur.isoformat())
        cur += timedelta(days=1)
    return days


def build_board(rows: list[dict]) -> dict:
    by_cid: dict[str, dict] = {}
    dates_seen: set[str] = set()

    for r in rows:
        dates_seen.add(r["date"])
        cid = r["cid"]
        if cid not in by_cid:
            by_cid[cid] = {
                "cid": cid,
                "name": r["name"],
                "creator": r["creator"],
                "by_date": {},
            }
        by_cid[cid]["by_date"][r["date"]] = int(r["chats"])
        if r["name"]:
            by_cid[cid]["name"] = r["name"]
        if r["creator"]:
            by_cid[cid]["creator"] = r["creator"]

    sorted_dates = sorted(dates_seen)
    if not sorted_dates:
        return {"name": load_activity_name(), "days": [], "racers": []}

    days = sorted_dates
    racers = []

    for cid, info in by_cid.items():
        series = []
        last = None
        for d in days:
            if d in info["by_date"]:
                last = info["by_date"][d]
            series.append(last)

        first_idx = next((i for i, v in enumerate(series) if v is not None), None)
        if first_idx is None:
            continue

        filled = []
        carry = None
        for v in series:
            if v is not None:
                carry = v
            filled.append(carry if carry is not None else 0)

        label = f"{info['creator']} · {info['name']}" if info["creator"] else info["name"]
        racers.append({
            "cid": cid,
            "name": info["name"],
            "creator": info["creator"],
            "label": label,
            "firstDay": first_idx,
            "series": filled,
        })

    racers.sort(key=lambda x: x["series"][-1], reverse=True)
    return {
        "name": load_activity_name(),
        "days": days,
        "racers": racers,
        "updatedAt": datetime.now().isoformat(timespec="seconds"),
    }


def render(board: dict) -> str:
    template = TEMPLATE.read_text(encoding="utf-8")
    data = json.dumps(board, ensure_ascii=False)
    return template.replace("/*__BOARD_DATA__*/", data)


def main():
    rows = []
    if DATA.exists():
        with DATA.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

    board = build_board(rows)
    OUTPUT.write_text(render(board), encoding="utf-8")

    print(f"活动: {board['name']}")
    if board["days"]:
        print(f"天数: {len(board['days'])}（{board['days'][0]} ~ {board['days'][-1]}）")
        print(f"bot 数: {len(board['racers'])}")
    else:
        print("尚无采集数据（已生成空页面，采集后重新 build 即可）")
    print(f"已生成: {OUTPUT}")

    if "--open" in sys.argv:
        webbrowser.open(OUTPUT.as_uri())


if __name__ == "__main__":
    main()
