#!/usr/bin/env python3
"""
排行榜 Railway 部署服务器
- 提供静态页面服务 (index.html)
- 每天 17:30 北京时间自动采集 + 更新页面
"""

import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, send_file
from apscheduler.schedulers.background import BackgroundScheduler

ROOT = Path(__file__).parent

# ── 日志 ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


# ── 确保 config.py 存在（Railway 环境从 Secret Variables 读取） ──
def ensure_config():
    config_path = ROOT / "config.py"
    if config_path.exists():
        return

    cookies = {
        "IPS_BL": os.environ.get("COOKIE_IPS_BL", ""),
        "ZYBIPSCAS": os.environ.get("COOKIE_ZYBIPSCAS", ""),
        "ZYBIPSUN": os.environ.get("COOKIE_ZYBIPSUN", ""),
    }

    if any(cookies.values()):
        config_path.write_text(f"COOKIES = {cookies!r}\n", encoding="utf-8")
        logging.info("✓ 从环境变量创建 config.py")
    else:
        logging.warning("⚠ 未设置 Cookie 环境变量，track.py 可能无法采集数据")


ensure_config()

# ── Flask 应用 ──
app = Flask(__name__)


@app.after_request
def no_cache(response):
    """禁止浏览器缓存，确保每次访问看到最新页面"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/")
def index():
    """排行榜首页"""
    html = ROOT / "index.html"
    if not html.exists():
        return "页面未生成，请先运行 build.py", 503
    return send_file(html)


@app.route("/health")
def health():
    """健康检查"""
    return jsonify({"status": "ok", "time": datetime.now().isoformat()})


@app.route("/update")
def manual_update():
    """手动触发采集 + 更新"""
    try:
        result = run_update()
        return jsonify({"status": "ok", "output": result})
    except Exception as e:
        logging.exception("手动更新失败")
        return jsonify({"status": "error", "message": str(e)}), 500


# ── 核心：采集 + 生成 ──
def run_update():
    """执行 track.py → build.py，更新排行榜数据"""
    logging.info("── 开始每日数据更新 ──")

    ensure_config()

    # Step 1: 采集数据
    logging.info("▶ 采集数据...")
    r1 = subprocess.run(
        [sys.executable, str(ROOT / "track.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=240,
    )
    track_out = r1.stdout.strip()
    for line in track_out.splitlines():
        logging.info(f"  {line}")

    if r1.returncode != 0:
        err = r1.stderr.strip() or track_out
        logging.error(f"❌ track.py 失败 (code={r1.returncode})")
        if r1.stderr.strip():
            logging.error(f"  stderr: {r1.stderr.strip()}")
        raise RuntimeError(f"track.py 失败 (code={r1.returncode}): {err}")

    # Step 2: 生成页面
    logging.info("▶ 生成页面...")
    r2 = subprocess.run(
        [sys.executable, str(ROOT / "build.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    build_out = r2.stdout.strip()
    for line in build_out.splitlines():
        logging.info(f"  {line}")

    if r2.returncode != 0:
        raise RuntimeError(f"build.py 失败: {r2.stderr.strip()}")

    logging.info("✓ 每日更新完成")
    return f"{track_out}\n{build_out}"


# ── 定时任务：每天 17:30 北京时间 ──
scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
scheduler.add_job(
    run_update,
    "cron",
    hour=17,
    minute=30,
    id="daily_update",
    name="每日数据采集与页面更新",
    misfire_grace_time=3600,  # 1 小时容错：服务器重启也能补跑
    coalesce=True,  # 不堆积任务
    max_instances=1,  # 不允许并发
)
scheduler.start()
job = scheduler.get_job("daily_update")
logging.info(f"⏰ 定时任务就绪: 每天 17:30 CST（下次触发: {job.next_run_time}）")


# ── 启动 ──
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
