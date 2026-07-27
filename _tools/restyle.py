# -*- coding: utf-8 -*-
"""사이트 전체 타이포 스케일 일괄 조정 + 주석(.filter-note) 평문화.

플레이북 `## 1. 확정 기본값`의 "타이포그래피 / 주석 스타일 / 디자인 변경 범위"
항목을 강제하는 도구. CSS는 리포트 전체가 공용이므로 한 곳만 바꾸지 말고
이 스크립트로 7개 리포트 + 허브를 한 번에 갱신한다.

동작
  1. 각 index.html 의 <style>...</style> 블록 안에서만 `font-size:Npx` 를 ±STEP
  2. `.filter-note` 규칙을 박스(배경·보더·패딩)에서 평문 주석으로 치환
  3. 블록 끝에 마커를 남겨 재실행해도 중복 적용되지 않음(idempotent)

사용
  python _tools/restyle.py              # dry-run (아무것도 쓰지 않음)
  python _tools/restyle.py --apply      # 실제 기록
  python _tools/restyle.py --step 1 --apply
"""
import re
import sys
import io
import glob
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MARKER_RE = re.compile(r'/\* type-scale:[^*]*\*/')
STYLE_RE = re.compile(r'(<style>)(.*?)(</style>)', re.S)
FS_RE = re.compile(r'(font-size:)(\d+(?:\.\d+)?)(px)')
# `.filter-note { ... }` 본 규칙만. `.filter-note b { ... }` 는 건드리지 않는다.
FN_RE = re.compile(r'^(\s*)\.filter-note\s*\{[^}]*\}', re.M)

FLAT_NOTE = ('{indent}.filter-note {{ color:var(--ink-faint); font-size:{size}px; '
             'margin:8px 0 4px; line-height:1.62; }}')


def parse_args(argv):
    apply_ = '--apply' in argv
    step = 2.0
    if '--step' in argv:
        step = float(argv[argv.index('--step') + 1])
    return apply_, step


def restyle(css, step):
    """<style> 블록 문자열을 받아 (수정본, 변경 통계) 반환."""
    bumps = []

    def bump(mo):
        old = float(mo.group(2))
        new = round(old + step, 2)
        new_s = str(int(new)) if new == int(new) else str(new)
        bumps.append((mo.group(2), new_s))
        return f'{mo.group(1)}{new_s}{mo.group(3)}'

    css = FS_RE.sub(bump, css)

    flattened = []

    def flatten(mo):
        rule = mo.group(0)
        fs = re.search(r'font-size:(\d+(?:\.\d+)?)px', rule)
        flattened.append(rule.strip()[:40])
        return FLAT_NOTE.format(indent=mo.group(1), size=fs.group(1) if fs else '13.3')

    css = FN_RE.sub(flatten, css)
    return css, len(bumps), len(flattened)


def main():
    apply_, step = parse_args(sys.argv)
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)
    marker = f'/* type-scale:{step:+g}px, flat-notes */'

    files = sorted(glob.glob('*/index.html')) + ['index.html']
    touched = 0
    for path in files:
        src = open(path, encoding='utf-8').read()
        if MARKER_RE.search(src):
            print(f'  SKIP (마커 있음 — 이미 적용)  {path}')
            continue
        m = STYLE_RE.search(src)
        if not m:
            print(f'  SKIP (<style> 없음)          {path}')
            continue

        css2, n_bump, n_flat = restyle(m.group(2), step)
        out = (src[:m.start()] + m.group(1) + css2 + '\n' + marker + '\n'
               + m.group(3) + src[m.end():])
        print(f'  {path}\n      font-size {step:+g}px x{n_bump}   .filter-note 평문화 x{n_flat}')
        touched += 1
        if apply_:
            open(path, 'w', encoding='utf-8', newline='').write(out)

    if not apply_:
        print(f'\nDRY RUN — {touched}개 파일이 바뀔 예정. 실제 적용은 --apply')
    else:
        print(f'\n{touched}개 파일 기록 완료.')
        print('배포 전 확인: 전체 리포트 CSS md5가 같은지 대조할 것')


if __name__ == '__main__':
    main()
