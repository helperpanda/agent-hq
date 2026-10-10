#!/usr/bin/env python3
"""승인/반려 이슈 처리. env: BODY. 작업 디렉터리=public 레포 루트, 데이터 레포는 ./_data"""
import os, re, csv, sys, json, subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta
ROOT = Path(__file__).resolve().parent.parent; DATA = ROOT / "_data"
f = {m.group(1).strip(): m.group(2).strip() for m in re.finditer(r"### (.+?)\n\n(.*?)(?=\n### |\Z)", os.environ["BODY"], re.S)}
tid, dec, cm = f.get("대상", ""), f.get("결정", ""), f.get("코멘트", "")
cm = "" if cm == "_No response_" else cm.replace("\n", " ")
if not re.fullmatch(r"(blog)/\d{4}-\d{2}-\d{2}(-\d)?", tid): print("ERR 대상 형식 오류"); sys.exit(1)
if dec not in ("승인", "반려"): print("ERR 결정은 승인/반려"); sys.exit(1)
d = DATA / "outbox" / tid
if not d.is_dir(): print("ERR 없는 항목"); sys.exit(1)
now = datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")
(d / ("APPROVED" if dec == "승인" else "REJECTED")).write_text(f"{now}\n{cm}\n", encoding="utf-8")
fb = DATA / "feedback" / "decisions.csv"; new = not fb.exists()
with fb.open("a", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    if new: w.writerow(["time", "target", "decision", "comment"])
    w.writerow([now, tid, dec, cm])
py = sys.executable
subprocess.run([py, "scripts/pending.py", str(DATA / "outbox")], check=True)
div = tid.split("/")[0]
left = [p for p in json.load(open("docs/data/pending.json", encoding="utf-8")) if p["division"] == div]
if left: subprocess.run([py, "scripts/status.py", div, "waiting", f"승인 대기 {len(left)}건"])
else: subprocess.run([py, "scripts/status.py", div, "done", f"{tid.split('/')[1]} {dec}됨"])
print(f"OK {tid} {dec}")
