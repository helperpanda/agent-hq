#!/usr/bin/env python3
"""에이전트 상태 기록 → docs/data/status.json + log.json (대시보드용)

사용법:
  python scripts/status.py <agent> <working|done|waiting|error|idle> "메시지"
  python scripts/status.py <agent> done "메시지" --push   # 바로 GitHub에 반영
"""
import json, sys, subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

KST = timezone(timedelta(hours=9))
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "docs" / "data"
STATES = {"working", "done", "waiting", "error", "idle"}
LOG_MAX = 200

def load(p, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

def main():
    args = [a for a in sys.argv[1:] if a != "--push"]
    push = "--push" in sys.argv
    if len(args) < 3 or args[1] not in STATES:
        print(__doc__); sys.exit(1)
    agent, state, msg = args[0], args[1], " ".join(args[2:])
    team = {a["id"] for a in load(DATA / "team.json", [])}
    if team and agent not in team:
        print(f"알 수 없는 에이전트: {agent} (team.json 확인)"); sys.exit(1)

    now = datetime.now(KST).isoformat(timespec="seconds")
    status = load(DATA / "status.json", {})
    status[agent] = {"state": state, "message": msg, "updated": now}
    (DATA / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")

    log = load(DATA / "log.json", [])
    log.insert(0, {"time": now, "agent": agent, "state": state, "message": msg})
    (DATA / "log.json").write_text(json.dumps(log[:LOG_MAX], ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[{agent}] {state}: {msg}")

    if push:
        subprocess.run(["git", "add", "docs/data"], cwd=ROOT)
        subprocess.run(["git", "commit", "-q", "-m", f"status: {agent} {state}"], cwd=ROOT)
        subprocess.run(["git", "push", "-q"], cwd=ROOT)

if __name__ == "__main__":
    main()
