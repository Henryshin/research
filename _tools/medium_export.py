# -*- coding: utf-8 -*-
"""
medium_export.py — 배포된 index.html의 영어(lang-en) 본문을 Medium 붙여넣기용
clean Markdown으로 추출한다.

왜 붙여넣기(paste)인가:
- 페이지는 KO/EN 두 언어가 한 DOM에 있어 Medium의 URL Import가 두 언어를
  섞어서 가져온다(엉킴). 그래서 EN 본문만 뽑아 깨끗한 Markdown으로 만든다.
- 차트/GIF는 Medium에서 렌더 안 되므로 [SCREENSHOT] 마커로 대체 → 캡처 삽입 안내.

출력: research/_medium/<slug>.md
  맨 위에 발행 체크리스트(제목·태그·canonical·차트 캡처) 헤더 포함.

사용:
    python _tools/medium_export.py <slug>
    python _tools/medium_export.py            # index.html 있는 모든 리포트
"""
import io, os, re, sys, glob
from html.parser import HTMLParser
from html import unescape

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://henryshin.github.io/research"

ARTICLE_RE = re.compile(r'<article id="lang-en".*?</article>', re.S)
CANON_RE = re.compile(r'<link\s+rel="canonical"\s+href="([^"]+)"', re.I)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
KEYWORDS_RE = re.compile(r'<meta\s+name="keywords"\s+content="([^"]*)"', re.I)
HERO_H1_RE = re.compile(r"<h1>(.*?)</h1>", re.S)
EYEBROW_RE = re.compile(r'<div class="eyebrow">(.*?)</div>', re.S)
# 면책조항은 <article> 밖의 공유 섹션(.disclaimer > .ct-en)에 있어 별도로 뽑는다
DISCLAIMER_EN_RE = re.compile(
    r'<div class="disclaimer">.*?<div class="ct-en"[^>]*>(.*?)</div>\s*</div>', re.S
)
TAG_STRIP_RE = re.compile(r"<[^>]+>")


class MdParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []          # 완성된 블록들
        self.buf = []          # 현재 인라인 텍스트
        self.tag_stack = []
        self.class_stack = []
        self.skip_depth = 0    # 차트 등 통째 건너뛸 영역 깊이
        # 표 상태
        self.in_table = False
        self.rows = []
        self.cur_row = None
        self.cur_cell = None
        self.cell_is_header = False
        self.header_seen = False
        # 리스트
        self.list_stack = []
        # KPI 카드 / meta 캡처
        self.kpi = None        # dict(label/value/sub) 수집 중
        self.cap_key = None    # 현재 캡처 중인 필드
        self.meta = None       # meta span 텍스트 리스트
        self.in_fig_cap = False  # figure 캡션(div.cap) 내부 여부 — 캡션끼리 뭉치는 것 방지

    # ---- helpers ----
    def _cls(self, attrs):
        for k, v in attrs:
            if k == "class":
                return v.split()
        return []

    def flush_para(self, prefix=""):
        text = "".join(self.buf).strip()
        text = re.sub(r"[ \t]+", " ", text)
        self.buf = []
        if text:
            self.out.append(prefix + text)

    # ---- tag handling ----
    def handle_starttag(self, tag, attrs):
        cls = self._cls(attrs)
        self.tag_stack.append(tag)
        self.class_stack.append(cls)

        if self.skip_depth:
            self.skip_depth += 1
            return

        # 차트/가격 섹션·언어토글·nav·히어로타이틀 등은 통째 스킵
        # (제목·부제는 Medium 자체 Title/Subtitle란에 직접 입력하도록 안내문으로 분리 —
        #  본문에 "# 제목"을 그대로 넣으면 Medium이 페이지 제목으로도 쓰면서 본문에도
        #  남겨 두어 제목이 중복 표시된다.)
        if ("price-chart" in " ".join(cls)) or ("chart-" in " ".join(cls)) \
           or "lang-toggle" in cls or tag == "nav" or "topbar" in cls \
           or "eyebrow" in cls or tag == "h1":
            self.skip_depth = 1
            return

        # KPI 카드: label/value/sub 개별 캡처
        if tag == "div" and "kpi-card" in cls:
            self.flush_para()
            self.kpi = {"label": "", "value": "", "sub": ""}
            return
        if self.kpi is not None and tag == "div":
            for key in ("label", "value", "sub"):
                if key in cls:
                    self.cap_key = key
                    return
        # meta(발행일 등) span 묶음
        if tag == "div" and "meta" in cls:
            self.flush_para()
            self.meta = []
            return
        # 소제목(sub-h) 이탤릭 처리 대상 표시
        if tag == "div" and "sub-h" in cls:
            self.flush_para()

        # figure 캡션(div.cap): 3-up 그림 캡션이 연달아 있으면 사이 flush 없이는
        # 한 덩어리로 뭉쳐 렌더링이 깨진다 → 캡션마다 독립 문단으로 분리.
        if tag == "div" and "cap" in cls:
            self.flush_para()
            self.in_fig_cap = True
            return
        if self.in_fig_cap and tag == "span" and not cls:
            self.buf.append(": ")  # 볼드 라벨과 설명 사이 구분자
        if tag == "div" and "rfig-credit" in cls:
            self.flush_para()

        if tag in ("h1", "h2", "h3", "h4"):
            self.flush_para()
        elif tag == "p":
            self.flush_para()
        elif tag in ("ul", "ol"):
            self.flush_para()
            self.list_stack.append("-" if tag == "ul" else "1.")
        elif tag == "li":
            self.flush_para()
        elif tag == "table":
            self.flush_para()
            self.in_table = True
            self.rows = []
            self.header_seen = False
        elif tag == "tr" and self.in_table:
            self.cur_row = []
        elif tag in ("th", "td") and self.in_table:
            self.cur_cell = []
            self.cell_is_header = (tag == "th")
        elif tag in ("strong", "b"):
            self.buf.append("**")
        elif tag in ("em", "i"):
            self.buf.append("*")
        elif tag == "br":
            self.buf.append(" ")
        elif tag == "img":
            alt = ""
            for k, v in attrs:
                if k == "alt":
                    alt = v
            self.out.append(f"> **[SCREENSHOT 삽입: {alt or 'image'}]**")
        elif tag == "figcaption":
            self.flush_para()

    def handle_endtag(self, tag):
        if self.tag_stack:
            self.tag_stack.pop()
        cls = self.class_stack.pop() if self.class_stack else []

        if self.skip_depth:
            self.skip_depth -= 1
            return

        # KPI 카드 마감 → 한 줄 bullet
        if tag == "div" and "kpi-card" in cls and self.kpi is not None:
            k = self.kpi
            self.kpi = None
            self.cap_key = None
            label = re.sub(r"\s+", " ", k["label"]).strip()
            value = re.sub(r"\s+", " ", k["value"]).strip()
            sub = re.sub(r"\s+", " ", k["sub"]).strip()
            line = f"- **{label}:** {value}"
            if sub:
                line += f" ({sub})"
            self.out.append(line)
            return
        if self.kpi is not None and tag == "div" and self.cap_key:
            self.cap_key = None
            return
        # meta 마감 → " · " 로 결합한 이탤릭 라인
        if tag == "div" and "meta" in cls and self.meta is not None:
            parts = [re.sub(r"\s+", " ", p).strip() for p in self.meta if p.strip()]
            self.meta = None
            if parts:
                self.out.append("_" + " · ".join(parts) + "_")
            return
        # sub-h 마감 → 이탤릭 소제목
        if tag == "div" and "sub-h" in cls:
            self.flush_para("_")
            return
        # figure 캡션(div.cap) 마감 → 독립 문단으로 flush, 다음 캡션과 안 섞이게
        if tag == "div" and "cap" in cls:
            self.in_fig_cap = False
            self.flush_para("- ")
            return
        if tag == "div" and "rfig-credit" in cls:
            self.flush_para("_")
            return

        if tag == "h1":
            self.flush_para("# ")
        elif tag == "h2":
            self.flush_para("## ")
        elif tag == "h3":
            self.flush_para("### ")
        elif tag == "h4":
            self.flush_para("#### ")
        elif tag == "p":
            self.flush_para()
        elif tag == "li":
            marker = self.list_stack[-1] if self.list_stack else "-"
            self.flush_para(marker + " ")
        elif tag in ("ul", "ol"):
            if self.list_stack:
                self.list_stack.pop()
        elif tag in ("th", "td") and self.in_table:
            text = re.sub(r"\s+", " ", "".join(self.cur_cell or []).strip())
            if self.cur_row is not None:
                self.cur_row.append(text)
            self.cur_cell = None
        elif tag == "tr" and self.in_table:
            if self.cur_row:
                self.rows.append((self.cell_is_header_row(), self.cur_row))
            self.cur_row = None
        elif tag == "table":
            self.emit_table()
            self.in_table = False
        elif tag in ("strong", "b"):
            self.buf.append("**")
        elif tag in ("em", "i"):
            self.buf.append("*")
        elif tag == "figcaption":
            self.flush_para("_")  # 캡션은 이탤릭 라인

    def cell_is_header_row(self):
        # 행에 th가 있었는지: 마지막 셀 판정으로 근사 → thead 여부는 rows에서 첫 행 처리
        return self.cell_is_header

    def handle_data(self, data):
        if self.skip_depth:
            return
        cur_cls = self.class_stack[-1] if self.class_stack else []
        cur_tag = self.tag_stack[-1] if self.tag_stack else ""
        # 숫자 라벨 스팬(num/no)은 뒤에, 단위 스팬(unit)은 앞에 공백 부여.
        # ⚠ "num"은 표의 우측정렬 숫자열(<td class="num">)에도 재사용되는 클래스라
        #    반드시 태그가 span일 때만(=섹션 번호 스팬) 적용한다.
        if cur_tag == "span" and "unit" in cur_cls:
            data = " " + data
        elif cur_tag == "span" and "num" in cur_cls and data.strip():
            data = data + ". "  # h2 섹션 번호: "1" -> "1. " (하위 헤딩 "1.1." 스타일과 통일)
        elif cur_tag == "span" and "no" in cur_cls and data.strip():
            data = data + " "   # h3/h4 번호는 이미 "1.1." 처럼 마침표 포함

        if self.kpi is not None and self.cap_key:
            self.kpi[self.cap_key] += data
        elif self.meta is not None:
            if data.strip():
                self.meta.append(data)
        elif self.in_table and self.cur_cell is not None:
            self.cur_cell.append(data)
        elif self.in_table:
            return
        else:
            self.buf.append(data)

    def emit_table(self):
        if not self.rows:
            return
        # 첫 행을 헤더로 사용
        header = self.rows[0][1]
        body = [r for _, r in self.rows[1:]]
        ncol = len(header)
        def fmt(row):
            row = (row + [""] * ncol)[:ncol]
            return "| " + " | ".join(row) + " |"
        lines = [fmt(header), "| " + " | ".join(["---"] * ncol) + " |"]
        lines += [fmt(r) for r in body]
        self.out.append("\n".join(lines))
        self.rows = []

    def result(self):
        self.flush_para()
        # 빈 줄로 블록 구분, 캡션 이탤릭 닫기 처리
        blocks = []
        for b in self.out:
            if b.startswith("_") and not b.endswith("_"):
                b = b + "_"
            blocks.append(b)
        blocks = _merge_list_blocks(blocks)
        md = "\n\n".join(blocks)
        md = re.sub(r"\n{3,}", "\n\n", md)
        return md.strip()


