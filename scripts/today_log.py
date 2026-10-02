#!/usr/bin/env python3
"""오늘 로그만 출력 (log.json 전체를 읽지 않기 위한 토큰 절약용)"""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
today = datetime.now(timezone(timedelta(hours=9))).date().isoformat()
for l in json.load(open(Path(__file__).resolve().parent.parent/"docs/data/log.json", encoding="utf-8")):
    if l["time"].startswith(today): print(f'{l["time"][11:16]} {l["agent"]} {l["state"]} {l["message"]}')
