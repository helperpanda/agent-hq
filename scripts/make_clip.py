#!/usr/bin/env python3
"""사장이 직접 받은 영상에서 필요한 구간만 잘라 X용 세로형 클립으로 만든다 (다운로드 기능 없음).
상단 제목 바 + 하단 출처 바를 입힌다. 최대 CLIP_MAX초.
사용: python scripts/make_clip.py <입력.mp4> <시작초> <끝초> <출력폴더> --title "제목\\n둘째줄" --credit "출처: @작성자 (TikTok)"
출력: <출력폴더>/clip.mp4, <출력폴더>/contact.jpg (결과 확인용 4컷)
"""
import argparse, subprocess, sys, tempfile, shutil
from pathlib import Path

CLIP_MAX = 15
FONT = "C:/Windows/Fonts/malgunbd.ttf"
if not Path(FONT).exists():
    FONT = "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"  # Actions(ubuntu)


def esc(p):  # ffmpeg 필터용 경로 이스케이프
    return str(p).replace("\\", "/").replace(":", "\\:")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("start", type=float); ap.add_argument("end", type=float); ap.add_argument("out")
    ap.add_argument("--title", required=True); ap.add_argument("--credit", required=True)
    a = ap.parse_args()
    dur = a.end - a.start
    if dur <= 0 or dur > CLIP_MAX:
        sys.exit(f"구간은 1~{CLIP_MAX}초여야 합니다 (현재 {dur:.1f}초). 원본을 길게 쓰지 않는다는 규칙입니다.")
    if not a.credit.strip():
        sys.exit("출처 표기 필수")
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp())
    (tmp / "t.txt").write_bytes(a.title.replace("\\n", "\n").replace("\r", "").encode("utf-8"))
    (tmp / "c.txt").write_bytes(a.credit.encode("utf-8"))
    vf = (f"scale=720:-2,pad=iw:ih+260:0:160:color=black,"
          f"drawtext=fontfile='{esc(FONT)}':textfile='{esc(tmp/'t.txt')}':fontcolor=white:fontsize=44:line_spacing=10:x=(w-text_w)/2:y=(160-text_h)/2,"
          f"drawtext=fontfile='{esc(FONT)}':textfile='{esc(tmp/'c.txt')}':fontcolor=#bbbbbb:fontsize=28:x=(w-text_w)/2:y=h-70")
    cmd = ["ffmpeg", "-y", "-ss", str(a.start), "-i", a.src, "-t", str(dur), "-vf", vf, "-r", "30",
           "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
           "-movflags", "+faststart", str(out / "clip.mp4")]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        sys.exit("ffmpeg 실패:\n" + r.stderr[-800:])
    # 결과 확인용 컨택트시트
    subprocess.run(["ffmpeg", "-y", "-i", str(out / "clip.mp4"), "-vf", f"fps=4/{dur},scale=270:-2,tile=4x1", "-frames:v", "1", str(out / "contact.jpg")],
                   capture_output=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"OK {out/'clip.mp4'} ({dur:.1f}s)")


if __name__ == "__main__":
    main()
