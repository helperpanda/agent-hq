#!/usr/bin/env python3
"""카드뉴스 PNG 합성 (1080x1350).
사용: python divisions/cardnews/render.py spec.json outdir
spec.json: {"bg_query":"inflation grocery", "cards":[{"headline":"...", "body":"..."}, ...]}
PEXELS_API_KEY 가 없거나 실패하면 단색 그라데이션 배경으로 대체."""
import json, os, sys, io, urllib.request, urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1350
FONTS = ["/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf", "C:/Windows/Fonts/malgunbd.ttf",
         "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", "/System/Library/Fonts/AppleSDGothicNeo.ttc"]
FONT = next((f for f in FONTS if Path(f).exists()), None)
def font(size): return ImageFont.truetype(FONT, size) if FONT else ImageFont.load_default()

def pexels_bg(query):
    key = os.environ.get("PEXELS_API_KEY")
    if not key or not query: return None
    try:
        req = urllib.request.Request("https://api.pexels.com/v1/search?per_page=1&orientation=portrait&query=" + urllib.parse.quote(query),
                                     headers={"Authorization": key})
        url = json.load(urllib.request.urlopen(req, timeout=15))["photos"][0]["src"]["large2x"]
        im = Image.open(io.BytesIO(urllib.request.urlopen(url, timeout=20).read())).convert("RGB")
        r = max(W / im.width, H / im.height); im = im.resize((int(im.width * r), int(im.height * r)))
        return im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
    except Exception as e:
        print("pexels 실패, 단색 배경 사용:", e); return None

def gradient(c1, c2):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H; d.line([(0, y), (W, y)], fill=tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)))
    return im

def wrap(draw, text, fnt, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split(" "):
            t = (cur + " " + word).strip()
            if draw.textlength(t, font=fnt) <= maxw: cur = t; continue
            if cur: lines.append(cur)
            cur = ""
            for ch in word:                      # 한 단어가 한 줄보다 길 때만 글자 단위
                if draw.textlength(cur + ch, font=fnt) > maxw: lines.append(cur); cur = ch
                else: cur += ch
        lines.append(cur)
    return lines

def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8")); out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    bg = pexels_bg(spec.get("bg_query")); n = len(spec["cards"])
    for i, c in enumerate(spec["cards"], 1):
        im = (bg.copy().filter(ImageFilter.GaussianBlur(2)) if bg else gradient((24, 32, 56), (70, 40, 90)))
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 150 if bg else 40)); im = Image.alpha_composite(im.convert("RGBA"), ov)
        d = ImageDraw.Draw(im)
        d.text((80, 90), f"{i}/{n}", font=font(40), fill=(255, 255, 255, 170))
        y = 260
        for ln in wrap(d, c["headline"], font(84), W - 160): d.text((80, y), ln, font=font(84), fill=(255, 214, 90)); y += 110
        y += 50
        for ln in wrap(d, c.get("body", ""), font(48), W - 160): d.text((80, y), ln, font=font(48), fill=(255, 255, 255)); y += 72
        d.text((80, H - 110), "헬퍼판다", font=font(36), fill=(255, 255, 255, 190))
        im.convert("RGB").save(out / f"card{i}.png")
    print(f"OK {n}장 → {out}")
main()
