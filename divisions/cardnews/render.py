#!/usr/bin/env python3
"""'8시반 머니레터' 카드뉴스 PNG 합성 (1080x1350). 기존 디자인(남색 그라데이션 + 오렌지 포인트) 재현.
사용: python divisions/cardnews/render.py spec.json outdir
spec.json: {"date":"2026-10-02", "cards":[{"label":"오늘의 기회","headline":"두 줄 이내 제목","body":"1~2줄 설명"}, ...3장]}
결과: outdir/card_1.png, card_2.png, card_3.png  (다운로드 폴더에서 card_1 / card_2 / card_3 로 보이도록)
서체 Noto Sans KR 은 없으면 자동 다운로드(캐시: FONT_DIR 또는 ~/.cache/agent-hq-fonts)."""
import json, os, sys, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
BRAND = "8시반 머니레터"
TOP, BOTTOM = (12, 24, 47), (29, 29, 45)
ORANGE, WHITE, CREAM = (255, 138, 42), (255, 255, 255), (255, 244, 230)
MX = 90  # 좌우 여백

FONT_DIR = Path(os.environ.get("FONT_DIR") or Path.home() / ".cache" / "agent-hq-fonts")
URL = "https://github.com/notofonts/noto-cjk/raw/main/Sans/SubsetOTF/KR/NotoSansKR-{}.otf"
def font(weight, size):
    p = FONT_DIR / f"NotoSansKR-{weight}.otf"
    if not p.exists():
        FONT_DIR.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(URL.format(weight), p)
    return ImageFont.truetype(str(p), size)

def background():
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / (H - 1); d.line([(0, y), (W, y)], fill=tuple(round(TOP[i] + (BOTTOM[i] - TOP[i]) * t) for i in range(3)))
    return im

def wrap(d, text, fnt, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split(" "):
            t = (cur + " " + word).strip()
            if d.textlength(t, font=fnt) <= maxw: cur = t; continue
            if cur: lines.append(cur)
            cur = ""
            for ch in word:
                if d.textlength(cur + ch, font=fnt) > maxw: lines.append(cur); cur = ch
                else: cur += ch
        lines.append(cur)
    return lines

def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8")); out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    n = len(spec["cards"]); date = spec["date"]
    f_brand, f_label, f_head, f_body, f_foot = font("Regular", 28), font("Bold", 40), font("Bold", 88), font("Regular", 46), font("Regular", 28)
    for i, c in enumerate(spec["cards"], 1):
        im = background(); d = ImageDraw.Draw(im)
        d.text((MX, 112), BRAND, font=f_brand, fill=CREAM, anchor="lm")
        d.text((W - MX, 112), f"{i}/{n}", font=f_brand, fill=CREAM, anchor="rm")
        d.rectangle([MX, 170, MX + 91, 178], fill=ORANGE)
        d.text((MX, 282), c["label"], font=f_label, fill=ORANGE, anchor="lm")
        y = 406
        for ln in wrap(d, c["headline"], f_head, W - 2 * MX)[:3]:
            d.text((MX, y), ln, font=f_head, fill=WHITE, anchor="lm"); y += 110
        y += 4
        for ln in wrap(d, c.get("body", ""), f_body, W - 2 * MX)[:3]:
            d.text((MX, y), ln, font=f_body, fill=CREAM, anchor="lm"); y += 70
        d.text((MX, 1262), f"{date} 아침 8:30", font=f_foot, fill=ORANGE, anchor="lm")
        im.save(out / f"card_{i}.png")
    print(f"OK {n}장 -> {out}")
main()
