# -*- coding: utf-8 -*-
"""
make_og.py — 리포트별 소셜 공유 카드(OG 이미지) 1200x630 PNG 생성.

배경: 전 페이지에 twitter:card=summary_large_image 가 선언돼 있는데 정작
og:image 가 0건이었다. 그 상태로 X/레딧/슬랙/카톡에 링크를 뿌리면 큰 카드가
뜨지 않는다. 플레이북이 copy-guard 를 철회하며 "확산이 보호보다 우선"이라고
확정한 것과 정면으로 어긋나는 구멍이라 메운다.

문구는 새로 쓰지 않는다. 각 리포트 <head> 와 영문 본문에서 뽑아 쓴다:
  회사명 = lang-en <h1> 의 괄호 앞
  티커   = lang-en .eyebrow 의 '·' 뒤   (예: KOSDAQ 064760)
  훅     = twitter:description 의 첫 문장 (110자 컷)

사용:
    python _tools/make_og.py                 # 전체(리포트 + 허브), 있으면 스킵
    python _tools/make_og.py tck-064760-sic-ring
    python _tools/make_og.py --force         # 재생성
    python _tools/make_og.py hub             # 허브 카드만
산출:
    <slug>/assets/og.png , assets/og.png (허브)
"""
import glob
import io
import os
import re
import sys
from html import escape, unescape

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _card import PALETTE, Renderer, assert_not_blank, head, save_png  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 630

EYEBROW_RE = re.compile(r'<article id="lang-en".*?<div class="eyebrow">(.*?)</div>', re.S)
H1_EN_RE = re.compile(r'<article id="lang-en".*?<h1>(.*?)</h1>', re.S)
TWDESC_RE = re.compile(r'<meta\s+name="twitter:description"\s+content="([^"]*)"', re.I)
OGDESC_RE = re.compile(r'<meta\s+property="og:description"\s+content="([^"]*)"', re.I)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
CARD_RE = re.compile(r'<a class="card"[^>]*href="\./([^"/]+)/"', re.S)


def plain(s):
    """태그 제거 + 엔티티 복원 + NBSP/유니코드 마이너스 정규화."""
    s = re.sub(r"<[^>]+>", " ", s)
    s = unescape(s).replace(" ", " ").replace("−", "-")
    return re.sub(r"\s+", " ", s).strip()


def first_sentence(text, limit=110):
    part = re.split(r"(?<=[.!?])\s|\s—\s|:\s", text)[0]
    return part[:limit].rstrip(" ,;·-")


def parse_report(html):
    eb = plain(EYEBROW_RE.search(html).group(1)) if EYEBROW_RE.search(html) else ""
    category, _, ticker = eb.partition("·")
    h1 = plain(H1_EN_RE.search(html).group(1)) if H1_EN_RE.search(html) else ""
    m = re.match(r"^(.+?)\s*\(", h1)
    company = (m.group(1) if m else h1).strip()

    dm = TWDESC_RE.search(html) or OGDESC_RE.search(html)
    hook = first_sentence(plain(dm.group(1))) if dm else ""

    return {
        "category": (category.strip() or "Equity Analysis").upper(),
        "ticker": ticker.strip(),
        "company": company,
        "hook": hook,
    }


def parse_hub(html):
    n = len(CARD_RE.findall(html))
    title = plain(TITLE_RE.search(html).group(1)) if TITLE_RE.search(html) else ""
    company = title.split("—")[0].strip() or "Henry Shin Research"
    dm = OGDESC_RE.search(html)
    hook = first_sentence(plain(dm.group(1)), 120) if dm else ""
    return {
        "category": "INDEPENDENT EQUITY NOTES",
        "ticker": f"{n} REPORTS" if n else "",
        "company": company,
        "hook": hook,
    }


