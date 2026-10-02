#!/usr/bin/env python3
"""outbox에서 승인/반려 표시가 없는 결과물 폴더를 찾아 docs/data/pending.json 생성 (파일 내용은 포함하지 않음)
사용: python scripts/pending.py [outbox 경로]"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "outbox"
BASE = "https://github.com/helperpanda/agent-hq-data/tree/main/outbox/"
items = []
for d in sorted(out.glob("*/*")):
    if not d.is_dir() or (d / "APPROVED").exists() or (d / "REJECTED").exists(): continue
    n = sum(1 for f in d.iterdir() if f.is_file())
    if n: items.append({"id": f"{d.parent.name}/{d.name}", "division": d.parent.name, "date": d.name, "files": n, "url": BASE + f"{d.parent.name}/{d.name}"})
items.sort(key=lambda x: x["date"], reverse=True)
(ROOT / "docs/data/pending.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"pending {len(items)}")
