#!/usr/bin/env python3
"""블로그 이미지 제작. 사용: python divisions/blog/make_images.py spec.json outdir
spec: {"title":"썸네일에 넣을 글 제목", "thumb_query":"english keywords",
       "images":[{"query":"english keywords","caption":"한글 설명(대체 문구)"}, ...]}
결과: outdir/thumb.jpg(대표, 1000x1000), img_1.jpg.. (본문, 폭 1200), contact.jpg(검수용 한눈 보기), credits.txt
기본은 큰 글씨 카드. 사진은 USE_PHOTOS=1 + PEXELS_API_KEY 일 때만 쓴다. 키가 없거나 검색 실패하면 그 장은 글자 카드(그라데이션)로 대체하고 표시한다.
이전에 쓴 사진은 used_photos.txt 로 중복 방지."""
import hashlib, io, json, os, sys, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
USED = ROOT / "used_photos.txt"
FONT_DIR = Path(os.environ.get("FONT_DIR") or Path.home() / ".cache" / "agent-hq-fonts")
URL = "https://github.com/notofonts/noto-cjk/raw/main/Sans/SubsetOTF/KR/NotoSansKR-{}.otf"
UA = {"User-Agent": "agent-hq"}


def font(weight, size):
    p = FONT_DIR / f"NotoSansKR-{weight}.otf"
    if not p.exists():
        FONT_DIR.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(URL.format(weight), p)
    return ImageFont.truetype(str(p), size)


def pexels(query):
    key = os.environ.get("PEXELS_API_KEY")
    if os.environ.get("USE_PHOTOS") != "1" or not key or not query:
        return None
    skip = set(USED.read_text().split()) if USED.exists() else set()
    try:
        req = urllib.request.Request(
            "https://api.pexels.com/v1/search?per_page=15&orientation=landscape&query=" + urllib.parse.quote(query),
            headers={"Authorization": key, **UA})
        for ph in json.load(urllib.request.urlopen(req, timeout=15)).get("photos", []):
            if str(ph["id"]) in skip:
                continue
            raw = urllib.request.urlopen(urllib.request.Request(ph["src"]["large2x"], headers=UA), timeout=25).read()
            with USED.open("a") as f:
                f.write(f"{ph['id']}\n")
            return Image.open(io.BytesIO(raw)).convert("RGB"), f"{ph.get('photographer', '')} / {ph['url']}"
    except Exception as e:
        print("pexels 실패:", query, e)
    return None


def card(text, size):
    w, h = size
    g = int(hashlib.md5(text.encode()).hexdigest(), 16)
    a = (30 + g % 40, 50 + (g >> 8) % 50, 90 + (g >> 16) % 60)
    im = Image.new("RGB", size)
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(c * (1 - t * 0.5)) for c in a))
    return im


def cover(im, size):
    r = max(size[0] / im.width, size[1] / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1))
    x, y = (im.width - size[0]) // 2, (im.height - size[1]) // 2
    return im.crop((x, y, x + size[0], y + size[1]))


def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for word in text.split(" "):
        t = (cur + " " + word).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = word
    return lines + [cur]


def fit(d, text, weight, maxw, maxh, hi, lo=48):
    """칸에 맞는 가장 큰 글씨 크기로 줄바꿈."""
    for sz in range(hi, lo - 1, -4):
        f = font(weight, sz)
        lines = wrap(d, text, f, maxw)
        if len(lines) * sz * 1.3 <= maxh:
            return f, lines, sz
    return f, lines, sz


def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    credits, fallbacks = [], []

    # 대표 이미지: 정사각, 제목 오버레이
    S = 1000
    r = pexels(spec.get("thumb_query"))
    if r:
        base = Image.blend(cover(r[0], (S, S)), Image.new("RGB", (S, S), (0, 0, 0)), 0.45)
        credits.append("thumb: " + r[1])
    else:
        base = card(spec["title"], (S, S))
        fallbacks.append("thumb")
    d = ImageDraw.Draw(base)
    f, lines, sz = fit(d, spec["title"], "Bold", S - 120, 760, 130)
    y = (S - len(lines) * sz * 1.3) / 2 + sz * 0.65
    for ln in lines:
        d.text((60, y), ln, font=f, fill=(255, 255, 255), anchor="lm")
        y += sz * 1.3
    base.save(out / "thumb.jpg", quality=90)
    paths = [out / "thumb.jpg"]

    # 본문 이미지
    for i, it in enumerate(spec.get("images", []), 1):
        r = pexels(it.get("query"))
        if r:
            im = r[0].resize((1200, int(r[0].height * 1200 / r[0].width)))
            credits.append(f"img_{i}: " + r[1])
        else:
            fallbacks.append(f"img_{i}")
            im = card(it.get("caption", ""), (1200, 675))
            dd = ImageDraw.Draw(im)
            ff, lines, sz = fit(dd, it.get("caption", ""), "Bold", 1040, 520, 110)
            yy = (675 - len(lines) * sz * 1.3) / 2 + sz * 0.65
            for ln in lines:
                dd.text((80, yy), ln, font=ff, fill=(255, 255, 255), anchor="lm")
                yy += sz * 1.3
        im.save(out / f"img_{i}.jpg", quality=88)
        paths.append(out / f"img_{i}.jpg")

    # 검수용 한눈 보기 (한 번만 열어보면 전체 확인 가능)
    th = 260
    tiles = []
    for p in paths:
        t = Image.open(p).convert("RGB")
        tiles.append((p.name, t.resize((int(t.width * th / t.height), th))))
    rows = [tiles[i:i + 3] for i in range(0, len(tiles), 3)]
    sheet = Image.new("RGB", (max(sum(t.width + 10 for _, t in rw) for rw in rows), (th + 10) * len(rows)), (255, 255, 255))
    fl = font("Bold", 22)
    y = 0
    for rw in rows:
        x = 0
        for name, t in rw:
            sheet.paste(t, (x, y))
            ImageDraw.Draw(sheet).text((x + 8, y + 6), name, font=fl, fill=(255, 255, 0))
            x += t.width + 10
        y += th + 10
    sheet.save(out / "contact.jpg", quality=80)
    (out / "credits.txt").write_text("\n".join(credits) + ("\n" if credits else ""), encoding="utf-8")
    print(f"OK 이미지 {len(paths)}장 -> {out}" + (f" | 글자카드로 대체: {fallbacks}" if fallbacks else ""))


main()