def build_html(d):
    P = PALETTE
    # 회사명 길이로 폰트 크기를 대략 맞추고(--len), line-clamp 으로 최악을 막는다.
    # 파이썬에서 이진탐색으로 줄이는 방식은 Playwright 왕복이 8~10회 늘고
    # 한글 keep-all 과 얽혀 수렴이 불안정해서 쓰지 않는다.
    ln = max(len(d["company"]), 3)
    extra = f"""
  body{{width:{W}px;height:{H}px;position:relative;overflow:hidden;}}
  /* 아주 옅은 대각 스트라이프 — 팔레트 정체성 + 양자화에 안전 */
  .bgfx{{position:absolute;inset:0;opacity:.055;
    background:repeating-linear-gradient(135deg,{P['accent_hero']} 0 2px,
      transparent 2px 26px);}}
  .wrap{{position:relative;height:100%;padding:64px 68px 56px;
    display:flex;flex-direction:column;}}
  .eyebrow{{display:flex;align-items:center;gap:14px;
    font-size:20px;font-weight:800;letter-spacing:.13em;
    color:{P['brand2']};text-transform:uppercase;}}
  .eyebrow::before{{content:"";width:4px;height:22px;border-radius:2px;
    background:{P['brand']};display:block;}}
  .mid{{flex:1;display:flex;flex-direction:column;justify-content:center;
    gap:22px;padding-bottom:8px;}}
  .company{{--len:{ln};
    font-weight:900;color:{P['ink']};letter-spacing:-.022em;line-height:1.05;
    font-size:clamp(46px, calc(1180px / var(--len) * 1.62), 96px);
    display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
    overflow:hidden;word-break:keep-all;}}
  .badge{{align-self:flex-start;background:{P['brand']};color:#fff;
    font-size:23px;font-weight:800;letter-spacing:.05em;
    padding:9px 17px;border-radius:7px;}}
  .hook{{font-size:31px;font-weight:500;color:{P['ink_soft']};line-height:1.38;
    display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
    overflow:hidden;max-width:1000px;}}
  .foot{{border-top:1px solid {P['line2']};padding-top:20px;
    display:flex;justify-content:flex-end;}}
  .domain{{font-size:21px;font-weight:600;color:{P['ink_faint']};
    letter-spacing:.01em;}}
"""
    badge = (f'<div class="badge">{escape(d["ticker"])}</div>'
             if d["ticker"] else "")
    hook = (f'<div class="hook">{escape(d["hook"])}</div>'
            if d["hook"] else "")
    return f"""<!doctype html><html><head>{head(extra)}</head><body>
<div class="bgfx"></div>
<div class="wrap">
  <div class="eyebrow">Henry Shin Research &nbsp;·&nbsp; {escape(d["category"])}</div>
  <div class="mid">
    <div class="company">{escape(d["company"])}</div>
    {badge}
    {hook}
  </div>
  <div class="foot"><div class="domain">henryshin.github.io/research</div></div>
</div></body></html>"""


def targets(args):
    """[(라벨, index.html 경로, og.png 경로)]"""
    hub = (os.path.join(ROOT, "index.html"), os.path.join(ROOT, "assets", "og.png"))
    slugs = [a for a in args if not a.startswith("-")]
    out = []
    if not slugs:
        for p in sorted(glob.glob(os.path.join(ROOT, "*", "index.html"))):
            d = os.path.basename(os.path.dirname(p))
            if d.startswith("_") or d == "about":
                continue
            out.append((d, p, os.path.join(ROOT, d, "assets", "og.png")))
        out.append(("(hub)", *hub))
    else:
        for s in slugs:
            if s == "hub":
                out.append(("(hub)", *hub))
            else:
                out.append((s, os.path.join(ROOT, s, "index.html"),
                            os.path.join(ROOT, s, "assets", "og.png")))
    return out


def main():
    args = sys.argv[1:]
    force = "--force" in args
    fallback = "--allow-fallback" in args
    items = targets(args)

    plan = []
    for label, src, out in items:
        if not os.path.isfile(src):
            print(f"{label:38s} MISSING ({os.path.relpath(src, ROOT)})")
            continue
        if os.path.exists(out) and not force:
            print(f"{label:38s} SKIP (존재 — --force 로 재생성)")
            continue
        html = open(src, encoding="utf-8").read()
        d = parse_hub(html) if label == "(hub)" else parse_report(html)
        if not d["company"]:
            print(f"{label:38s} SKIP (회사명 추출 실패)")
            continue
        plan.append((label, out, d))

    if not plan:
        print("\n생성할 카드 없음.")
        return

    with Renderer(scale=2, allow_fallback=fallback) as r:
        for label, out, d in plan:
            img = r.shot(build_html(d), W, H)
            ncol = assert_not_blank(img)
            size, used = save_png(img, out)
            rel = os.path.relpath(out, ROOT).replace("\\", "/")
            print(f"{label:38s} OK  {rel}  {size/1024:6.1f}KB  "
                  f"({used}색/{ncol}종)  <- {d['company']} / {d['ticker']}")


if __name__ == "__main__":
    main()
