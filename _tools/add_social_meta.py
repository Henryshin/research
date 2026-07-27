# -*- coding: utf-8 -*-
"""
add_social_meta.py — og:image / twitter:image 를 각 페이지 <head> 에 주입한다.

배경: 전 페이지가 twitter:card=summary_large_image 를 선언해놓고 정작
og:image 가 0건이었다. 그래서 X/레딧/슬랙/카톡에 링크를 붙여도 큰 카드가
뜨지 않았다. make_og.py 가 만든 카드를 여기서 연결한다.

동작:
- <meta name="theme-color"> 뒤에 마커 블록을 idempotent 삽입/교체.
  (canonical 뒤는 add_hreflang.py 의 블록이 점유하므로 겹치지 않게 띄운다.)
- 이미지 URL 은 canonical 에서 뽑은 절대 https URL + 콘텐츠 해시 쿼리.
  함정: X/LinkedIn 은 OG 이미지를 URL 단위로 몇 주간 캐시한다. 파일을
  갈아끼워도 옛 이미지를 계속 쓴다. ?v=<md58> 를 붙여 재생성 시 자동 무효화.
- 하드 가드: og.png 가 없으면 절대 메타를 넣지 않는다. 404 이미지를 가리키면
  X 가 카드를 통째로 숨기고 그 실패를 캐시한다.

매핑:
    <slug>/index.html -> <slug>/assets/og.png
    index.html (허브)  -> assets/og.png
    about/index.html   -> assets/og.png (허브 카드 재사용)

사용:
    python _tools/add_social_meta.py            # 전체
    python _tools/add_social_meta.py tck-064760-sic-ring hub about
    python _tools/add_social_meta.py --dry-run  # 변경 미리보기
"""
import glob
import hashlib
import io
import os
import re
import sys
from html import escape, unescape

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

START = "<!-- social:auto (add_social_meta.py) -->"
END = "<!-- /social:auto -->"
BLOCK_RE = re.compile(re.escape(START) + r".*?" + re.escape(END) + r"\n?", re.S)

CANON_RE = re.compile(r'<link\s+rel="canonical"\s+href="([^"]+)"\s*/?>', re.I)
ANCHOR_RE = re.compile(r'<meta\s+name="theme-color"[^>]*>', re.I)
OGTITLE_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)


def site_base(canonical):
    """canonical -> (origin, 사이트 루트 경로).

    /research/ 를 하드코딩하지 않는다. 나중에 커스텀 도메인으로 옮겨도
    canonical 만 바뀌면 자동으로 따라온다.
    """
    m = re.match(r"^(https?://[^/]+)(/.*)?$", canonical)
    origin = m.group(1)
    seg = (m.group(2) or "/").strip("/").split("/")
    base = "/" + seg[0] + "/" if seg and seg[0] else "/"
    return origin, base


def build_block(img_url, alt):
    alt = escape(alt, quote=True)
    return "\n".join([
        START,
        f'<meta property="og:image" content="{img_url}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{alt}">',
        f'<meta name="twitter:image" content="{img_url}">',
        f'<meta name="twitter:image:alt" content="{alt}">',
        END,
    ])


def png_for(rel_dir):
    """페이지 디렉토리(ROOT 기준 상대) -> (png 절대경로, 사이트 내 상대 URL 경로)"""
    if rel_dir in ("", "about"):
        return os.path.join(ROOT, "assets", "og.png"), "assets/og.png"
    return (os.path.join(ROOT, rel_dir, "assets", "og.png"),
            f"{rel_dir}/assets/og.png")


def process(path, dry=False):
    rel_dir = os.path.relpath(os.path.dirname(path), ROOT).replace("\\", "/")
    if rel_dir == ".":
        rel_dir = ""

    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    m = CANON_RE.search(html)
    if not m:
        return "SKIP (canonical 없음)"
    origin, base = site_base(m.group(1))

    png, url_path = png_for(rel_dir)
    if not os.path.isfile(png):
        # 404 를 가리키느니 아무것도 안 넣는 게 낫다.
        return "SKIP (og.png 없음 — make_og.py 먼저)"

    with open(png, "rb") as f:
        h = hashlib.md5(f.read()).hexdigest()[:8]
    img_url = f"{origin}{base}{url_path}?v={h}"

    tm = OGTITLE_RE.search(html)
    alt = unescape(tm.group(1)) if tm else "Henry Shin Research"
    alt = alt.split("—")[0].strip() + " — social card"

    block = build_block(img_url, alt)

    if START in html:
        new = BLOCK_RE.sub(block + "\n", html, count=1)
        action = "UPDATED"
    else:
        am = ANCHOR_RE.search(html)
        if am:
            new = html.replace(am.group(0), am.group(0) + "\n" + block, 1)
        else:
            new = html.replace("</head>", block + "\n</head>", 1)
        action = "INSERTED"

    if new == html:
        return "NOCHANGE"
    if dry:
        return f"{action} (dry-run) -> ...{url_path}?v={h}"
    # newline="" 필수: 없으면 윈도우에서 \n 이 \r\n 으로 바뀌어
    # git diff 가 파일 전체 재작성으로 폭발한다.
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(new)
    return f"{action} -> ...{url_path}?v={h}"


def targets(args):
    slugs = [a for a in args if not a.startswith("-")]
    if not slugs:
        paths = sorted(glob.glob(os.path.join(ROOT, "*", "index.html")))
        paths = [p for p in paths
                 if not os.path.basename(os.path.dirname(p)).startswith("_")]
        return paths + [os.path.join(ROOT, "index.html")]
    out = []
    for s in slugs:
        out.append(os.path.join(ROOT, "index.html") if s == "hub"
                   else os.path.join(ROOT, s, "index.html"))
    return out


def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args
    for p in targets(args):
        label = os.path.relpath(p, ROOT).replace("\\", "/")
        if not os.path.isfile(p):
            print(f"{label:50s} MISSING")
            continue
        print(f"{label:50s} {process(p, dry)}")


if __name__ == "__main__":
    main()
