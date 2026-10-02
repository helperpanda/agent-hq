#!/usr/bin/env python3
"""LLM을 돌릴 가치가 있는지 싼 검사로 먼저 판단. exit 0=실행, 1=생략(상태만 기록)"""
import sys, json, subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
KST = timezone(timedelta(hours=9))
agent = sys.argv[1]
def say(who, msg):
    subprocess.run([sys.executable, str(ROOT/"scripts"/"status.py"), who, "idle", msg])
def metric_rows():
    n = 0
    for f in (ROOT/"metrics").glob("*.csv"):
        n += max(0, sum(1 for l in open(f, encoding="utf-8") if l.strip()) - 1)
    return n
if agent in ("analyst", "improver"):
    n = metric_rows()
    if n < 5:
        say("analyst" if agent == "analyst" else "chief", f"성과 데이터 {n}/5건 - 쌓이는 중 (실행 생략)")
        sys.exit(1)
if agent == "chief":
    today = datetime.now(KST).date().isoformat()
    log = json.load(open(ROOT/"docs/data/log.json", encoding="utf-8"))
    if not [l for l in log if l["time"].startswith(today) and l["agent"] != "chief" and l["state"] != "idle"]:
        say("chief", "오늘 활동 없음 - 보고 생략")
        sys.exit(1)
sys.exit(0)
