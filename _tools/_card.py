# -*- coding: utf-8 -*-
"""
_card.py — 소셜 카드 이미지 렌더링 공용 코어. (CLI 아님, import 전용)

make_og.py / make_social_cards.py 가 공유하는 것:
- Playwright chromium 부트스트랩 (브라우저 1회 기동 → 여러 장 렌더)
- Pretendard 웹폰트 로드 보장 (조용한 시스템폰트 폴백 방지)
- PIL 팔레트 양자화로 용량 예산 맞추기
- 사이트와 동일한 올리브/세이지 팔레트 토큰

왜 Playwright인가: cairosvg/matplotlib이 없고, 무엇보다 사이트 본문과
'같은 CSS·같은 폰트'로 그려야 카드와 페이지가 따로 놀지 않는다.
"""
import io
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PRETENDARD_CSS = ("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9"
                  "/dist/web/static/pretendard.css")

# 플레이북 §4 팔레트(라이트)와 동일. 카드는 항상 라이트 한 벌만 쓴다.
PALETTE = {
    "bg": "#f7f7f2", "card": "#fffefb", "ink": "#16180f", "ink_soft": "#3f4433",
    "ink_faint": "#7d8271", "line": "#ecede3", "line2": "#d9dbc9",
    "brand": "#3f4d1e", "brand2": "#55652c", "accent_hero": "#a9b491",
    "neg": "#c05b41",
}

FONT_STACK = ("'Pretendard',-apple-system,BlinkMacSystemFont,\"Segoe UI\","
              "Roboto,'Malgun Gothic',sans-serif")

# 실제로 카드에서 쓰는 웨이트만 명시 로드한다.
_WEIGHTS = ("400", "500", "600", "800", "900")


def head(extra_css=""):
    """카드 HTML의 공통 <head> 조각."""
    return f"""<meta charset="utf-8">
<link rel="stylesheet" href="{PRETENDARD_CSS}">
<style>
  *{{margin:0;padding:0;box-sizing:border-box;}}
  html,body{{background:{PALETTE['bg']};font-family:{FONT_STACK};
    -webkit-font-smoothing:antialiased;text-rendering:geometricPrecision;}}
  {extra_css}
</style>"""


class Renderer:
    """with Renderer() as r: r.shot(html, 1200, 630)

    브라우저를 한 번만 띄운다. Pretendard static CSS는 웨이트별 woff2를
    각각 받아 첫 로드가 수 초 걸리므로, slug마다 새로 띄우면 그만큼 반복된다.
    """

    def __init__(self, scale=2, allow_fallback=False):
        self.scale = scale
        self.allow_fallback = allow_fallback
        self._pw = None
        self._browser = None

    def __enter__(self):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch()
        return self

    def __exit__(self, *exc):
        if self._browser:
            self._browser.close()
        if self._pw:
            self._pw.stop()
        return False

    def shot(self, html, w, h, wait_ms=0, scale=None):
        # scale 은 샷마다 덮어쓸 수 있다. 3000px 배너를 2배로 그리면 6000px 이라
        # 과하다. (sync_playwright 를 중첩 기동하면 asyncio 충돌이 나므로
        # Renderer 를 두 개 띄우는 방식은 쓸 수 없다.)
        scale = self.scale if scale is None else scale
        ctx = self._browser.new_context(
            viewport={"width": w, "height": h},
            device_scale_factor=scale,
            # 사이트 CSS에 prefers-color-scheme:dark 가 있다. 카드는 라이트 고정.
            color_scheme="light",
        )
        page = ctx.new_page()
        page.set_content(html, wait_until="networkidle")

        # 함정: document.fonts.ready 만으로는 부족하다. 해당 웨이트로 아직
        # 아무 텍스트도 레이아웃되지 않았으면 브라우저가 그 웨이트를 요청조차
        # 하지 않은 채로 ready 가 즉시 resolve 된다. 명시적으로 load 시킨다.
        page.evaluate(
            """async (weights) => {
                 await Promise.all(weights.map(
                   w => document.fonts.load(w + ' 64px Pretendard')));
                 await document.fonts.ready;
               }""",
            list(_WEIGHTS),
        )
        ok = page.evaluate("document.fonts.check('900 64px Pretendard')")
        if not ok and not self.allow_fallback:
            ctx.close()
            raise RuntimeError(
                "Pretendard 웹폰트 로드 실패 (CDN 확인). "
                "시스템 폰트로라도 뽑으려면 --allow-fallback")

        if wait_ms:
            page.wait_for_timeout(wait_ms)

        buf = page.screenshot(clip={"x": 0, "y": 0, "width": w, "height": h})
        ctx.close()

        img = Image.open(io.BytesIO(buf)).convert("RGB")
        if scale != 1:
            # 2배로 그린 뒤 축소 = 텍스트 가장자리 품질이 눈에 띄게 좋아진다.
            img = img.resize((w, h), Image.LANCZOS)
        return img


def save_png(img, path, max_bytes=300_000):
    """예산 안에서 가장 색 수가 많은(=화질 좋은) 팔레트를 고른다.

    반환: (바이트수, 사용한 색 수)
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    best = None
    for colors in (32, 64, 128, 256):
        q = img.quantize(colors=colors, method=Image.MEDIANCUT,
                         dither=Image.FLOYDSTEINBERG)
        buf = io.BytesIO()
        q.save(buf, "PNG", optimize=True)
        if buf.tell() <= max_bytes:
            best = (buf.getvalue(), colors)  # 더 큰 팔레트가 되면 계속 갱신
    if best is None:
        buf = io.BytesIO()
        img.save(buf, "PNG", optimize=True)
        best = (buf.getvalue(), "truecolor(예산초과)")
    with open(path, "wb") as f:
        f.write(best[0])
    return len(best[0]), best[1]


def assert_not_blank(img, min_colors=8):
    """Playwright 는 조용히 백지를 뱉을 때가 있다. 색 수로 잡아낸다."""
    cols = img.getcolors(1_000_000)
    n = len(cols) if cols else 1_000_000
    if n < min_colors:
        raise RuntimeError(f"렌더 결과가 사실상 백지다 (색 {n}종). 템플릿/폰트 확인 필요.")
    return n
