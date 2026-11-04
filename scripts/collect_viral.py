"""도파민 인기글 수집 (패턴 학습용). 레딧 RSS + 네이트판 랭킹 -> agent-hq-data/corpus/viral.jsonl
원문은 비공개 데이터 레포에만 저장하고 분석 전용으로 쓴다. 게시물은 재창작만 한다(원문 복붙 금지).
사용: python scripts/collect_viral.py [--reddit-limit 100] [--nate-pages 3]
"""
import argparse, json, re, time, html, sys
from pathlib import Path
from urllib.request import Request, urlopen

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
OUT = Path(__file__).resolve().parent.parent / "agent-hq-data" / "corpus" / "viral.jsonl"
if not OUT.parent.exists():  # 로컬: 형제 폴더 / Actions: 레포 루트에 연결된 폴더
    OUT = Path(__file__).resolve().parent.parent.parent / "agent-hq-data" / "corpus" / "viral.jsonl"

SUBS = ["AmItheAsshole", "AITAH", "relationship_advice", "TrueOffMyChest", "pettyrevenge",
        "ProRevenge", "MaliciousCompliance", "entitledparents", "tifu", "confessions"]
NATE_LISTS = ["/talk/ranking", "/talk/ranking/d", "/talk/ranking/w", "/talk/ranking/m"]


def get(url):
    for i in range(3):
        try:
            return urlopen(Request(url, headers={"User-Agent": UA}), timeout=20).read().decode("utf-8", "replace")
        except Exception as e:
            time.sleep(2 * (i + 1))
    print("FAIL", url, file=sys.stderr)
    return ""


def text(h):
    h = re.sub(r"<br\s*/?>|</p>", "\n", h)
    h = re.sub(r"<[^>]+>", "", h)
    return re.sub(r"\n{3,}", "\n\n", html.unescape(h)).strip()


def reddit(limit):
    for sub in SUBS:
        for t in ("year", "month"):
            x = get(f"https://www.reddit.com/r/{sub}/top/.rss?t={t}&limit={limit}")
            for e in re.findall(r"<entry>(.*?)</entry>", x, re.S):
                id_ = re.search(r"<id>(.*?)</id>", e).group(1)
                title = html.unescape(re.search(r"<title>(.*?)</title>", e, re.S).group(1))
                c = re.search(r"<content[^>]*>(.*?)</content>", e, re.S)
                body = text(html.unescape(c.group(1))) if c else ""
                yield {"id": "r:" + id_, "src": f"reddit/{sub}", "range": t, "title": title, "body": body[:4000], "comments": []}
            time.sleep(2)


def nate(pages):
    for lst in NATE_LISTS:
        ids = []
        for p in range(1, pages + 1):
            h = get(f"https://pann.nate.com{lst}?page={p}")
            ids += [i for i in re.findall(r'href="/talk/(\d{8,})"', h) if i not in ids]
            time.sleep(1)
        for i in ids:
            h = get(f"https://pann.nate.com/talk/{i}")
            m = re.search(r'id="contentArea">(.*?)</div>', h, re.S)
            if not m:
                continue
            t = re.search(r'<h4[^>]*>(.*?)</h4>', h, re.S) or re.search(r'property="og:title" content="([^"]*)"', h)
            cm = [text(c) for c in re.findall(r'class="usertxt"[^>]*>(.*?)</dd>', h, re.S)][:5]
            yield {"id": "n:" + i, "src": "natepann", "range": lst, "title": re.sub(r"\s*\|\s*네이트 판.*$", "", text(t.group(1))) if t else "",
                   "body": text(m.group(1))[:4000], "comments": [c[:300] for c in cm]}
            time.sleep(1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--reddit-limit", type=int, default=100)
    ap.add_argument("--nate-pages", type=int, default=3)
    ap.add_argument("--only", choices=["reddit", "nate"])
    a = ap.parse_args()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    seen = set()
    if OUT.exists():
        seen = {json.loads(l)["id"] for l in OUT.read_text(encoding="utf-8").splitlines() if l.strip()}
    n = 0
    with OUT.open("a", encoding="utf-8") as f:
        srcs = []
        if a.only != "nate": srcs.append(reddit(a.reddit_limit))
        if a.only != "reddit": srcs.append(nate(a.nate_pages))
        for gen in srcs:
            for r in gen:
                if r["id"] in seen or len(r["body"]) < 200:
                    continue
                seen.add(r["id"]); n += 1
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"added {n}, total {len(seen)} -> {OUT}")
