#!/usr/bin/env python3
"""쇼츠 성과 정밀 분석 (계산은 전부 여기서, 해석은 analyst가). 사용: python scripts/analyze_videos.py [metrics/shorts.csv]
출력: 채널 기준선 / 최근 영상 대비 / 구간별(길이·제목·훅·요일·주제) 비교 / 상관 / 이탈 구간 / 추세. 표본 작으면 '참고용' 표시."""
import csv, sys, statistics as st
from datetime import datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "metrics" / "shorts.csv"
NUM = ["views","likes","saves","followers_delta","duration_s","avg_view_pct","avg_view_s","impressions","ctr_pct","shares","comments","drop_off_s"]
def num(v):
    try: return float(str(v).replace(",", "").strip())
    except Exception: return None
rows = []
for r in csv.DictReader(open(path, encoding="utf-8")):
    if not (r.get("date") or "").strip(): continue
    r = {k: (v or "").strip() for k, v in r.items() if k}
    for k in NUM: r[k] = num(r.get(k))
    rows.append(r)
rows.sort(key=lambda r: r["date"]); n = len(rows)
print(f"# 쇼츠 분석 (영상 {n}건" + (f", {rows[0]['date']}~{rows[-1]['date']})" if n else ")"))
if n == 0: sys.exit(0)
if n < 5: print(f"⚠️ 표본 {n}건 — 모든 수치는 참고용, 결론/방향 변경 금지")
def vals(key, rs=rows): return [r[key] for r in rs if r.get(key) is not None]
def med(key, rs=rows):
    v = vals(key, rs); return st.median(v) if v else None
def fmt(x, d=0): return "-" if x is None else (f"{x:,.{d}f}")
print("\n## 채널 기준선 (중앙값)")
for k, label, d in [("views","조회수",0),("avg_view_pct","평균 시청 지속률%",1),("avg_view_s","평균 시청 시간(초)",1),("ctr_pct","CTR%",1),("duration_s","영상 길이(초)",0),("followers_delta","구독 증가",1)]:
    print(f"- {label}: {fmt(med(k), d)} (n={len(vals(k))})")
bv = med("views")
print("\n## 최근 영상 (기준선 대비)")
for r in rows[-7:]:
    ratio = f"{r['views']/bv:.1f}배" if r["views"] is not None and bv else "-"
    print(f"- {r['date']} | {r['title'][:24]} | 조회 {fmt(r['views'])} ({ratio}) | 지속률 {fmt(r['avg_view_pct'],1)}% | CTR {fmt(r['ctr_pct'],1)}% | 이탈 {fmt(r['drop_off_s'])}초 | 훅: {r['hook'][:24]}")
def groups(title, keyfn, min_n=1):
    g = {}
    for r in rows:
        k = keyfn(r)
        if k: g.setdefault(k, []).append(r)
    if len(g) < 2: return
    print(f"\n## {title}")
    for k, rs in sorted(g.items(), key=lambda kv: -(med("views", kv[1]) or 0)):
        if len(rs) < min_n: continue
        tag = "" if len(rs) >= 3 else " (참고용)"
        print(f"- {k}: n={len(rs)} | 조회 중앙값 {fmt(med('views', rs))} | 지속률 중앙값 {fmt(med('avg_view_pct', rs),1)}%{tag}")
def dur(r):
    d = r["duration_s"]
    return None if d is None else ("≤20초" if d <= 20 else "21~35초" if d <= 35 else "36~50초" if d <= 50 else ">50초")
groups("영상 길이별", dur)
groups("제목 길이별", lambda r: "≤15자" if len(r["title"]) <= 15 else "16~25자" if len(r["title"]) <= 25 else ">25자")
def hook(r):
    h = r["hook"]
    if not h: return None
    return "질문형" if ("?" in h or h.endswith("요")) else ("숫자 포함" if any(c.isdigit() for c in h) else "단정/기타")
groups("훅 유형별", hook)
groups("업로드 요일별", lambda r: "월화수목금토일"[datetime.strptime(r["date"], "%Y-%m-%d").weekday()] if len(r["date"]) == 10 else None)
groups("주제별", lambda r: r["topic"])
print("\n## 상관 (n≥8일 때만)")
def corr(a, b, label):
    pairs = [(r[a], r[b]) for r in rows if r[a] is not None and r[b] is not None]
    if len(pairs) < 8: print(f"- {label}: 표본 {len(pairs)}건 — 계산 안 함"); return
    try: print(f"- {label}: r={st.correlation(*zip(*pairs)):+.2f} (n={len(pairs)})")
    except st.StatisticsError: print(f"- {label}: 값 변화 없음")
corr("avg_view_pct", "views", "지속률 ↔ 조회수"); corr("duration_s", "avg_view_pct", "길이 ↔ 지속률"); corr("ctr_pct", "views", "CTR ↔ 조회수")
d = vals("drop_off_s")
if d:
    early = sum(1 for x in d if x <= 3)
    print(f"\n## 이탈 구간\n- 가장 많이 빠지는 지점 중앙값 {st.median(d):.0f}초, 3초 이내 이탈 {early}/{len(d)}건" + (" → 훅 문제 가능성" if early / len(d) >= 0.5 else ""))
if n >= 10:
    a, b = med("views", rows[-5:]), med("views", rows[-10:-5])
    print(f"\n## 추세\n- 최근 5편 조회 중앙값 {fmt(a)} vs 직전 5편 {fmt(b)} ({(a/b-1)*100:+.0f}%)" if a and b else "")
