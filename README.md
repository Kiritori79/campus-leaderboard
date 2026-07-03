# 动态排行榜 · 模板

0 数据开箱即用。复制本文件夹 → 改配置 → 采集 → 生成动画看板。

## 三步开活动

```bash
./setup.sh
```

1. `activity.txt` — 活动名称（第一行）
2. `config.py` — `cp config.example.py config.py`，填入 Cookie
3. `bots.txt` — 每行一个 bot cid

```bash
python3 track.py
python3 build.py --open
```

## 常用命令

| 命令 | 作用 |
|------|------|
| `python3 track.py` | 采集今日 → `data.csv` |
| `python3 build.py --open` | 生成并打开看板 |
| `./reset.sh` | 清空数据，开始新活动 |
| `./install_cron.sh 11:30` | 每天定时采集（需 Mac 开机） |

## 文件

| 文件 | 说明 |
|------|------|
| `activity.txt` | 活动名 |
| `bots.txt` | 参赛 cid |
| `config.py` | Cookie（本地，勿提交） |
| `data.csv` | 采集数据（自动生成） |
| `viewer.html` | 页面模板 |
| `index.html` | 看板（build 生成） |

## WorkBuddy 话术

```
帮我初始化动态排行榜项目
把活动名称改成「XXX」
帮我更新 Cookie：ZYBIPSCAS=...; IPS_BL=...; ZYBIPSUN=...
在 bots.txt 加上这些 cid：4pefe、4p7kS
采集今天的数据并生成排行榜
帮我重置项目，开始一场新活动
```
