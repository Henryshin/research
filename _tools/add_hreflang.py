# -*- coding: utf-8 -*-
"""
add_hreflang.py — 각 리포트 index.html에 국제 SEO용 hreflang 대체 태그를 주입한다.

동작:
- <link rel="canonical" href="..."> 를 찾아 그 base URL 기준으로
  ko / en / x-default hreflang(?lang=) 3줄을 canonical 바로 뒤에 삽입.
- idempotent: 기존 <!-- hreflang --> 블록이 있으면 통째로 교체(중복 안 쌓임).

배경: 페이지는 이미 ?lang=ko / ?lang=en 을 지원(JS가 파라미터를 읽어 기본 언어 설정)
하므로 파일을 복제하지 않고 쿼리 URL을 언어별 대체 URL로 구글에 알려준다.

사용:
    python _tools/add_hreflang.py            # 저장소 내 모든 */index.html 처리
    python _tools/add_hreflang.py <slug> ... # 특정 폴더만
"""
import io, sys, re, glob, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

START = "<!-- hreflang:auto (add_hreflang.py) -->"
END = "<!-- /hreflang:auto -->"
BLOCK_RE = re.compile(re.escape(START) + r".*?" + re.escape(END) + r"\n?", re.S)
CANON_RE = re.compile(r'<link\s+rel="canonical"\s+href="([^"]+)"\s*/?>', re.I)


def build_block(base):
    base = base.rstrip()
    # canonical에 이미 쿼리가 붙어있으면 경로만 사용
    base = base.split("?")[0]
    lines = [
        START,
        f'<link rel="alternate" hreflang="ko" href="{base}?lang=ko">',
        f'<link rel="alternate" hreflang="en" href="{base}?lang=en">',
        f'<link rel="alternate" hreflang="x-default" href="{base}">',
        END,
    ]
    return "\n".join(lines)


def process(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    m = CANON_RE.search(html)
    if not m:
        return path, "SKIP (canonical 없음)"
    base = m.group(1)
    block = build_block(base)

    if START in html:
        new = BLOCK_RE.sub(block + "\n", html, count=1)
        action = "UPDATED"
    else:
        canon_line = m.group(0)
        new = html.replace(canon_line, canon_line + "\n" + block, 1)
        action = "INSERTED"

    if new == html:
        return path, "NOCHANGE"
    with open(path, "w", encoding="utf-8") as f:
        f.write(new)
    return path, f"{action} -> {base}"


def main():
    args = sys.argv[1:]
    if args:
        targets = [os.path.join(ROOT, a, "index.html") for a in args]
    else:
        targets = sorted(glob.glob(os.path.join(ROOT, "*", "index.html")))
    for p in targets:
        if not os.path.isfile(p):
            print(f"{os.path.relpath(p, ROOT):55s} MISSING")
            continue
        _, status = process(p)
        print(f"{os.path.relpath(p, ROOT):55s} {status}")


if __name__ == "__main__":
    main()
