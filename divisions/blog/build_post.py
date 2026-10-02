#!/usr/bin/env python3
"""post.md + 이미지를 합쳐 복붙용 post.html(이미지 내장) 생성.
사용: python divisions/blog/build_post.py outbox/blog/YYYY-MM-DD
post.md 안에서 이미지는 ![설명](img_1.jpg) 형식. 첫 줄은 '# 제목'."""
import base64, re, sys
from pathlib import Path
import markdown

d = Path(sys.argv[1])
md = (d / "post.md").read_text(encoding="utf-8")


def inline(m):
    p = d / m.group(2)
    if not p.exists():
        return m.group(0)
    return f"![{m.group(1)}](data:image/jpeg;base64,{base64.b64encode(p.read_bytes()).decode()})"


body = markdown.markdown(re.sub(r"!\[(.*?)\]\((.*?)\)", inline, md), extensions=["extra", "sane_lists"])
tags = (d / "tags.txt").read_text(encoding="utf-8").strip() if (d / "tags.txt").exists() else ""
note = f"① 아래 본문 전체를 드래그해서 복사 → 네이버 스마트에디터에 붙여넣기 ② 대표 이미지는 thumb.jpg 업로드 ③ 태그: {tags}"
css = ("body{max-width:720px;margin:24px auto;font:16px/1.8 'Malgun Gothic',sans-serif;color:#222;padding:0 16px}"
       "img{max-width:100%;display:block;margin:18px 0}h1{font-size:26px}h2{font-size:20px;margin-top:32px}"
       ".box{background:#f4f4f4;padding:12px;font-size:13px;color:#555}")
(d / "post.html").write_text(
    f'<!doctype html><meta charset="utf-8"><title>블로그 원고</title><style>{css}</style><div class="box">{note}</div>{body}',
    encoding="utf-8")
print("OK", d / "post.html")
