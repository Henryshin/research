# -*- coding: utf-8 -*-
"""
make_profile.py — 소셜 계정 프로필 이미지(아바타/헤더) 생성.

X·Bluesky 계정을 새로 파면서 필요한 것들. 사이트·OG카드와 같은
올리브 팔레트 + Pretendard 를 써서 어디서 마주쳐도 같은 브랜드로 읽히게 한다.

규격(2026-07 기준):
  avatar        400x400   (X·Bluesky 공통. 원형으로 잘리므로 안전영역 중앙)
  x-header     1500x500   (X 프로필 배너. 좌하단은 아바타가 겹침)
  bsky-banner  3000x1000  (Bluesky 배너. X와 같은 3:1이라 디자인 공유)

사용:
    python _tools/make_profile.py            # 전체, 있으면 스킵
    python _tools/make_profile.py --force
산출: _brand/avatar.png, _brand/x-header.png, _brand/bsky-banner.png
"""
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _card import PALETTE, Renderer, assert_not_blank, head, save_png  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.join(ROOT, "_brand")

P = PALETTE
TAGLINE = "Korea's semiconductor &amp; robotics supply chain, in English"


def avatar_html(size=400):
    return f"""<!doctype html><html><head>{head(f'''
  body{{width:{size}px;height:{size}px;display:flex;align-items:center;
    justify-content:center;background:{P['brand']};}}
  .m{{font-weight:900;font-size:{int(size*0.42)}px;color:#f7f7f2;
    letter-spacing:-.03em;line-height:1;}}
  .r{{position:absolute;bottom:{int(size*0.17)}px;
    width:{int(size*0.20)}px;height:{int(size*0.035)}px;border-radius:99px;
    background:{P['accent_hero']};}}
''')}</head><body><div class="m">HS</div><div class="r"></div></body></html>"""


def banner_html(w, h):
    """3:1 배너. X는 좌하단에 아바타가 겹치므로 문구를 오른쪽으로 민다."""
    s = w / 1500.0  # 1500px 기준으로 잡고 배수 적용
    return f"""<!doctype html><html><head>{head(f'''
  body{{width:{w}px;height:{h}px;position:relative;overflow:hidden;
    background:{P['bg']};}}
  .bgfx{{position:absolute;inset:0;opacity:.06;
    background:repeating-linear-gradient(135deg,{P['accent_hero']} 0 {2*s}px,
      transparent {2*s}px {30*s}px);}}
  .wrap{{position:relative;height:100%;
    padding:{60*s}px {80*s}px {60*s}px {330*s}px;
    display:flex;flex-direction:column;justify-content:center;
    gap:{18*s}px;}}
  .eyebrow{{display:flex;align-items:center;gap:{12*s}px;
    font-size:{20*s}px;font-weight:800;letter-spacing:.14em;
    color:{P['brand2']};text-transform:uppercase;}}
  .eyebrow::before{{content:"";width:{4*s}px;height:{21*s}px;
    border-radius:{2*s}px;background:{P['brand']};display:block;}}
  .t{{font-size:{46*s}px;font-weight:900;color:{P['ink']};
    letter-spacing:-.02em;line-height:1.14;max-width:{1020*s}px;}}
  .d{{font-size:{22*s}px;font-weight:600;color:{P['ink_faint']};}}
''')}</head><body>
<div class="bgfx"></div>
<div class="wrap">
  <div class="eyebrow">Henry Shin Research</div>
  <div class="t">{TAGLINE}</div>
  <div class="d">henryshin.github.io/research</div>
</div></body></html>"""


JOBS = [
    ("avatar.png", lambda: avatar_html(400), 400, 400),
    ("x-header.png", lambda: banner_html(1500, 500), 1500, 500),
    ("bsky-banner.png", lambda: banner_html(3000, 1000), 3000, 1000),
]


def main():
    force = "--force" in sys.argv
    todo = []
    for name, fn, w, h in JOBS:
        out = os.path.join(BRAND, name)
        if os.path.exists(out) and not force:
            print(f"{name:18s} SKIP (존재 — --force 로 재생성)")
            continue
        todo.append((name, fn, w, h, out))

    if not todo:
        print("\n생성할 것 없음.")
        return

    # 3000px 배너는 device_scale_factor=2 면 6000px 이라 과하다. 배너만 1배.
    with Renderer(scale=2) as r:
        for name, fn, w, h, out in todo:
            img = r.shot(fn(), w, h, scale=1 if w >= 3000 else None)
            assert_not_blank(img)
            size, used = save_png(img, out, max_bytes=1_500_000)
            print(f"{name:18s} OK  {w}x{h}  {size/1024:6.1f}KB  ({used}색)")


if __name__ == "__main__":
    main()