_LIST_ITEM_RE = re.compile(r"^(?:[-*]|\d+\.)\s")


def _merge_list_blocks(blocks):
    """연속된 리스트 항목 블록들을 빈 줄 없이 하나로 합친다.

    KPI 카드나 <li> 하나마다 self.out에 별도 블록으로 쌓이는데, result()가
    블록 사이를 "\\n\\n"으로 잇다 보니 Markdown 리스트가 항목마다 빈 줄로
    끊긴 "loose list"가 된다. Medium 붙여넣기 파서는 이걸 항목 사이에
    빈 불릿(empty bullet)으로 오인식하므로, 연속 리스트 항목은 "\\n" 하나로
    묶어 하나의 tight list 블록으로 만든다.
    """
    merged = []
    run = []
    for b in blocks:
        if _LIST_ITEM_RE.match(b):
            run.append(b)
        else:
            if run:
                merged.append("\n".join(run))
                run = []
            merged.append(b)
    if run:
        merged.append("\n".join(run))
    return merged


def _plain(html_fragment):
    return unescape(TAG_STRIP_RE.sub("", html_fragment)).strip()


def export(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    slug = os.path.basename(os.path.dirname(path))

    m = ARTICLE_RE.search(html)
    if not m:
        return slug, "SKIP (lang-en article 없음)"
    article = m.group(0)

    canon = CANON_RE.search(html)
    canon_url = canon.group(1) if canon else f"{BASE_URL}/{slug}/"
    title_m = HERO_H1_RE.search(article)
    hero_title = _plain(title_m.group(1)) if title_m else (
        unescape(TITLE_RE.search(html).group(1).strip()) if TITLE_RE.search(html) else slug
    )
    eyebrow_m = EYEBROW_RE.search(article)
    subtitle = _plain(eyebrow_m.group(1)) if eyebrow_m else ""
    kw_m = KEYWORDS_RE.search(html)
    tags = []
    if kw_m:
        raw = [t.strip() for t in kw_m.group(1).split(",")]
        # 영문/숫자 위주 태그 5개 추천
        tags = [t for t in raw if re.search(r"[A-Za-z]", t)][:5]

    p = MdParser()
    p.feed(article)
    body = p.result()

    # 면책조항: <article> 밖 공유 섹션(.disclaimer > .ct-en)이라 별도로 뽑아 본문 끝에 붙인다
    dm = DISCLAIMER_EN_RE.search(html)
    if dm:
        dp = MdParser()
        dp.feed(dm.group(1))
        disclaimer_md = dp.result()
        disclaimer_md = re.sub(r"^###\s+", "## ", disclaimer_md, count=1)  # 섹션급 헤딩으로
        body = body + "\n\n" + disclaimer_md

    header = f"""<!--
=========================================================
 MEDIUM 발행용 초안 — 붙여넣기(paste) 방식
 소스: {canon_url}?lang=en
=========================================================
 ⚠ 디자인 한계 (미리 알아둘 것):
   Medium 에디터는 커스텀 CSS/폰트/색을 지원하지 않는다. Pretendard 폰트,
   올리브 팔레트, KPI 카드 레이아웃은 Medium에 옮길 방법이 없다(플랫폼 자체
   제약). 살아남는 건 텍스트·굵게/기울임·표·이미지뿐. 원본 디자인을 그대로
   보여주고 싶은 부분(KPI 4개 수치, 감속기 3종 그림, 가격차트)은 아래처럼
   "스크린샷 이미지"로 박아넣는 게 유일한 방법이다.

 발행 절차:
 1) Medium → Write a story (새 글)
 2) 제목란에 직접 타이핑: "{hero_title}"
    부제(subtitle)란: 클릭을 유도하는 한 줄을 직접 작성할 것.
      "{subtitle}"(원문 eyebrow 문구)는 그대로 쓰지 말 것 — 사이트에선 카테고리
      라벨이라 괜찮지만, Medium 부제는 피드/검색 미리보기에 노출돼 클릭률에
      영향을 주므로 투자 포인트를 압축한 문장이 낫다.
      예) 밸류에이션 훅: "Trading at 114x trailing P/E — is the humanoid-robot
      bet already priced in?" / 희소성 훅: "Korea's only maker mass-producing
      the full robot-reducer lineup." 실제 데이터는 본문 참고해 종목 특성에 맞게 작성.
    (본문에 '# 제목'을 그대로 붙여넣으면 Medium이 제목을 자동 추출하면서
     본문에도 남겨 제목이 두 번 보인다 — 그래서 제목은 이 파일에 넣지 않았음)
 3) 아래 '_Original Feb 2026 ...' 로 시작하는 줄(발행일·기준가 캡션, 본문 첫 줄로는 유지)
    부터 끝까지 복사해 붙여넣기
 4) [SCREENSHOT 삽입: ...] 마커 위치에 배포페이지 차트/그림 캡처를 넣기
    (캡처: 배포 URL 열고 해당 영역 스크린샷)
 5) 표가 깨지면 → 해당 표를 이미지로 캡처해 대체(Medium 표 지원 빈약)
 6) 발행 전 하단에 원문 링크 추가:
      "Originally published (with interactive chart & Korean version) at {canon_url}"
 7) 태그(최대 5): {', '.join(tags) if tags else '(수동 지정)'}
 --- canonical(원문 SEO 보호) ---
 * 가장 확실한 방법은 이 글을 '붙여넣기' 대신 medium.com/p/import 로
   {canon_url}en/  (영어 전용 URL) 를 임포트하는 것. 그러면 canonical 자동 연결.
   (영어 전용 URL은 build_en_mirror 단계 도입 시 생성 — 미도입이면 붙여넣기 사용)
 * 붙여넣기 시 Medium이 canonical을 가져감 → 해외 도달은 늘지만 원문 SEO는 분산.
=========================================================
-->

"""
    out_dir = os.path.join(ROOT, "_medium")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{slug}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header + body + "\n")
    return slug, f"OK -> _medium/{slug}.md ({len(body)} chars)"


def main():
    args = sys.argv[1:]
    if args:
        targets = [os.path.join(ROOT, a, "index.html") for a in args]
    else:
        targets = sorted(glob.glob(os.path.join(ROOT, "*", "index.html")))
    for p in targets:
        if not os.path.isfile(p):
            print(f"{p}: MISSING")
            continue
        slug, status = export(p)
        print(f"{slug:50s} {status}")


if __name__ == "__main__":
    main()
