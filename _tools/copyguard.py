# -*- coding: utf-8 -*-
"""본문 복사 억제(copy-guard)를 전체 페이지에 주입한다.

⚠️ 한계를 먼저 알 것 — 이건 '차단'이 아니라 '억제'다.
  · 소스 보기(Ctrl+U)·JS 끄기·리더모드·curl·devtools 로 전부 우회된다.
  · 리포지토리가 public 이므로 github.com/Henryshin/research 에서 원문 그대로 읽힌다.
  · 스크린샷/화면녹화는 웹 기술로 막을 방법이 아예 없다(OS 레벨 동작).
  따라서 목적은 "우연히 드래그해서 긁어가는 것" 정도를 줄이는 데 있다.

SEO·접근성은 유지된다: 텍스트가 DOM 에 그대로 남으므로 구글 색인과
스크린리더는 영향을 받지 않는다. (캔버스 렌더링·JS 난독화 같은 방식은
색인을 통째로 죽이므로 절대 쓰지 말 것.)

사용
  python _tools/copyguard.py            # dry-run
  python _tools/copyguard.py --apply
  python _tools/copyguard.py --remove --apply   # 되돌리기
"""
import re
import sys
import io
import glob
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CSS_MARK = '/* copy-guard */'
JS_MARK = '<!-- copy-guard -->'

CSS_BLOCK = """
  /* copy-guard */
  .container, .nav-inner { -webkit-user-select:none; -moz-user-select:none; -ms-user-select:none; user-select:none; }
  .container img, .container figure { -webkit-user-drag:none; user-drag:none; }
"""

JS_BLOCK = """<!-- copy-guard -->
<script>
(function () {
  function block(e) { e.preventDefault(); return false; }
  var events = ['copy', 'cut', 'contextmenu', 'dragstart', 'selectstart'];
  for (var i = 0; i < events.length; i++) document.addEventListener(events[i], block);
})();
</script>
"""

STYLE_END_RE = re.compile(r'(\n</style>)')
BODY_END_RE = re.compile(r'(\n</body>)')
CSS_STRIP_RE = re.compile(r'\n  /\* copy-guard \*/\n(?:.*\n)*?.*user-drag:none;\s*\}\n')
JS_STRIP_RE = re.compile(r'<!-- copy-guard -->\n<script>\n(?:.*\n)*?</script>\n')


def main():
    apply_ = '--apply' in sys.argv
    remove = '--remove' in sys.argv
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)

    files = sorted(glob.glob('*/index.html')) + ['index.html']
    touched = 0
    for path in files:
        src = open(path, encoding='utf-8').read()
        has = CSS_MARK in src

        if remove:
            if not has:
                print(f'  SKIP (없음)                {path}')
                continue
            out = JS_STRIP_RE.sub('', CSS_STRIP_RE.sub('\n', src))
            print(f'  REMOVE                     {path}')
        else:
            if has:
                print(f'  SKIP (이미 적용)           {path}')
                continue
            if not STYLE_END_RE.search(src) or not BODY_END_RE.search(src):
                print(f'  SKIP (구조 불일치)         {path}')
                continue
            out = STYLE_END_RE.sub(CSS_BLOCK + r'\1', src, count=1)
            out = BODY_END_RE.sub('\n' + JS_BLOCK + r'\1', out, count=1)
            print(f'  ADD                        {path}')

        touched += 1
        if apply_:
            open(path, 'w', encoding='utf-8', newline='').write(out)

    verb = '제거' if remove else '적용'
    if not apply_:
        print(f'\nDRY RUN — {touched}개 파일 {verb} 예정. 실제 반영은 --apply')
    else:
        print(f'\n{touched}개 파일 {verb} 완료.')


if __name__ == '__main__':
    main()
